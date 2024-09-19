from odoo import models, fields

class ResCountryWard(models.Model):
    _name = 'res.country.ward'
    _description = 'Ward'

    name = fields.Char(string='Ward Name', required=True)
    district_id = fields.Many2one('res.country.district', string='District', required=True)
    code = fields.Char(string='Ward Code')
