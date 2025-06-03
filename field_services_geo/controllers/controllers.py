# -*- coding: utf-8 -*-
# from odoo import http


# class FieldServicesGeo(http.Controller):
#     @http.route('/field_services_geo/field_services_geo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/field_services_geo/field_services_geo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('field_services_geo.listing', {
#             'root': '/field_services_geo/field_services_geo',
#             'objects': http.request.env['field_services_geo.field_services_geo'].search([]),
#         })

#     @http.route('/field_services_geo/field_services_geo/objects/<model("field_services_geo.field_services_geo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('field_services_geo.object', {
#             'object': obj
#         })

