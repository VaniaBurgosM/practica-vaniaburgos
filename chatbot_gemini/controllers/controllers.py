# -*- coding: utf-8 -*-
# from odoo import http


# class ChatbotGemini(http.Controller):
#     @http.route('/chatbot_gemini/chatbot_gemini', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/chatbot_gemini/chatbot_gemini/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('chatbot_gemini.listing', {
#             'root': '/chatbot_gemini/chatbot_gemini',
#             'objects': http.request.env['chatbot_gemini.chatbot_gemini'].search([]),
#         })

#     @http.route('/chatbot_gemini/chatbot_gemini/objects/<model("chatbot_gemini.chatbot_gemini"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('chatbot_gemini.object', {
#             'object': obj
#         })

