from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class ZohoAPI(models.AbstractModel):
    _name = 'zoho.api'
    _description = 'Zoho Books API Connector'

    def _get_active_config(self):
        """Get the active Zoho configuration"""
        config = self.env['zoho.config'].search([('is_active', '=', True)], limit=1)
        if not config:
            raise UserError(_('No active Zoho Books configuration found. Please configure one first.'))
        return config

    def _ensure_valid_token(self, config=None):
        """Ensure we have a valid access token"""
        if not config:
            config = self._get_active_config()
        
        # Check if token is expired or will expire in the next 5 minutes
        now = fields.Datetime.now()
        if not config.access_token or not config.token_expiry or config.token_expiry <= now + timedelta(minutes=5):
            config.generate_access_token()
        
        if not config.access_token:
            raise UserError(_('Failed to generate access token.'))
        
        return config

    def _make_request(self, endpoint, method='GET', params=None, data=None, config=None):
        """Make a request to the Zoho Books API"""
        if not config:
            config = self._ensure_valid_token()
        
        base_url = f'https://books.zoho.com/api/v3'
        url = f'{base_url}/{endpoint}'
        
        headers = {
            'Authorization': f'Zoho-oauthtoken {config.access_token}',
            'Content-Type': 'application/json',
            'organizationId': config.organization_id
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, params=params, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, params=params, json=data)
            else:
                raise UserError(_('Unsupported HTTP method: %s') % method)
            
            response.raise_for_status()
            result = response.json()
            
            # Check for Zoho API error
            if result.get('code') != 0 and 'message' in result:
                raise UserError(_('Zoho API Error: %s') % result.get('message'))
            
            return result
        
        except requests.exceptions.RequestException as e:
            # If token expired, try to regenerate and retry once
            if response.status_code == 401:
                _logger.info("Access token expired, regenerating...")
                config.generate_access_token()
                return self._make_request(endpoint, method, params, data, config)
            
            raise UserError(_('Error connecting to Zoho API: %s') % str(e))

    def get_customers(self, page=1, per_page=200):
        """Get customers from Zoho Books"""
        return self._make_request('contacts', params={
            'filter_by': 'CustomerType.Customers',
            'page': page,
            'per_page': per_page
        })

    def get_vendors(self, page=1, per_page=200):
        """Get vendors from Zoho Books"""
        return self._make_request('contacts', params={
            'filter_by': 'VendorType.Vendors',
            'page': page,
            'per_page': per_page
        })

    def get_chart_of_accounts(self, page=1, per_page=200):
        """Get chart of accounts from Zoho Books"""
        return self._make_request('chartofaccounts', params={
            'page': page,
            'per_page': per_page
        })

    def get_invoices(self, page=1, per_page=200):
        """Get invoices from Zoho Books"""
        return self._make_request('invoices', params={
            'page': page,
            'per_page': per_page
        })

    def get_bills(self, page=1, per_page=200):
        """Get bills from Zoho Books"""
        return self._make_request('bills', params={
            'page': page,
            'per_page': per_page
        })

    def get_journal_entries(self, page=1, per_page=200):
        """Get journal entries from Zoho Books"""
        return self._make_request('journals', params={
            'page': page,
            'per_page': per_page
        })

    def get_items(self, page=1, per_page=200):
        """Get items from Zoho Books"""
        return self._make_request('items', params={
            'page': page,
            'per_page': per_page
        })

    def get_taxes(self, page=1, per_page=200):
        """Get taxes from Zoho Books"""
        return self._make_request('settings/taxes', params={
            'page': page,
            'per_page': per_page
        })

    def get_currencies(self, page=1, per_page=200):
        """Get currencies from Zoho Books"""
        return self._make_request('settings/currencies', params={
            'page': page,
            'per_page': per_page
        })

    def get_payment_terms(self, page=1, per_page=200):
        """Get payment terms from Zoho Books"""
        return self._make_request('settings/paymentterms', params={
            'page': page,
            'per_page': per_page
        })
