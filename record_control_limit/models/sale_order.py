from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # Check quotation quota before creating
        self._check_quotation_quota()
        return super(SaleOrder, self).create(vals)

    def _check_quotation_quota(self):
        """Check if quotation quota is reached"""
        max_quotations = self.env['ir.config_parameter'].sudo().get_param('record_control_limit.max_quotations')
        
        if max_quotations:
            try:
                max_quotations = int(max_quotations)
                current_quotations = self.env['sale.order'].search_count([
                    ('company_id', '=', self.env.company.id)
                ])
                
                if current_quotations >= max_quotations:
                    raise UserError(_(
                        "Quota de devis atteint ! Vous avez atteint la limite de %d devis. "
                        "Contactez votre administrateur pour augmenter votre quota." % max_quotations
                    ))
            except ValueError:
                # If the parameter is not a valid integer, ignore the quota
                pass 