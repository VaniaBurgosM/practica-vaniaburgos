{
    'name': "Agente IA Gemini",
    'summary': "Agente AI Gemini en Discuss",
    'description':"Agente de IA con API Gemini para integrar al módulo Discuss de Odoo.",
    'author': "VB",
    'website': "https://vaniaburgosm-practica-vaniaburgos-agente-ia-20490582.dev.odoo.com/odoo",

    'category': 'Tools',
    'version': '0.1',
    'depends': ['base', 'mail'],


    'data': [
        'security/ir.model.access.csv',
        'data/agente_ia_bot.xml',
        'views/discuss_channel_views.xml'
    ],

    'post_init_hook': 'post_init_hook',

    # 'demo': [
    #     'demo/demo.xml',
    # ], 
}