{
    'name': 'SaaS Instance Quota Manager',
    'version': '1.0.0',
    'category': 'SaaS',
    'summary': 'Manage quotas for SaaS instances',
    'description': """
        This module allows SaaS administrators to manage quotas for client instances.
        
        Features:
        - Add quota fields to saas.client model
        - Apply quotas to client instances via XML-RPC
        - Manage quotas from the SaaS admin interface
        - Auto-install record_control_limit module in new instances
    """,
    'author': 'Your Company',
    'depends': ['odoo_saas_kit', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'data/saas_module_data.xml',
        'views/saas_client_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
} 