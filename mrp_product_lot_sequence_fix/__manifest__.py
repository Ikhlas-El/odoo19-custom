
{
    'name': 'MRP Product Lot Sequence Fix',
    'version': '1.0',
    'category': 'Manufacturing',
    'summary': 'Use product lot sequence in Manufacturing Orders',
    'description': """
        This module ensures that when generating lots from Manufacturing Orders,
        the product's lot sequence (from OCA product_lot_sequence) is used
        instead of the global lot generation policy.
    """,
    'license': 'LGPL-3',
    'depends': [
        'mrp',
        'stock',
        'product_lot_sequence',
    ],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}