from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    warranty_ids = fields.Many2one('medical.warranty', 'sale.order_id', string='Garansi')
    warranty_count = fields.Integer(string='Jumlah Garansi', compute='_compute_warranty_count')
    has_medical_product = fields.Boolean(string='Mengandung Alat Kesehatan', compute='_compute_has_medical_product')
