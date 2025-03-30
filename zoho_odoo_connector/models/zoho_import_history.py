from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json

_logger = logging.getLogger(__name__)

class ZohoImportHistory(models.Model):
    _name = 'zoho.import.history'
    _description = 'Zoho Import History'
    _order = 'import_date desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    import_date = fields.Datetime(string='Import Date', default=fields.Datetime.now, required=True)
    import_type = fields.Selection([
        ('customers', 'Customers'),
        ('vendors', 'Vendors'),
        ('chart_of_accounts', 'Chart of Accounts'),
        ('invoices', 'Invoices'),
        ('bills', 'Bills'),
        ('journal_entries', 'Journal Entries'),
        ('items', 'Items'),
        ('taxes', 'Taxes'),
        ('currencies', 'Currencies'),
        ('payment_terms', 'Payment Terms'),
        ('all', 'All Data')
    ], string='Import Type', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('partially_completed', 'Partially Completed')
    ], string='Status', default='draft', required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    total_records = fields.Integer(string='Total Records', default=0)
    processed_records = fields.Integer(string='Processed Records', default=0)
    successful_records = fields.Integer(string='Successful Records', default=0)
    failed_records = fields.Integer(string='Failed Records', default=0)
    skipped_records = fields.Integer(string='Skipped Records', default=0)
    log_ids = fields.One2many('zoho.import.log', 'import_history_id', string='Logs')
    notes = fields.Text(string='Notes')
    
    @api.depends('import_type', 'import_date')
    def _compute_name(self):
        """Compute the name of the import history"""
        for record in self:
            if record.import_date:
                date_str = fields.Datetime.to_string(record.import_date)
                record.name = f"{record.import_type.replace('_', ' ').title()} - {date_str}"
            else:
                record.name = record.import_type.replace('_', ' ').title() if record.import_type else 'New Import'
    
    def action_view_logs(self):
        """View the logs for this import history"""
        self.ensure_one()
        return {
            'name': _('Import Logs'),
            'type': 'ir.actions.act_window',
            'res_model': 'zoho.import.log',
            'view_mode': 'tree,form',
            'domain': [('import_history_id', '=', self.id)],
            'context': {'default_import_history_id': self.id},
        }
    
    def action_retry_failed(self):
        """Retry failed imports"""
        self.ensure_one()
        if self.status != 'failed' and self.status != 'partially_completed':
            raise UserError(_('Only failed or partially completed imports can be retried.'))
        
        # Create a new import history record for the retry
        new_history = self.copy({
            'import_date': fields.Datetime.now(),
            'status': 'draft',
            'total_records': 0,
            'processed_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'skipped_records': 0,
            'notes': _('Retry of import %s') % self.name,
            'log_ids': False,
        })
        
        # Get the failed records from the original import
        failed_logs = self.env['zoho.import.log'].search([
            ('import_history_id', '=', self.id),
            ('status', '=', 'failed')
        ])
        
        # Return an action to open the wizard with the new import history
        return {
            'name': _('Retry Failed Imports'),
            'type': 'ir.actions.act_window',
            'res_model': 'zoho.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_import_history_id': new_history.id,
                'default_import_type': self.import_type,
                'default_retry_mode': True,
                'default_retry_record_ids': failed_logs.mapped('zoho_record_id'),
            },
        }


class ZohoImportLog(models.Model):
    _name = 'zoho.import.log'
    _description = 'Zoho Import Log'
    _order = 'create_date desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    import_history_id = fields.Many2one('zoho.import.history', string='Import History', required=True, ondelete='cascade')
    zoho_record_id = fields.Char(string='Zoho Record ID', required=True)
    zoho_record_name = fields.Char(string='Zoho Record Name')
    record_type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('account', 'Account'),
        ('invoice', 'Invoice'),
        ('bill', 'Bill'),
        ('journal', 'Journal Entry'),
        ('item', 'Item'),
        ('tax', 'Tax'),
        ('currency', 'Currency'),
        ('payment_term', 'Payment Term')
    ], string='Record Type', required=True)
    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped')
    ], string='Status', required=True)
    odoo_record_model = fields.Char(string='Odoo Model')
    odoo_record_id = fields.Integer(string='Odoo Record ID')
    odoo_record_name = fields.Char(string='Odoo Record Name')
    message = fields.Text(string='Message')
    zoho_data = fields.Text(string='Zoho Data')
    create_date = fields.Datetime(string='Created On', readonly=True)
    
    @api.depends('record_type', 'zoho_record_name', 'status')
    def _compute_name(self):
        """Compute the name of the import log"""
        for record in self:
            if record.zoho_record_name:
                record.name = f"{record.record_type.title()} - {record.zoho_record_name} ({record.status.title()})"
            else:
                record.name = f"{record.record_type.title()} - {record.zoho_record_id} ({record.status.title()})"
    
    def action_view_zoho_data(self):
        """View the Zoho data for this log"""
        self.ensure_one()
        if not self.zoho_data:
            raise UserError(_('No Zoho data available for this record.'))
        
        try:
            data = json.loads(self.zoho_data)
            formatted_data = json.dumps(data, indent=4)
            
            return {
                'name': _('Zoho Data'),
                'type': 'ir.actions.act_window',
                'res_model': 'zoho.data.viewer',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_data': formatted_data},
            }
        except Exception as e:
            raise UserError(_('Error parsing Zoho data: %s') % str(e))
    
    def action_view_odoo_record(self):
        """View the Odoo record for this log"""
        self.ensure_one()
        if not self.odoo_record_model or not self.odoo_record_id:
            raise UserError(_('No Odoo record associated with this log.'))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.odoo_record_model,
            'res_id': self.odoo_record_id,
            'view_mode': 'form',
            'target': 'current',
        }


class ZohoDataViewer(models.TransientModel):
    _name = 'zoho.data.viewer'
    _description = 'Zoho Data Viewer'
    
    data = fields.Text(string='Data')
