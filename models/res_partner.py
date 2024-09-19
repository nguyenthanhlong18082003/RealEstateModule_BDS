from odoo import _, models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"
    link_fb = fields.Char(string="Facebook Profile")
    link_zl = fields.Char(string="Partner Zalo")
    link_wa = fields.Char(string="Partner WhatApp")
    link_vb = fields.Char(string="Partner Viber")
    link_ms = fields.Char(string="Partner Messenger")

    cccd_nb = fields.Char(string="Số CMND / CCCD")

    sale_houses = fields.Many2many(
        "res.brokerage1",
        relation="partner_brokerage_rel",
        string="Nhà đất bán",
    )

    rent_house = fields.Many2many(
        "res.brokerage2",
        string="Nhà đất cho thuê",
    )

    state_sale_house = fields.Many2many(
        "res.brokerage3",
        string="Khu vực bán",
    )
    state_rent_house = fields.Many2many(
        "res.brokerage4",
        string="Khu vực thuê",
    )

    add_user_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="partner_partner_rel",
        column1="parent_partner_id",
        column2="child_partner_id",
        string="Users with Access",
    )

    class ResBrokerage1(models.Model):
        _name = "res.brokerage1"
        _description = "Brokerage 1"
        type_brokerage = fields.Char(string="Loại nhà bán", required=True)
        display_name = fields.Char(
            string="Display Name", compute="_compute_display_name", store=True
        )

        @api.depends("type_brokerage")
        def _compute_display_name(self):
            for record in self:
                record.display_name = record.type_brokerage


class ResBrokerage2(models.Model):
    _name = "res.brokerage2"
    _description = "Brokerage 2"
    type = fields.Char(string="Loại nhà thuê", required=True)
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )

    @api.depends("type")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.type


class ResBrokerage3(models.Model):
    _name = "res.brokerage3"
    _description = "Brokerage 3"
    type = fields.Char(string="Loại nhà bán", required=True)
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )

    @api.depends("type")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.type


class ResBrokerage4(models.Model):
    _name = "res.brokerage4"
    _description = "Brokerage 4"
    type = fields.Char(string="Loại nhà bán", required=True)
    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=True
    )

    @api.depends("type")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.type
