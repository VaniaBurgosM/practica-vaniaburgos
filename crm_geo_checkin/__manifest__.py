# -*- coding: utf-8 -*-
{
    "name": "CRM Geo Check-In",
    "version": "1.0",
    "category": "CRM",
    "summary": "Registrar check-in georreferenciado en oportunidades",
    "description": """
Permite a los vendedores registrar un check-in geolocalizado directamente desde el formulario del lead (oportunidad). 
Guarda latitud, longitud, fecha/hora y calcula distancia al cliente.
""",
    "author": "Sellside Chile",
    "website": "https://sellside.cl",
    "license": "AGPL-3",
    "depends": ['base', 'web', 'crm', 'mail'],
    "data": [
        "views/crm_lead_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "crm_geo_checkin/static/src/js/geo_checkin.js",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}