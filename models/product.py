# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import requests
from odoo import _, models, fields, api
from odoo.http import request
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"
    pr_status = fields.Selection(
        [
            ("sel_4", "Không"),
            ("sel_1", "Có sẵn"),
            ("sel_2", "Đã đặt cọc"),
            ("sel_3", "Đã bán"),
        ],
        string="Trạng thái",
        default="sel_4",
    )
    h_o_c_seri = fields.Char(
        string="Số seri sổ hồng"
    )  # h_o_c = House ownership certificate
    is_standard = fields.Boolean(default=True, string="Cam kết đạt chuẩn")
    acreage = fields.Float(string="Diện tích")
    real_acreage = fields.Float(string="Diện tích thực tế")
    is_owner = fields.Boolean(string="Sản phẩm đầu chủ", default=True, readonly=True)
    juridical = fields.Text(string="Pháp lý")
    alley = fields.Char(string="Ngõ, số nhà")
    street = fields.Char(string="Đường phố")
    street2 = fields.Char(string="Đường phố 2") 
    ward = fields.Char(string="Phường xã")
    district = fields.Char(string="Quận huyện")
    city = fields.Char(string="Thành phố")
    state_id = fields.Many2one(comodel_name="res.country.state")
    country_id = fields.Many2one(
        comodel_name="res.country", default=lambda self: self.env.ref("base.vn")
    )

    # Trường để lưu ID của sản phẩm cha
    parent_product_id = fields.Many2one(
        "product.template", string="Parent Product", readonly=True
    )

    # Trường để lưu IDs của các sản phẩm con
    child_product_ids = fields.One2many(
        "product.template", "parent_product_id", string="Child Products", readonly=True
    )
    
    child_partner_ids = fields.Many2many(
        comodel_name="res.partner",  # model liên kết là res.partner
        relation="product_template_partner_rel",  # tên bảng quan hệ trong cơ sở dữ liệu
        column1="product_id",  # tên cột trong bảng quan hệ cho product.template
        column2="partner_id",  # tên cột trong bảng quan hệ cho res.partner
        string="Users with Access",
    )
    rs_status = fields.Boolean(string="Cam kết đạt chuẩn trạng thái")
    balcony = fields.Integer(string="Số ban công")
    offer_price = fields.Float(string="Giá chào hợp đồng (Triệu VND)")
    close_price = fields.Float(string="Giá chốt (Triệu VND)")
    direction_id = fields.Many2one("product.direction", string="Hướng nhà")

    product_type_id = fields.Many2one("product.type", string="Loại bất động sản")

    nums_bedrooms = fields.Integer(string="Số phòng ngủ")
    nums_bath = fields.Integer(string="Số nhà vệ sinh")
    facade = fields.Float(string="Mặt tiền (m)")
    real_length = fields.Float(string="Chiều dài (m)")
    bonus_money = fields.Float(string="Hoa hồng (Triệu VND)")
    bonus_money_percent = fields.Float(string="Hoa hồng %")
    way_in = fields.Integer(string="Ngõ vào (m)")
    floors = fields.Integer(string="Số Tầng")
    interior = fields.Text(string="Nội thất")

    district_id = fields.Many2one("res.country.district", string="District")
    ward_id = fields.Many2one("res.country.ward", string="Ward")
    sell_name = fields.Char(string="Tên chủ nhà")
    sell_phone = fields.Char(string="Điện thoại chủ nhà")
    contract = fields.Many2one("res.partner", string="Hợp đồng")

    activity_user_id = fields.Many2one(comodel_name='res.partner', readonly=True, store=True, auth='public')
    # Tài khoản liên kết
    supp_fb = fields.Char(string="Facebook")

    supp_zl = fields.Char(string="Zalo")

    supp_wa = fields.Char(string="WhatApp")

    supp_vb = fields.Char(string="Viber")

    supp_ms = fields.Char(string="Messenger")

    btn_options = fields.Selection(
        [
            ("PopUp", "PopUp"),
            ("Section", "Section"),
        ],
        string="Form type",
        default="PopUp",
    )
    form_model_name = fields.Selection(
        [("crm.lead", "Create an Opportunity"), ("mail.mail", "Send an E-mail")],
        string="Form model",
        default="crm.lead",
    )

    @api.onchange("state_id")
    def _onchange_state_id(self):
        self.district_id = False
        self.ward_id = False

    @api.onchange("district_id")
    def _onchange_district_id(self):
        self.ward_id = False

    @api.model
    def duplicate_product(self, record_id):
        # Lấy thông tin sản phẩm gốc (cha)
        parent_product = self.env["product.template"].browse(record_id)

        # Tạo sản phẩm mới với thông tin từ sản phẩm gốc
        new_product_vals = {
            'name': parent_product.name,
            'list_price': parent_product.list_price,
            'is_owner': False,
            'image_1920': parent_product.image_1920,
            'parent_product_id': parent_product.id,  # Gán parent_product_id của sản phẩm mới là ID của sản phẩm cha
            'acreage': parent_product.acreage,
            'real_acreage': parent_product.real_acreage,
            'juridical': parent_product.juridical,
            'alley': parent_product.alley,
            'street': parent_product.street,
            'street2': parent_product.street2,
            'ward': parent_product.ward,
            'ward_id': parent_product.ward_id.id if parent_product.ward_id else False,  # Sử dụng ID
            'district': parent_product.district,
            'district_id': parent_product.district_id.id if parent_product.district_id else False,  # Sử dụng ID
            'city': parent_product.city,
            'state_id': parent_product.state_id.id if parent_product.state_id else False,  # Sử dụng ID
            'country_id': parent_product.country_id.id if parent_product.country_id else False,  # Sử dụng ID
            'rs_status': parent_product.rs_status,
            'balcony': parent_product.balcony,
            'offer_price': parent_product.offer_price,
            'close_price': parent_product.close_price,
            'direction_id': parent_product.direction_id.id if parent_product.direction_id else False,  # Sử dụng ID
            'product_type_id': parent_product.product_type_id.id if parent_product.product_type_id else False,  # Sử dụng ID
            'nums_bedrooms': parent_product.nums_bedrooms,
            'nums_bath': parent_product.nums_bath,
            'facade': parent_product.facade,
            'real_length': parent_product.real_length,
            'bonus_money': parent_product.bonus_money,
            'bonus_money_percent': parent_product.bonus_money_percent,
            'way_in': parent_product.way_in,
            'interior': parent_product.interior,
            'sell_name': parent_product.sell_name,
            'sell_phone': parent_product.sell_phone,
            'contract': parent_product.contract,   
        }

        # Tạo sản phẩm mới
        new_product = self.env["product.template"].sudo().create(new_product_vals)

        # Cập nhật trường child_product_ids của sản phẩm cha với ID của sản phẩm mới
        parent_product.write({'child_product_ids': [(4, new_product.id)]})
        create_uid_id = new_product.create_uid.partner_id.id
        new_product.write({'activity_user_id': create_uid_id})
        return new_product

    def action_open_parent_product(self):
        self.ensure_one()  # Chỉ làm việc với một bản ghi
        if self.parent_product_id:
            return {
                "type": "ir.actions.act_window",
                "name": "Parent Product",
                "res_model": "product.template",
                "view_mode": "form",
                "res_id": self.parent_product_id.id,
                "target": "current",
            }

    def action_publish(self):
        for record in self:
            record.is_published = True

    @api.model
    def get_user_domain(self):
        user = self.env.user
        partner_id = user.partner_id.id
        return [('is_owner', '=', True), ('child_partner_ids', 'in', [partner_id])]

    def check_access_rule(self, operation):
        try:
            # Kiểm tra xem operation có phải là 'read' và context của request có chứa 'check_child_partner_ids' hay không
            if operation == 'read' and self.env.context.get('check_child_partner_ids'):
                # Kiểm tra xem người dùng hiện tại có phải là thành viên của nhóm 'base.group_user' (nhóm người dùng thông thường) hay không
                is_admin = self.env.user.has_group('base.group_user')
                # Nếu người dùng không phải là thành viên của nhóm 'base.group_user'
                if not is_admin:
                    # Lấy ID của partner liên kết với người dùng hiện tại
                    user_partner_id = self.env.user.partner_id.id
                    # Tìm ra danh sách các product IDs mà người dùng được phép truy cập, dựa trên việc partner của người dùng được liên kết với các product
                    allowed_product_ids = self.search([('child_partner_ids', 'in', user_partner_id)]).ids
                    # Kiểm tra xem các product IDs mà người dùng đang cố gắng truy cập có nằm trong danh sách các product được phép truy cập hay không
                    if not set(self.ids).issubset(set(allowed_product_ids)):
                        # Nếu không, raise một AccessError để ngăn chặn việc truy cập
                        raise AccessError("You do not have access to view this product.")
            # Gọi đến super().check_access_rule(operation) để tiếp tục kiểm tra các quyền truy cập khác
            return super(ProductTemplateInherit, self).check_access_rule(operation)
        except Exception as e:
            # Nếu có bất kỳ exception nào xảy ra, log lại và raise lại exception đó
            self._log_error(str(e))
            raise

    def read(self, fields=None, load='_classic_read'):
        try:
            # Kiểm tra xem người dùng có phải là quản trị viên không
            if self.env.user.has_group('base.group_system'):
                # Nếu là quản trị viên, trả về tất cả các sản phẩm
                return super(ProductTemplateInherit, self).read(fields=fields, load=load)
            # Kiểm tra xem có cần phải kiểm tra quyền truy cập hay không
            elif 'check_child_partner_ids' in self.env.context:
                # Lấy ID đối tác của người dùng hiện tại
                user_partner_id = self.env.user.partner_id.id

                # Tìm các sản phẩm mà người dùng có quyền truy cập
                allowed_product_ids = self.search([('child_partner_ids', 'in', [user_partner_id])]).ids

                # Chỉ trả về các bản ghi có ID nằm trong danh sách các sản phẩm được phép
                return super(ProductTemplateInherit, self.filtered(lambda r: r.id in allowed_product_ids)).read(fields=fields, load=load)
            else:
                # Không cần kiểm tra quyền truy cập, trả về dữ liệu bình thường
                return super(ProductTemplateInherit, self).read(fields=fields, load=load)
        except Exception as e:
            self._log_error(e)
            raise

