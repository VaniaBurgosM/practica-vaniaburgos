# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class field_services_geo(models.Model):
#     _name = 'field_services_geo.field_services_geo'
#     _description = 'field_services_geo.field_services_geo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

