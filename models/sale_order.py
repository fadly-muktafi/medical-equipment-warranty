from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    warranty_ids = fields.One2many('medical.warranty', 'sale_order_id', string='Garansi')
    warranty_count = fields.Integer(string='Jumlah Garansi', compute='_compute_warranty_count')
    has_medical_product = fields.Boolean(string='Mengandung Alat Kesehatan', compute='_compute_has_medical_product')

    @api.depends('warranty_ids')
    def _compute_warranty_count(self):
        for order in self:
            order.warranty_count = len(order.warranty_ids)

    @api.depends('order_line.product_id')
    def _compute_has_medical_product(self):
        for order in self:
            order.has_medical_product = any(
                line.product_id and line.product_id.product_tmpl_id.is_medical_device
                for line in order.order_line
            )

    def action_confirm(self):
        res = super().action_confirm()
        self._generate_medical_warranties()
        return res

    def _generate_medical_warranties(self):
        Warranty = self.env['medical.warranty']
        for order in self:
            existing_line_ids = order.warranty_ids.mapped('sale_order_line_id').ids
            lines = order.order_line.filtered(
                lambda l: l.product_id
                and l.product_id.product_tmpl_id.is_medical_device
                and l.id not in existing_line_ids
            )
            for line in lines:
                product_template = line.product_id.product_tmpl_id
                Warranty.create({
                    'product_id': line.product_id.id,
                    'sale_order_id': order.id,
                    'sale_order_line_id': line.id,
                    'partner_id': order.partner_id.id,
                    'date_start': order.date_order.date() if order.date_order else fields.Date.context_today(self),
                    'duration_months': product_template.warranty_duration or 12,
                    'warranty_type': 'seller', 
                })

    def action_generate_warranty(self):
        self.ensure_one()
        self._generate_medical_warranties()
        return self.action_view_warranty()

    def action_view_warranty(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('medical_equipment_warranty.action_medical_warranty')
        action['domain'] = [('sale_order_id', '=', self.id)]
        action['context'] = {
            'default_sale_order_id': self.id,
            'default_partner_id': self.partner_id.id,
        }
        return action
