from odoo import SUPERUSER_ID

def set_password_post_init(cr, registry):
    from odoo.api import Environment
    env = Environment(cr, SUPERUSER_ID, {})
    user = env.ref('chatbot_gemini.gemini_ai_user', raise_if_not_found=False)
    if user:
        user.sudo().write({'password': 'gemini_bot'})