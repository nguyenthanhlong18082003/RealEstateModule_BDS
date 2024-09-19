from odoo import models, fields

class Cart(models.Model):
    _name = 'res.cart'
    _description = 'Giỏ hàng'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string="Image", attachment=True)
