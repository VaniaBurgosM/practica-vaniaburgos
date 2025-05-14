from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    stock_level = fields.Float(string = "Nivel de Stock", compute = '_compute_stock_level')

#Método:
    def _compute_stock_level(self):
        for product in self:
            product.stock_level = sum(product.stock_quant_ids.mapped('quantity'))

