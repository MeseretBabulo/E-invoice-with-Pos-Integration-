# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Pos Integration',
    'version': '1.0.1',
    'category': 'Sales/Point Of Sale',
    'sequence': 20,
    'summary': 'PoS api integration',
    'description': "",
    'author': "mesi2640@gmail.com",
    'images': ['static/images/addis-favicon.png'],
    'installable': True,
    'application': True,
    'depends': ['point_of_sale', 'stock_account', 'barcodes', 
                'purchase', 'sh_message', 'operating_unit'],
    'data': [
        'security/ir.model.access.csv',
        'views/posorder_view.xml',
        'views/pos_purchase_view.xml'

    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_integration/static/src/css/create_invoice.css',
            'pos_integration/static/src/js/create_invoice.js',
        ],
        'web.assets_qweb': [
            'pos_integration/static/src/view/create_invoice.xml',
            'pos_integration/static/src/view/QR.xml',

        ],
    },

}
