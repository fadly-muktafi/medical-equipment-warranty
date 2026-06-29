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
        'security/ir.model.accesss.csv',
        'data/sequence-data.xml',
        'data/email-template.xml',
        'data/ir-cron.xml',
        'views/menu.xml',
        'views/medical-warranty-views.xml',
        'views/medical-warranty-claim-views.xml',
        'views/product-template-views.xml',
        'views/sale-order-views.xml',
        'views/sale-order-views.xml',
        'report/warranty-card-action.xml',
        'report/warranty-card-report.xml',
    ],
    'installable': True,
    'application': True,
}
