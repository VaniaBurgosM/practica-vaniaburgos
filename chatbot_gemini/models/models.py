# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class chatbot_gemini(models.Model):
#     _name = 'chatbot_gemini.chatbot_gemini'
#     _description = 'chatbot_gemini.chatbot_gemini'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

