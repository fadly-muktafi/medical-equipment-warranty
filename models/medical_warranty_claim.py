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
    resolution = fields.Text(string='Resolusi / Tindak Lanjut')
    
    state = fields.Selection([
        ('new', 'Baru'),
        ('progress', 'Diproses'),
        ('rejected', 'Ditolak'),
        ('resolved', 'Selesai'),
    ], string='Status', default='new', tracking=True, copy=False)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.warranty.claim') or _('New')
            return super().create(vals_list)

    def action_set_progress(self):
        self.write({'state': 'progress'})

    def action_set_rejected(self):
        self.write({'state': 'rejected'})

    def action_set_resolved(self):
        self.write({'state': 'resolved'})

    def action_reset_new(self):
        self.write({'state': 'new'})
