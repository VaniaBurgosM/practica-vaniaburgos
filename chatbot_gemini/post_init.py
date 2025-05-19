from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    group_public = env.ref('base.group_public')  # grupo público estándar de Odoo

    canal_model = env['discuss.channel']
    canal = canal_model.search([('name', '=', 'Canal del Chatbot')], limit=1)
    if not canal:
        canal_model.create({
            'name': 'Canal del Chatbot',
            'channel_type': 'channel',
            'group_public_id': group_public.id,
        })