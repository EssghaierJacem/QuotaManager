{
    'name': 'Record Control Limit',
    'version': '1.0.0',
    'category': 'Sales',
    'summary': 'Control quotation and invoice creation limits',
    'description': """
        This module controls the number of quotations (sale.order) and invoices (account.move) 
        that can be created based on quotas defined in system parameters.
        
        Features:
        - Reads quotas from ir.config_parameter
        - Blocks creation when quota is reached
        - Provides quota usage view in Sales menu
    """,
    'author': 'Your Company',
    'depends': ['sale', 'account', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/quota_usage_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
} 