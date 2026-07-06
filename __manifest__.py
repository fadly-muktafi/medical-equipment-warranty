{
    'name': 'Medical Equipment Warranty & Certification Manager',
    'version': '19.0.1.0.0',
    'category': 'Medical',
    'summary': 'Manajemen Garansi Alat Kesehatan, Serial Number & Sertifikasi',
    'author': 'Ahmad Fadly Muktafi',
    'depends': [
        'sale_management', 'stock', 'product', 'mail'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/email_template_data.xml',
        'data/ir_cron_data.xml',
        'report/warranty_card_template.xml',
        'report/warranty_card_report.xml',
        'views/medical_warranty_views.xml',
        'views/medical_warranty_claim_views.xml',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
