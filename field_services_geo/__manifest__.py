# -*- coding: utf-8 -*-
{
    'name': 'CRM Geo Checkin',

    'summary': 'Registro de check-in georreferenciado para vendedores en visitas a clientes desde CRM',

    'description': """
Este módulo permite a los vendedores registrar un check-in georreferenciado directamente desde su dispositivo móvil o navegador al visitar a un cliente. La ubicación capturada se almacena junto al registro del cliente en CRM, permitiendo verificar que la visita se realizó en el lugar correcto. Ideal para equipos de ventas en terreno.
""",

    'author': 'Sellside',
    'website': 'https://www.sellside.cl',

    'category': 'Sales/CRM',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['crm'],

    'data': [
        'security/ir.model.access.csv',
        'views/field_services_view.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'crm_geo_checkin/static/src/js/geo_checkin.js',
            'crm_geo_checkin/static/src/js/geo_checkin_hook.js',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}