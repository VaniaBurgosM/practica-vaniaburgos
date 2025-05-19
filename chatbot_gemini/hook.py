from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    canal_model = env['discuss.channel']
    canal_model.crear_o_activar_canal_gemini()