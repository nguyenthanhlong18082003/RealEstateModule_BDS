from odoo import _, models, fields, api
class CustomConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_type_id = fields.Many2one('product.type', string='Product Type')
    product_direction_id = fields.Many2one('product.direction', string='Product Direction')
    # Add other fields as needed
