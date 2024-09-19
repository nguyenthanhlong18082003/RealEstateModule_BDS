from odoo import fields, models

class ResAgency(models.Model):
    _name = "res.agency"
    _description = "Real Estate Agency"

    name = fields.Char(string="Họ Tên")
    age = fields.Char(string="Tuổi")