from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta

class MedicalWarranty(models.Model):
    _name = 'medical.warranty'
    _description = 'Garansi Alat Kesehatan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_end asc, id desc'
    _rec_name = 'name'
    _sql_constraints = [(
        'duration_months_positive',
        'CHECK(duration_months > 0)',
        'Durasi garansi harus lebih besar dari 0 bulan'
    )]

    name = fields.Char(string='Nomor Garansi', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Perusahaan', required=True, default=lambda self: self.env.company)

    product_id = fields.Many2one(
        'product.product', string='Produk', required=True, tracking=True, domain="[('is_medical_device','=',True)]"
    )
    product_requires_serial = fields.Boolean(related='product_id.product_tmpl_id.requires_serial', string='Wajib Nomor Seri')
    lot_id = fields.Many2one('stock.lot', string='Nomor Seri / Lot', domain="[('product_id','=',product_id)]")

    sale_order_id = fields.Many2one('sale.order', string='Sales Order', ondelete='cascade', tracking=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Baris Sales Order', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Pelanggan', required=True, tracking=True)

    date_start = fields.Date(string='Tanggal Mulai', required=True, default=fields.Date.context_today)
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
    claim_count = fields.Integer(string='Jumlah Klaim', compute='_compute_claim_count', store=True)
    
    notes = fields.Text(string='Catatan')

    @api.depends('date_start', 'duration_months')
    def _compute_date_end(self):
        for rec in self:
            if rec.date_start and rec.duration_months:
                rec.date_end = rec.date_start + relativedelta(months=rec.duration_months)
            else:
                rec.date_end = False
    
    @api.depends('date_end')
    def _compute_days_remaining(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_end:
                rec.days_remaining = (rec.date_end - today).days
            else:
                rec.days_remaining = 0

    @api.depends('claim_ids')
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
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('medical.warranty') or _('New')
            vals.setdefault('state', 'active')
        return super().create(vals_list)

    def action_active(self):
        self.write({'state': 'active'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
        
    def action_view_claims(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('medical_equipment_warranty.action_medical_warranty_claim')
        action['domain'] = [('warranty_id', '=', self.id)]
        action['context'] = {
            'default_warranty_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_product_id': self.product_id.id,
        }
        return action

    def action_print_warranty_card(self):
        return self.env.ref('medical_equipment_warranty.action_report_warranty_card').report_action(self)

    def _cron_check_expiry(self):
        today = fields.Date.context_today(self)
        expired = self.search([
            ('state', 'in', ('active', 'expiring')),
            ('date_end', '<', today),
        ])
        expired.write({'state': 'expired'})
        expiring_soon = self.search([
            ('state', '=', 'active'),
            ('date_end', '>=', today),
            ('date_end', '<=', today + relativedelta(days=30)),
        ])
        expiring_soon.write({'state': 'expiring'})

        template_30 = self.env.ref('medical_equipment_warranty.email_template_warranty_expires_30_days', raise_if_not_found=False)
        if template_30:
            to_notify_30 = self.search([
                ('state', '=', 'expiring'),
                ('notify_30_sent', '=', False),
                ('date_end', '<=', today + relativedelta(days=30)),
            ])
            for rec in to_notify_30:
                template_30.send_mail(rec.id, force_send=True)
            to_notify_30.write({'notify_30_sent': True})

        template_7 = self.env.ref('medical_equipment_warranty.email_template_warranty_expires_7_days', raise_if_not_found=False)
        if template_7:
            to_notify_7 = self.search([
                ('state', '=', 'expiring'),
                ('notify_7_sent', '=', False),
                ('date_end', '<=', today + relativedelta(days=7)),
            ])
            for rec in to_notify_7:
                template_7.send_mail(rec.id, force_send=True)
            to_notify_7.write({'notify_7_sent': True})

        return True
