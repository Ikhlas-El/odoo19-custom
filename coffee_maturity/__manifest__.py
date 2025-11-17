{
    'name': "Coffee Maturity Tracking",
    'version': '1.0',
    'depends': ['stock', 'mrp'],
    'category': 'Inventory',
    'summary': "Tracks coffee maturity duration from MO finish date",
    'data': [
        'views/stock_production_lot_views.xml',
        'data/category_data.xml',
    ],
    'installable': True,
    'application': False,
}
