from odoo import models, fields

class ProductStock(models.Model):
    _name = 'product.stock'
    _description = 'Stock de Productos'

    product_id = fields.Many2one('product.product', string="Producto", required=True)