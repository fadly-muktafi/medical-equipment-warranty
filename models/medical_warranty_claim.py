from odoo import fields, models, api, _

class MedicalWarrantyClaim(models.Model):
    _name = 'medical.warranty.claim'
    _description = 'Klaim Garansi Alat Kesehatan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'claim_date desc, id desc'

    name = fields.Char(string='Nomor Klaim', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    warranty_id = fields.Many2one('medical.warranty', string='Garansi', required=True, ondelete='cascade', tracking=True)
    product_id = fields.Many2one(related='warranty_id.product_id', string='Produk', store=True, readonly=True)
    partner_id = fields.Many2one(related='warranty_id.partner_id', string='Pelanggan', store=True, readonly=True)
    company_id = fields.Many2one(related='warranty_id.company_id', string='Perusahaan', store=True, readonly=True)
    claim_date = fields.Date(string='Tanggal Klaim', required=True, default=fields.Date.context_today)
    description = fields.Text(string='Deskripsi Masalah', required=True)
    resolution = fieldss.Text(string='Resolusi / Tindak Lanjut')
    state = fields.Selection([
        ('new', 'Baru'),
        ('progress', 'Diproses'),
        ('rejected', 'Ditolak'),
        ('resolved', 'Selesai'),
    ], string='Status', default='new', tracking=True, copy=False)
    