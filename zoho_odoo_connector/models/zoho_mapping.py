from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ZohoAccountMapping(models.Model):
    _name = 'zoho.account.mapping'
    _description = 'Zoho Account Mapping'
    _rec_name = 'zoho_account_name'

    zoho_account_id = fields.Char(string='Zoho Account ID', required=True)
    zoho_account_name = fields.Char(string='Zoho Account Name', required=True)
    zoho_account_type = fields.Char(string='Zoho Account Type')
    odoo_account_id = fields.Many2one('account.account', string='Odoo Account', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_account', 'unique(zoho_account_id)', 'This Zoho account is already mapped!')
    ]


class ZohoTaxMapping(models.Model):
    _name = 'zoho.tax.mapping'
    _description = 'Zoho Tax Mapping'
    _rec_name = 'zoho_tax_name'

    zoho_tax_id = fields.Char(string='Zoho Tax ID', required=True)
    zoho_tax_name = fields.Char(string='Zoho Tax Name', required=True)
    zoho_tax_percentage = fields.Float(string='Zoho Tax Percentage')
    odoo_tax_id = fields.Many2one('account.tax', string='Odoo Tax', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_tax', 'unique(zoho_tax_id)', 'This Zoho tax is already mapped!')
    ]


class ZohoPaymentTermMapping(models.Model):
    _name = 'zoho.payment.term.mapping'
    _description = 'Zoho Payment Term Mapping'
    _rec_name = 'zoho_term_name'

    zoho_term_id = fields.Char(string='Zoho Term ID', required=True)
    zoho_term_name = fields.Char(string='Zoho Term Name', required=True)
    odoo_term_id = fields.Many2one('account.payment.term', string='Odoo Payment Term', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_term', 'unique(zoho_term_id)', 'This Zoho payment term is already mapped!')
    ]


class ZohoCurrencyMapping(models.Model):
    _name = 'zoho.currency.mapping'
    _description = 'Zoho Currency Mapping'
    _rec_name = 'zoho_currency_name'

    zoho_currency_id = fields.Char(string='Zoho Currency ID', required=True)
    zoho_currency_name = fields.Char(string='Zoho Currency Name', required=True)
    zoho_currency_code = fields.Char(string='Zoho Currency Code', required=True)
    odoo_currency_id = fields.Many2one('res.currency', string='Odoo Currency', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_currency', 'unique(zoho_currency_id)', 'This Zoho currency is already mapped!')
    ]


class ZohoContactMapping(models.Model):
    _name = 'zoho.contact.mapping'
    _description = 'Zoho Contact Mapping'
    _rec_name = 'zoho_contact_name'

    zoho_contact_id = fields.Char(string='Zoho Contact ID', required=True)
    zoho_contact_name = fields.Char(string='Zoho Contact Name', required=True)
    zoho_contact_type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('both', 'Both')
    ], string='Contact Type', required=True)
    odoo_partner_id = fields.Many2one('res.partner', string='Odoo Partner', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_contact', 'unique(zoho_contact_id)', 'This Zoho contact is already mapped!')
    ]


class ZohoJournalMapping(models.Model):
    _name = 'zoho.journal.mapping'
    _description = 'Zoho Journal Mapping'
    _rec_name = 'zoho_journal_name'

    zoho_journal_id = fields.Char(string='Zoho Journal ID', required=True)
    zoho_journal_name = fields.Char(string='Zoho Journal Name', required=True)
    odoo_journal_id = fields.Many2one('account.journal', string='Odoo Journal', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_journal', 'unique(zoho_journal_id)', 'This Zoho journal is already mapped!')
    ]


class ZohoItemMapping(models.Model):
    _name = 'zoho.item.mapping'
    _description = 'Zoho Item Mapping'
    _rec_name = 'zoho_item_name'

    zoho_item_id = fields.Char(string='Zoho Item ID', required=True)
    zoho_item_name = fields.Char(string='Zoho Item Name', required=True)
    odoo_product_id = fields.Many2one('product.product', string='Odoo Product', required=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_item', 'unique(zoho_item_id)', 'This Zoho item is already mapped!')
    ]


class ZohoDocumentMapping(models.Model):
    _name = 'zoho.document.mapping'
    _description = 'Zoho Document Mapping'
    
    zoho_document_id = fields.Char(string='Zoho Document ID', required=True)
    zoho_document_number = fields.Char(string='Zoho Document Number')
    zoho_document_type = fields.Selection([
        ('invoice', 'Invoice'),
        ('bill', 'Bill'),
        ('journal', 'Journal Entry'),
        ('payment', 'Payment'),
        ('credit_note', 'Credit Note'),
        ('debit_note', 'Debit Note')
    ], string='Document Type', required=True)
    odoo_document_model = fields.Char(string='Odoo Model', required=True)
    odoo_document_id = fields.Integer(string='Odoo Document ID', required=True)
    odoo_document_name = fields.Char(string='Odoo Document Name', compute='_compute_odoo_document_name', store=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_zoho_document', 'unique(zoho_document_id, zoho_document_type)', 'This Zoho document is already mapped!')
    ]
    
    @api.depends('odoo_document_model', 'odoo_document_id')
    def _compute_odoo_document_name(self):
        """Compute the name of the Odoo document"""
        for record in self:
            if record.odoo_document_model and record.odoo_document_id:
                try:
                    document = self.env[record.odoo_document_model].browse(record.odoo_document_id)
                    if document.exists():
                        record.odoo_document_name = document.display_name
                    else:
                        record.odoo_document_name = f"Document not found ({record.odoo_document_id})"
                except Exception as e:
                    record.odoo_document_name = f"Error: {str(e)}"
            else:
                record.odoo_document_name = "Not mapped yet"
