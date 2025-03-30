{
    'name': 'Zoho Books to Odoo Accounting Connector',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Import data from Zoho Books to Odoo Accounting',
    'description': """
        This module allows you to import data from Zoho Books to Odoo Accounting.
        Features include:
        - Import customers and vendors
        - Import chart of accounts
        - Import bills and invoices
        - Import journal entries
        - Configuration for API credentials
        - Mapping between Zoho Books and Odoo Accounting
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'base',
        'account',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/zoho_config_views.xml',
        'views/zoho_mapping_views.xml',
        'views/menu_views.xml',
        'wizards/import_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'external_dependencies': {
        'python': ['requests'],
    },
}
