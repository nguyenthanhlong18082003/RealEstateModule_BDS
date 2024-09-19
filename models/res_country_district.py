from odoo import models, fields

class ResCountryDistrict(models.Model):
    _name = 'res.country.district'
    _description = 'District'

    name = fields.Char(string='District Name', required=True)
    state_id = fields.Many2one('res.country.state', string='State', required=True)
    code = fields.Char(string='District Code')
