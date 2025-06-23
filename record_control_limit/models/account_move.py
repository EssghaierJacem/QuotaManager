from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        # Check invoice quota before creating
        self._check_invoice_quota()
        return super(AccountMove, self).create(vals)

    def _check_invoice_quota(self):
        """Check if invoice quota is reached"""
        max_invoices = self.env['ir.config_parameter'].sudo().get_param('record_control_limit.max_invoices')
        
        if max_invoices:
            try:
                max_invoices = int(max_invoices)
                current_invoices = self.env['account.move'].search_count([
                    ('move_type', 'in', ['out_invoice', 'out_refund'])
                ])
                
                if current_invoices >= max_invoices:
                    raise UserError(_(
                        "Quota de factures atteint ! Vous avez atteint la limite de %d factures. "
                        "Contactez votre administrateur pour augmenter votre quota." % max_invoices
                    ))
            except ValueError:
                # If the parameter is not a valid integer, ignore the quota
                pass 