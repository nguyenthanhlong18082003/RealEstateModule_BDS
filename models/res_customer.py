from odoo import fields, models

class ResCustomer(models.Model):
    _name = "res.customer"
    _description = "Khách hàng"

    name = fields.Char(string="Tên")