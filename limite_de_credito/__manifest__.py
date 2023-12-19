{
    'name': 'Limite de credito a clientes con bloqueo en venta',
    'author': 'Jeffry',
    'category': 'Accounting',
    'version': '15.4.3.0',
    'description': """Limite de credito a clientes con bloqueo en venta""",
    'sequence': 11,
    'website': 'https://www.gader.cl',
    'depends': ['base','sale','contacts','account'],
    'license': 'LGPL-3',
    'data': [
        'views/res_partner.xml',
        'views/res_config_settings.xml',
        'views/account_move.xml',
        'views/sale_order.xml',
    ],
    'price': 10,
    'currency': 'USD',
    'installable': True,
}
