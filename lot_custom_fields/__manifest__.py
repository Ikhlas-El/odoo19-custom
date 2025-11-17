{
    'name': "Stock Lot Custom Fields",
    'version': '1.0',
    'depends': ['base', 'stock','mrp'],
    'author': "Ikhlas",
    'category': 'Inventory',
    'description': """
        Adds custom fields to stock.production.lot.
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/stock_lot_views.xml',
        'views/report_lot_label_inherit.xml',
        'views/mrp_label_production_override.xml',
        'data/coffee_origin_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}