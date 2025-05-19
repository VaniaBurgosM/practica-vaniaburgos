from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    group_public = env.ref('base.group_public')

    canal_model = env['discuss.channel']
    canal = canal_model.search([('name', '=', 'Asistente IA Gemini')], limit=1)
    if not canal:
        canal_model.create({
            'name': 'Asistente IA Gemini',
            'channel_type': 'channel',
            'group_public_id': group_public.id,
            'is_gemini_enabled': True,
        })

    else:
        if not canal.is_gemini_enabled:
            canal.write({'is_gemini_enabled': True})