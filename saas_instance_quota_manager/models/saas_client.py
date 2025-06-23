from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)


class SaasClient(models.Model):
    _inherit = 'saas.client'

    max_quotations = fields.Integer(string='Max Quotations', default=0, help="Maximum number of quotations allowed (0 = unlimited)")
    max_invoices = fields.Integer(string='Max Invoices', default=0, help="Maximum number of invoices allowed (0 = unlimited)")

    def apply_quotas(self):
        """Apply quotas to the client instance via XML-RPC"""
        for client in self:
            if not client.client_url:
                raise UserError(_("URL client non définie pour l'instance %s") % client.name)
            
            try:
                # Get client credentials from the SaaS contract
                if not client.saas_contract_id:
                    raise UserError(_("Aucun contrat SaaS associé à l'instance %s") % client.name)
                
                contract = client.saas_contract_id
                
                # Connect to client instance
                client_url = client.client_url.rstrip('/')
                common = xmlrpc.client.ServerProxy(f'{client_url}/xmlrpc/2/common')
                
                # Try to authenticate with admin user
                uid = common.authenticate(contract.db_template, 'admin', contract.token, {})
                
                if not uid:
                    raise UserError(_("Impossible de s'authentifier sur l'instance %s") % client.name)
                
                # Connect to models
                models = xmlrpc.client.ServerProxy(f'{client_url}/xmlrpc/2/object')
                
                # Update configuration parameters
                if client.max_quotations > 0:
                    models.execute_kw(contract.db_template, uid, contract.token, 'ir.config_parameter', 'set_param', [
                        'record_control_limit.max_quotations', str(client.max_quotations)
                    ])
                
                if client.max_invoices > 0:
                    models.execute_kw(contract.db_template, uid, contract.token, 'ir.config_parameter', 'set_param', [
                        'record_control_limit.max_invoices', str(client.max_invoices)
                    ])
                
                # If quotas are set to 0, remove the parameters (unlimited)
                if client.max_quotations == 0:
                    models.execute_kw(contract.db_template, uid, contract.token, 'ir.config_parameter', 'unlink', [
                        models.execute_kw(contract.db_template, uid, contract.token, 'ir.config_parameter', 'search', [
                            [('key', '=', 'record_control_limit.max_quotations')]
                        ])
                    ])
                
                if client.max_invoices == 0:
                    models.execute_kw(contract.db_template, uid, contract.token, 'ir.config_parameter', 'unlink', [
                        models.execute_kw(contract.db_template, uid, contract.token, 'ir.config_parameter', 'search', [
                            [('key', '=', 'record_control_limit.max_invoices')]
                        ])
                    ])
                
                _logger.info(f"Quotas applied successfully to instance {client.name}")
                
            except Exception as e:
                _logger.error(f"Error applying quotas to instance {client.name}: {str(e)}")
                raise UserError(_("Erreur lors de l'application des quotas à l'instance %s: %s") % (client.name, str(e)))

    def get_quota_usage(self):
        """Get current quota usage from client instance"""
        for client in self:
            if not client.client_url or not client.saas_contract_id:
                continue
                
            try:
                contract = client.saas_contract_id
                client_url = client.client_url.rstrip('/')
                common = xmlrpc.client.ServerProxy(f'{client_url}/xmlrpc/2/common')
                
                uid = common.authenticate(contract.db_template, 'admin', contract.token, {})
                if not uid:
                    continue
                
                models = xmlrpc.client.ServerProxy(f'{client_url}/xmlrpc/2/object')
                
                # Get current usage
                quotation_count = models.execute_kw(contract.db_template, uid, contract.token, 'sale.order', 'search_count', [[]])
                invoice_count = models.execute_kw(contract.db_template, uid, contract.token, 'account.move', 'search_count', [
                    [('move_type', 'in', ['out_invoice', 'out_refund'])]
                ])
                
                return {
                    'quotations': quotation_count,
                    'invoices': invoice_count
                }
                
            except Exception as e:
                _logger.error(f"Error getting quota usage for instance {client.name}: {str(e)}")
                return None 