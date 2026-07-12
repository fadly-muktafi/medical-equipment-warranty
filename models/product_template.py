from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_medical_device = fields.Boolean(string='Alat Kesehatan')
    medical_category = fields.Selection([
        ('diagnostic', 'Diagnostik'),
        ('therapeutic', 'Alat Terapi'),
        ('disposable', 'Produk Disposable'),
        ('hospital_equipment', 'Peralatan Rumah Sakit'),
        ('lab_equipment', 'Alat Laboratorium'),
        ('mobility_aid', 'Alat Bantu Mobilitas'),
        ('other', 'Lainnya'),
    ], string='Kategori Medis')

    warranty_duration = fields.Integer(string='Durasi Garansi (Bulan)', default=12)
    requires_serial = fields.Boolean(string='Wajib Nomor Seri')
    
    bpom_number = fields.Char(string='Nomor Izin Edar BPOM')
    kemenkes_certif = fields.Char(string='Nomor Sertifikasi Kemenkes')
    certif_expiry_date = fields.Date(string='Tanggal Kadaluwarsa Sertifikasi')
    certif_expired = fields.Boolean(string='Sertifikasi Kadaluwarsa', compute='_compute_certif_expired')

    @api.depends('certif_expiry_date')
    def _compute_certif_expired(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.certif_expired = bool(rec.certif_expiry_date and rec.certif_expiry_date < today)
