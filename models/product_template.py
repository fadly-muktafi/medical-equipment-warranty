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
        ('mobility_aid', 'Alat Bntu Mobilitas'),
        ('other', 'Lainnya'),
    ], string='Kategori Medis')

    warranty_duration = fields.Integer(string='Durasi Garansi (Bulan)', default=12)
    requires_serial = fields.Boolean(string='Wajib Nomor Seri')
    bpom_number = fields.Char(string='Nomor Izin Edar BPOM')
    kemenkes_certif = fields.Char(string='Nomor Sertifikasi Kemenkes')
    certif_expiry_date = fields.Date(string='Tanggal Kadaluwarsa Sertifikasi')
    certif_expired = fields.Boolean(string='Sertifikasi Kadaluwarsa', compute='_compute_certif_expired')
