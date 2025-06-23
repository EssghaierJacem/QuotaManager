from odoo import models, fields, api, _
from odoo.exceptions import UserError


class QuotaUsage(models.Model):
    _name = 'quota.usage'
    _description = 'Quota Usage Display'
    _auto = False  # This is a database view

    name = fields.Char(string='Quota Type', readonly=True)
    total_quota = fields.Integer(string='Total Quota', readonly=True)
    current_usage = fields.Integer(string='Current Usage', readonly=True)
    remaining = fields.Integer(string='Remaining', readonly=True)
    percentage_used = fields.Float(string='Percentage Used (%)', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)

    def init(self):
        tools = self.env['ir.module.module'].sudo().search([('name', '=', 'base')])
        if tools:
            self.env.cr.execute("""
                CREATE OR REPLACE VIEW quota_usage AS (
                    SELECT 
                        'quotations' as name,
                        COALESCE(CAST(param_quotations.value AS INTEGER), 0) as total_quota,
                        COUNT(so.id) as current_usage,
                        GREATEST(0, COALESCE(CAST(param_quotations.value AS INTEGER), 0) - COUNT(so.id)) as remaining,
                        CASE 
                            WHEN COALESCE(CAST(param_quotations.value AS INTEGER), 0) > 0 
                            THEN ROUND((COUNT(so.id)::numeric / CAST(param_quotations.value AS numeric)) * 100, 2)
                            ELSE 0 
                        END as percentage_used,
                        so.company_id as company_id
                    FROM sale_order so
                    CROSS JOIN ir_config_parameter param_quotations
                    WHERE param_quotations.key = 'record_control_limit.max_quotations'
                    GROUP BY param_quotations.value, so.company_id
                    
                    UNION ALL
                    
                    SELECT 
                        'invoices' as name,
                        COALESCE(CAST(param_invoices.value AS INTEGER), 0) as total_quota,
                        COUNT(am.id) as current_usage,
                        GREATEST(0, COALESCE(CAST(param_invoices.value AS INTEGER), 0) - COUNT(am.id)) as remaining,
                        CASE 
                            WHEN COALESCE(CAST(param_invoices.value AS INTEGER), 0) > 0 
                            THEN ROUND((COUNT(am.id)::numeric / CAST(param_invoices.value AS numeric)) * 100, 2)
                            ELSE 0 
                        END as percentage_used,
                        am.company_id as company_id
                    FROM account_move am
                    CROSS JOIN ir_config_parameter param_invoices
                    WHERE param_invoices.key = 'record_control_limit.max_invoices'
                    AND am.move_type IN ('out_invoice', 'out_refund')
                    GROUP BY param_invoices.value, am.company_id
                )
            """) 