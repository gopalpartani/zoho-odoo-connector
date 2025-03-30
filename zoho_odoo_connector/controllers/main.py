from odoo import http, _
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class ZohoController(http.Controller):
    @http.route('/zoho_odoo_connector/webhook', type='json', auth='public', csrf=False)
    def zoho_webhook(self, **post):
        """Handle webhooks from Zoho Books"""
        _logger.info("Received webhook from Zoho Books")
        
        try:
            # Get the data from the request
            data = request.jsonrequest
            _logger.info("Webhook data: %s", json.dumps(data))
            
            # Verify the webhook signature if needed
            # This would require storing a webhook secret in the configuration
            
            # Process the webhook based on the event type
            event_type = data.get('event_type')
            
            if not event_type:
                return {'status': 'error', 'message': 'Missing event_type'}
            
            # Handle different event types
            if event_type == 'contact.create' or event_type == 'contact.update':
                self._handle_contact_webhook(data)
            elif event_type == 'invoice.create' or event_type == 'invoice.update':
                self._handle_invoice_webhook(data)
            elif event_type == 'bill.create' or event_type == 'bill.update':
                self._handle_bill_webhook(data)
            elif event_type == 'journal.create' or event_type == 'journal.update':
                self._handle_journal_webhook(data)
            else:
                _logger.warning("Unhandled webhook event type: %s", event_type)
                return {'status': 'warning', 'message': f'Unhandled event type: {event_type}'}
            
            return {'status': 'success'}
        
        except Exception as e:
            _logger.exception("Error processing Zoho webhook: %s", str(e))
            return {'status': 'error', 'message': str(e)}
    
    def _handle_contact_webhook(self, data):
        """Handle contact webhooks"""
        contact_data = data.get('contact', {})
        contact_id = contact_data.get('contact_id')
        
        if not contact_id:
            _logger.warning("Missing contact_id in webhook data")
            return
        
        # Check if this contact is already mapped
        mapping = request.env['zoho.contact.mapping'].sudo().search([
            ('zoho_contact_id', '=', contact_id)
        ], limit=1)
        
        if mapping:
            # Contact exists, update it
            _logger.info("Updating existing contact mapping for Zoho contact %s", contact_id)
            # Logic to update the contact would go here
        else:
            # New contact, create it
            _logger.info("Creating new contact from webhook for Zoho contact %s", contact_id)
            # Logic to create the contact would go here
    
    def _handle_invoice_webhook(self, data):
        """Handle invoice webhooks"""
        invoice_data = data.get('invoice', {})
        invoice_id = invoice_data.get('invoice_id')
        
        if not invoice_id:
            _logger.warning("Missing invoice_id in webhook data")
            return
        
        # Check if this invoice is already mapped
        mapping = request.env['zoho.document.mapping'].sudo().search([
            ('zoho_document_id', '=', invoice_id),
            ('zoho_document_type', '=', 'invoice')
        ], limit=1)
        
        if mapping:
            # Invoice exists, update it
            _logger.info("Updating existing invoice mapping for Zoho invoice %s", invoice_id)
            # Logic to update the invoice would go here
        else:
            # New invoice, create it
            _logger.info("Creating new invoice from webhook for Zoho invoice %s", invoice_id)
            # Logic to create the invoice would go here
    
    def _handle_bill_webhook(self, data):
        """Handle bill webhooks"""
        bill_data = data.get('bill', {})
        bill_id = bill_data.get('bill_id')
        
        if not bill_id:
            _logger.warning("Missing bill_id in webhook data")
            return
        
        # Check if this bill is already mapped
        mapping = request.env['zoho.document.mapping'].sudo().search([
            ('zoho_document_id', '=', bill_id),
            ('zoho_document_type', '=', 'bill')
        ], limit=1)
        
        if mapping:
            # Bill exists, update it
            _logger.info("Updating existing bill mapping for Zoho bill %s", bill_id)
            # Logic to update the bill would go here
        else:
            # New bill, create it
            _logger.info("Creating new bill from webhook for Zoho bill %s", bill_id)
            # Logic to create the bill would go here
    
    def _handle_journal_webhook(self, data):
        """Handle journal webhooks"""
        journal_data = data.get('journal', {})
        journal_id = journal_data.get('journal_id')
        
        if not journal_id:
            _logger.warning("Missing journal_id in webhook data")
            return
        
        # Check if this journal is already mapped
        mapping = request.env['zoho.document.mapping'].sudo().search([
            ('zoho_document_id', '=', journal_id),
            ('zoho_document_type', '=', 'journal')
        ], limit=1)
        
        if mapping:
            # Journal exists, update it
            _logger.info("Updating existing journal mapping for Zoho journal %s", journal_id)
            # Logic to update the journal would go here
        else:
            # New journal, create it
            _logger.info("Creating new journal from webhook for Zoho journal %s", journal_id)
            # Logic to create the journal would go here
