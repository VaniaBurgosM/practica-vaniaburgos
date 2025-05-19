def set_password_post_init(cr, registry):
    from odoo.api import Environment
    env = Environment(cr, 1, {})
    user = env.ref('chatbot_gemini.gemini_ai_user')
    if user:
        user.sudo().write({'password': 'gemini_bot'})