from odoo import models, fields

class StockLocation(models.Model):
    _inherit = 'stock.location'
    _description = 'Ubicación del Stock'

    location_type = fields.Selection([
        ('internal', 'Interna'),
        ('transit', 'Tránsito'),
        ('inventory', 'Inventario'),
    ], string="Tipo de Ubicación", default='internal')
    
    description = fields.Text(string="Descripción")

    # Relación con movimientos de stock
    stock_move_ids = fields.One2many('stock.move', 'source_location_id', string="Movimientos del Stock desde esta Ubicación")


class StockMove(models.Model):
    _inherit = 'stock.move'
    _description = 'Movimiento del Stock'

    product_id = fields.Many2one('product.product', string="Producto", required=True)
    source_location_id = fields.Many2one('stock.location', string="Ubicación de Origen")
    destination_location_id = fields.Many2one('stock.location', string="Ubicación de Destino")
    quantity = fields.Float(string="Cantidad")
    move_date = fields.Datetime(string="Fecha de Movimiento", default=fields.Datetime.now)
    move_type = fields.Selection([('in', 'Entrada'), ('out', 'Salida')], string="Tipo de Movimiento")

class StockAdjustment(models.Model):
    _name = 'stock.adjustment'
    _description = 'Ajuste del Stock'

    adjustment_reason = fields.Text(string="Razón del Ajuste")
    location_id = fields.Many2one('stock.location', string="Ubicación del Stock", required=True)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('done', 'Hecho'),
        ('cancel', 'Cancelado'),
    ], string='Estado', default='draft')

    adjustment_date = fields.Datetime(string="Fecha de Ajuste", default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="Usuario", default=lambda self: self.env.user)

    product_id = fields.Many2one('product.product', string="Producto")
    adjusted_quantity = fields.Float(string="Cantidad Ajustada")
    quantity_before_adjustment = fields.Float(string="Cantidad Antes del Ajuste")
    quantity_after_adjustment = fields.Float(string="Cantidad Después del Ajuste")

    def confirm_adjustment(self):
        self.state = 'done'

