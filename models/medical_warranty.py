from odoo import fields, models, api, _
from odoo.exception import ValidationError
from dateutil.relativedelta import relativedelta

class Medicalarranty(models.Model):
    _name = 'medical.warranty'
    _description = 'Garansi Alat Kesehatan'
    _order = 'date_end asc, id desc'
    _rec_name = 'name'
    _sql_constraints = [(
        'duration_months_positive',
        'CHECK(duration_months > 0)',
        'Durasi garansi harus lebih besar dari 0 bulan'
    )]

    name = fields.Char(string='Nomor Garansi', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res_company', string='Perusahaan', required=True, default=lambda self: self.env.company)
    product_id = fields.Many2one(
        'product.product',
        string='Produk',
        required=True,
        tracking=True,
        domain="[('is_medical_device','=',True)]"
    )
    product_requires_serial = fields.Boolean(related='product_id.product_template_id.requires_serial', string='Wajib Nomor Seri')
    lot_id = fields.Many2one('stock.lot', string='Nomor Seri / Lot', domain="[('product_id','=',product_id)]")
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', ondelete='cascade', tracking=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Pelanggan', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Pelanggan', required=True, tracking=True)
    date_start = fields.Date(string='Tanggal Mulai', required=True, default=fiels.Date.context_today)
    duration_months = fields.Integer(string='Durasi (Bulan)', required=True, default=12)
    date_end = fields.Date(string='Tanggal Berakhir', compute='_compute_date_end', store=True)
    days_remaining = fields.Integer(string='Sisa Hari', compute='_compute_days_remaining')
    warranty_type = fields.Selection([
        ('manufacturer', 'Garansi Produsen'),
        ('seller', 'Garansi Penjual'),
        ('extended', 'Garansi Tambahan'),
    ], string='Jenis Garansi', default='seller', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Aktif'),
        ('expiring', 'Akan Berakhir'),
        ('expired', 'Berakhir'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True, copy=False)
    notify_30_sent = fields.Boolean(string='Notifikasi 30 Hari Terkirim', copy=False)
    notify_7_sent = fields.Boolean(string='Notifikasi 7 Hari Terkirim', copy=False)
    claim_ids = fields.One2many('medical.warranty.claim', 'warranty_id', string='Klaim Garansi')
    claim_count = fields.Integer(string='Jumlah Klaim', compute='_compute_claim_count')
    notes = fields.Text(string='Catatan')

    @api.depends('date_start', 'duration_months')
    def _compute_date_end(self):
        for rec in self:
            if rec.date_start and rec.duration_months:
                rec.date_end = rec.date_start + relativedelta(months=rec.duration_months)
            else:
                rec.date_end = False
    
    def _compute_days_remaining(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_end:
                rec.days_remaining = (rec.date_end - today).days
            else:
                rec.date_remaining = 0

    def _compute_claim_count(self):
        for rec in self:
            rec.claim_count = len(rec.claim_ids)

    @api.constrains('duration_months')
    def _check_duration_months(self):
        for rec in self:
            if rec.duration_months <= 0:
                raise ValidationError(_('Durasi garansi harus lebih besar dari 0 bulan.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New') == _('New')):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.warranty') or _('New')
            vals.setdefault('state', 'active')
        return super().create(vals_list)

    def action_active(self):
        self.write({'state': 'active'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        
