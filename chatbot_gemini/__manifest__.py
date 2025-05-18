{
    'name': "Agente IA Gemini",
    'summary': "Agente AI Gemini en Discuss",
    'description':"Agente de IA con API Gemini para integrar al módulo Discuss de Odoo.",
    'author': "VB",
    'website': "https://vaniaburgosm-practica-vaniaburgos-agente-ia-20490582.dev.odoo.com/odoo",

    'category': 'Tools',
    'version': '0.1',
    'depends': ['base', 'mail', 'discuss'],


    'data': [
        'security/ir.model.access.csv',
        'views/agente_ia_bot_view.xml',
    ],
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}