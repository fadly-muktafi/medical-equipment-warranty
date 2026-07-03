from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    warranty_ids = fields.Many2one('medical.warranty', 'sale.order_id', string='Garansi')
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
                line.product_id and line.product_id.product_template_id.is_medical_device
                for line in order.order_line
            )
