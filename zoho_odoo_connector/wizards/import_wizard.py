from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import json
from datetime import datetime
import time

_logger = logging.getLogger(__name__)

class ZohoImportWizard(models.TransientModel):
    _name = 'zoho.import.wizard'
    _description = 'Zoho Import Wizard'
    
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
    ], string='Import Type', required=True, default='customers')
    
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    
    create_missing = fields.Boolean(string='Create Missing Records', default=True,
                                   help='Create records in Odoo if they do not exist')
    update_existing = fields.Boolean(string='Update Existing Records', default=True,
                                    help='Update existing records in Odoo with data from Zoho')
    
    import_history_id = fields.Many2one('zoho.import.history', string='Import History', readonly=True)
    state = fields.Selection([
        ('config', 'Configuration'),
        ('preview', 'Preview'),
        ('importing', 'Importing'),
        ('done', 'Done')
    ], string='State', default='config', required=True)
    
    preview_data = fields.Text(string='Preview Data', readonly=True)
    preview_count = fields.Integer(string='Record Count', readonly=True)
    
    progress = fields.Integer(string='Progress', readonly=True, default=0)
    message = fields.Text(string='Message', readonly=True)
    
    retry_mode = fields.Boolean(string='Retry Mode', default=False)
    retry_record_ids = fields.Text(string='Retry Record IDs')
    
    def action_preview(self):
        """Preview the data to be imported"""
        self.ensure_one()
        
        try:
            # Get the API connector
            api = self.env['zoho.api']
            
            # Get the data based on the import type
            if self.import_type == 'customers':
                result = api.get_customers(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('contacts', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'vendors':
                result = api.get_vendors(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('contacts', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'chart_of_accounts':
                result = api.get_chart_of_accounts(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('chartofaccounts', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'invoices':
                result = api.get_invoices(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('invoices', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'bills':
                result = api.get_bills(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('bills', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'journal_entries':
                result = api.get_journal_entries(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('journals', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'items':
                result = api.get_items(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('items', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'taxes':
                result = api.get_taxes(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('taxes', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'currencies':
                result = api.get_currencies(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('currencies', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'payment_terms':
                result = api.get_payment_terms(page=1, per_page=10)  # Limit to 10 for preview
                records = result.get('payment_terms', [])
                self.preview_count = result.get('page_context', {}).get('total', 0)
            elif self.import_type == 'all':
                # For 'all', just show a summary of what will be imported
                self.preview_data = json.dumps({
                    'message': 'All data will be imported. This may take a while.',
                    'types': [
                        'customers', 'vendors', 'chart_of_accounts', 'invoices', 
                        'bills', 'journal_entries', 'items', 'taxes', 
                        'currencies', 'payment_terms'
                    ]
                }, indent=4)
                self.state = 'preview'
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': self._name,
                    'res_id': self.id,
                    'view_mode': 'form',
                    'target': 'new',
                }
            
            # Format the preview data
            self.preview_data = json.dumps(records, indent=4)
            
            # Update the state
            self.state = 'preview'
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
        
        except Exception as e:
            raise UserError(_('Error previewing data: %s') % str(e))
    
    def action_import(self):
        """Start the import process"""
        self.ensure_one()
        
        # Create an import history record if one doesn't exist
        if not self.import_history_id:
            self.import_history_id = self.env['zoho.import.history'].create({
                'import_type': self.import_type,
                'status': 'in_progress',
                'notes': f'Import initiated by {self.env.user.name}'
            })
        else:
            self.import_history_id.write({
                'status': 'in_progress',
                'import_date': fields.Datetime.now()
            })
        
        # Update the state
        self.state = 'importing'
        self.message = _('Import started. This may take a while...')
        
        # Return the view to show progress
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_do_import(self):
        """Perform the actual import (called from the client via AJAX)"""
        self.ensure_one()
        
        try:
            # Get the API connector
            api = self.env['zoho.api']
            
            # Determine which import method to call based on the import type
            if self.import_type == 'customers':
                self._import_customers(api)
            elif self.import_type == 'vendors':
                self._import_vendors(api)
            elif self.import_type == 'chart_of_accounts':
                self._import_chart_of_accounts(api)
            elif self.import_type == 'invoices':
                self._import_invoices(api)
            elif self.import_type == 'bills':
                self._import_bills(api)
            elif self.import_type == 'journal_entries':
                self._import_journal_entries(api)
            elif self.import_type == 'items':
                self._import_items(api)
            elif self.import_type == 'taxes':
                self._import_taxes(api)
            elif self.import_type == 'currencies':
                self._import_currencies(api)
            elif self.import_type == 'payment_terms':
                self._import_payment_terms(api)
            elif self.import_type == 'all':
                self._import_all(api)
            
            # Update the import history
            if self.import_history_id.failed_records > 0:
                status = 'partially_completed'
            else:
                status = 'completed'
            
            self.import_history_id.write({
                'status': status,
                'last_sync_date': fields.Datetime.now()
            })
            
            # Update the wizard state
            self.state = 'done'
            self.message = _('Import completed successfully!')
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
        
        except Exception as e:
            # Update the import history
            self.import_history_id.write({
                'status': 'failed',
                'notes': f'{self.import_history_id.notes or ""}\nError: {str(e)}'
            })
            
            # Update the wizard state
            self.state = 'done'
            self.message = _('Import failed: %s') % str(e)
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }
    
    def action_view_import_history(self):
        """View the import history"""
        self.ensure_one()
        
        return {
            'name': _('Import History'),
            'type': 'ir.actions.act_window',
            'res_model': 'zoho.import.history',
            'res_id': self.import_history_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def _import_customers(self, api):
        """Import customers from Zoho Books"""
        # Implementation would go here
        # This would fetch customers from Zoho Books and create/update them in Odoo
        pass
    
    def _import_vendors(self, api):
        """Import vendors from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_chart_of_accounts(self, api):
        """Import chart of accounts from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_invoices(self, api):
        """Import invoices from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_bills(self, api):
        """Import bills from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_journal_entries(self, api):
        """Import journal entries from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_items(self, api):
        """Import items from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_taxes(self, api):
        """Import taxes from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_currencies(self, api):
        """Import currencies from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_payment_terms(self, api):
        """Import payment terms from Zoho Books"""
        # Implementation would go here
        pass
    
    def _import_all(self, api):
        """Import all data from Zoho Books"""
        # This would call all the other import methods in the correct order
        self._import_currencies(api)
        self._import_taxes(api)
        self._import_payment_terms(api)
        self._import_chart_of_accounts(api)
        self._import_customers(api)
        self._import_vendors(api)
        self._import_items(api)
        self._import_invoices(api)
        self._import_bills(api)
        self._import_journal_entries(api)
