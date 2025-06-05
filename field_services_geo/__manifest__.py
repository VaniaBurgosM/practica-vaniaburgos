# __manifest__.py
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
    'depends': ['project', 'industry_fsm', 'web'], # Asegúrate de que 'web' esté aquí
    'data': [
        'security/ir.model.access.csv',
        'views/field_services_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'field_services_geo/static/src/components/geo_checkin_widget/geo_checkin_widget.js', # Cargar el componente JS
            'field_services_geo/static/src/components/geo_checkin_widget/geo_checkin_widget.xml', # Cargar la plantilla Owl
            'field_services_geo/static/src/js/field_services.js', # Cargar el archivo de registro del widget (el que usa field_registry)
        ],
    },
    'installable': True,
    'application': False,
}