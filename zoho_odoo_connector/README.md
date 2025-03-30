# Zoho Books to Odoo Accounting Connector

This module allows you to import data from Zoho Books to Odoo Accounting.

## Features

- Import customers and vendors
- Import chart of accounts
- Import bills and invoices
- Import journal entries
- Configuration for API credentials
- Mapping between Zoho Books and Odoo Accounting

## Installation

1. Download the module
2. Extract it to your Odoo addons directory
3. Restart Odoo server
4. Go to Apps menu and install the module

## Configuration

1. Go to Zoho Books > Configuration > API Configuration
2. Create a new configuration with your Zoho Books API credentials
3. Test the connection to ensure it works

## Usage

1. Set up mappings between Zoho Books and Odoo entities
2. Use the import wizard to import data from Zoho Books
3. View import history and logs to track the import process

## Getting Zoho Books API Credentials

1. Go to [Zoho API Console](https://api-console.zoho.com/)
2. Create a new client (Self Client)
3. Set the scope to "ZohoBooks.fullaccess.all"
4. Generate the code and then exchange it for a refresh token
5. Find your organization ID in Zoho Books under Settings > Organization Profile

## Technical Details

The module uses the Zoho Books API v3 to fetch data from Zoho Books and import it into Odoo. It provides a mapping system to map Zoho Books entities to Odoo entities, and a logging system to track the import process.

## Dependencies

- Odoo Accounting module (account)
- Odoo Contacts module (contacts)
- Python requests library

## License

LGPL-3
