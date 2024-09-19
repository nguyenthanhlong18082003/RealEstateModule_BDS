from odoo import models, fields

class Direction(models.Model):
    _name = 'product.direction'
    _description = 'Direction'

    name = fields.Char(string='Name', required=True)
    image = fields.Binary(string="Image", attachment=True)
