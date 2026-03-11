# -*- coding: utf-8 -*-
{
    'name': 'Odoo Fût Module',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Gestion des fûts dans les ordres de fabrication',
    'depends': [
        'mrp',
        'product',
        'hr',
        'mrp_production_responsable',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/mrp_production_views.xml',
        'report/report_fut_etiquette.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}