from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class ZohoConfig(models.Model):
    _name = 'zoho.config'
    _description = 'Zoho Books Configuration'

    name = fields.Char(string='Name', required=True, default='Zoho Books Configuration')
    client_id = fields.Char(string='Client ID', required=True, help='Zoho Books API Client ID')
    client_secret = fields.Char(string='Client Secret', required=True, help='Zoho Books API Client Secret')
    refresh_token = fields.Char(string='Refresh Token', required=True, help='Zoho Books API Refresh Token')
    organization_id = fields.Char(string='Organization ID', required=True, help='Zoho Books Organization ID')
    access_token = fields.Char(string='Access Token', readonly=True, help='Zoho Books API Access Token (auto-generated)')
    token_expiry = fields.Datetime(string='Token Expiry', readonly=True)
    is_active = fields.Boolean(string='Active', default=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', readonly=True)
    
    _sql_constraints = [
        ('unique_config', 'unique(is_active)', 'Only one active configuration is allowed!')
    ]
    
    @api.model
    def create(self, vals):
        """Ensure only one active configuration exists"""
        if vals.get('is_active', True):
            active_configs = self.search([('is_active', '=', True)])
            if active_configs:
                raise UserError(_('Only one active configuration is allowed. Please deactivate the existing one first.'))
        return super(ZohoConfig, self).create(vals)
    
    def write(self, vals):
        """Ensure only one active configuration exists"""
        if vals.get('is_active', False):
            active_configs = self.search([('is_active', '=', True), ('id', '!=', self.id)])
            if active_configs:
                raise UserError(_('Only one active configuration is allowed. Please deactivate the existing one first.'))
        return super(ZohoConfig, self).write(vals)
    
    def generate_access_token(self):
        """Generate a new access token using the refresh token"""
        self.ensure_one()
        
        if not self.client_id or not self.client_secret or not self.refresh_token:
            raise UserError(_('Client ID, Client Secret, and Refresh Token are required.'))
        
        url = 'https://accounts.zoho.com/oauth/v2/token'
        data = {
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            
            if 'access_token' in result:
                self.write({
                    'access_token': result['access_token'],
                    'token_expiry': fields.Datetime.now() + fields.Datetime.from_string('PT1H'),  # Token valid for 1 hour
                })
                return True
            else:
                raise UserError(_('Failed to generate access token: %s') % result.get('error_description', 'Unknown error'))
        
        except requests.exceptions.RequestException as e:
            raise UserError(_('Error connecting to Zoho API: %s') % str(e))
    
    def test_connection(self):
        """Test the connection to Zoho Books API"""
        self.ensure_one()
        
        # First, generate a new access token
        self.generate_access_token()
        
        if not self.access_token:
            raise UserError(_('Failed to generate access token.'))
        
        # Test the connection by fetching organization details
        url = f'https://books.zoho.com/api/v3/organizations/{self.organization_id}'
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') == 0:  # Success code in Zoho API
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _('Successfully connected to Zoho Books!'),
                        'sticky': False,
                        'type': 'success',
                    }
                }
            else:
                raise UserError(_('Failed to connect to Zoho Books: %s') % result.get('message', 'Unknown error'))
        
        except requests.exceptions.RequestException as e:
            raise UserError(_('Error connecting to Zoho API: %s') % str(e))
