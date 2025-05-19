from odoo import SUPERUSER_ID

def set_password_post_init(env):
    user = env.ref('chatbot_gemini.gemini_ai_user', raise_if_not_found=False)
    if user:
        user.sudo().write({'password': 'gemini_bot'})