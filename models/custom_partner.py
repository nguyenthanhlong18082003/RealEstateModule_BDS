from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class CustomFriendPartner(models.Model):
    _name="custom.friend.partner"
    _description="Custom Partner for Add Friend"

    partner_id = fields.Many2one("res.partner","Partner ID")
    agency_id = fields.Char("Mã môi giới")
    name = fields.Char("Tên")
    phone = fields.Char("Số điện thoại")
    email = fields.Char("Email")

    def add_partner(self):
        partner_id_to_add = self.env.context.get("partner_id")
        partner = self.env['res.partner'].search([('id','=',partner_id_to_add)])
        self.env['sent.friend.request'].create({
            'sent_request': partner.id,
            'create_uid': self.env.user.id
        })
        self.env['friend.request'].create({
            'request_target': partner.id,
            'request_partner': self.env.user.partner_id.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Friend Request',
            'res_model': 'sent.friend.request',
            'domain': [('create_uid','=',self.env.user.id)],
            'view_mode': 'kanban',
            'target': 'current',
        }

    def view_partner(self):
        partner_id = self.env.context.get("partner_id")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact',
            'res_model': 'res.partner',
            'res_id': partner_id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def add_all_partners(self):
        users = self.env['res.users'].search([])
        sent_requests = self.env['sent.friend.request'].search([('create_uid', '=', self.env.user.id)])
        sent_requests = sent_requests.mapped('sent_request.id')
        current_partner = self.env.user.partner_id
        _logger.info("\n\n\n %s \n\n",current_partner.friend_partner_ids.ids)
        partner_ids = []
        for user in users:
            if (user.has_group("RealEstateModule_BDS.access_res_module_user")) and (user.partner_id.id not in current_partner.friend_partner_ids.ids) and (user.partner_id.id not in sent_requests) and (user.partner_id.id != current_partner.id):
                _logger.info("\n\n\n %s \n\n",user.partner_id.id)
                partner_ids.append(user.partner_id.id)

        partners = self.env['res.partner'].search([('id','in',partner_ids)])
        self.env['custom.friend.partner'].search([]).unlink()
        
        for partner in partners:
            existing = self.search([('partner_id', '=', partner.id)])
            if not existing:
                self.create({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                    'phone': partner.phone,
                    'agency_id': 'mg-' + str(partner.id)
                })
        return True

class CustomPartner(models.Model):
    _name="custom.partner"
    _description="Custom Partner for Add Partner"

    partner_id = fields.Many2one("res.partner","Partner ID")
    agency_id = fields.Char("Mã môi giới")
    name = fields.Char("Tên")
    phone = fields.Char("Số điện thoại")
    email = fields.Char("Email")

    def add_partner(self):
        partner_id_to_add = self.env.context.get("partner_id")
        partner = self.env['res.partner'].search([('id','=',partner_id_to_add)])
        self.env['sent.partner.request'].create({
            'sent_request': partner.id,
            'create_uid': self.env.user.id
        })
        self.env['partner.request'].create({
            'request_target': partner.id,
            'request_partner': self.env.user.partner_id.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Partner Request',
            'res_model': 'sent.partner.request',
            'domain': [('create_uid','=',self.env.user.id)],
            'view_mode': 'kanban',
            'target': 'current',
        }

    def view_partner(self):
        partner_id = self.env.context.get("partner_id")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact',
            'res_model': 'res.partner',
            'res_id': partner_id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def add_all_partners(self):
        users = self.env['res.users'].search([])
        sent_requests = self.env['sent.partner.request'].search([('create_uid', '=', self.env.user.id)])
        sent_requests = sent_requests.mapped('sent_request.id')
        current_partner = self.env.user.partner_id
        partner_ids = []
        for user in users:
            if (user.has_group("RealEstateModule_BDS.access_res_module_user")) and (user.partner_id.id not in current_partner.team_partner_ids.ids) and (user.partner_id.id in current_partner.friend_partner_ids.ids) and (user.partner_id.id not in sent_requests) and (user.partner_id.id != current_partner.id):
                partner_ids.append(user.partner_id.id)

        partners = self.env['res.partner'].search([('id','in',partner_ids)])
        self.env['custom.partner'].search([]).unlink()
        
        for partner in partners:
            existing = self.search([('partner_id', '=', partner.id)])
            if not existing:
                self.create({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                    'phone': partner.phone,
                    'agency_id': 'mg-' + str(partner.id)
                })
        return True

class CustomPartner(models.Model):
    _name="custom.team"
    _description="Custom Team for Add Team Partner"

    partner_id = fields.Many2one("res.partner","Partner ID")
    agency_id = fields.Char("Mã môi giới")
    name = fields.Char("Tên")
    phone = fields.Char("Số điện thoại")
    email = fields.Char("Email")

    def add_partner(self):
        partner_id_to_add = self.env.context.get("partner_id")
        partner = self.env['res.partner'].search([('id','=',partner_id_to_add)])
        self.env['sent.team.request'].create({
            'sent_request': partner.id,
            'create_uid': self.env.user.id
        })
        self.env['team.request'].create({
            'request_target': partner.id,
            'request_partner': self.env.user.partner_id.id
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Team Request',
            'res_model': 'sent.team.request',
            'domain': [('create_uid','=',self.env.user.id)],
            'view_mode': 'kanban',
            'target': 'current',
        }

    def view_partner(self):
        partner_id = self.env.context.get("partner_id")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Contact',
            'res_model': 'res.partner',
            'res_id': partner_id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def add_all_partners(self):
        users = self.env['res.users'].search([])
        sent_requests = self.env['sent.team.request'].search([('create_uid', '=', self.env.user.id)])
        sent_requests = sent_requests.mapped('sent_request.id')
        current_partner = self.env.user.partner_id
        partner_ids = []
        for user in users:
            if (user.has_group("RealEstateModule_BDS.access_res_module_user")) and (user.partner_id.id not in current_partner.team_partner_ids.ids) and (user.partner_id.id in current_partner.co_partner_ids.ids) and (user.partner_id.id not in sent_requests) and (user.partner_id.id != current_partner.id):
                partner_ids.append(user.partner_id.id)

        partners = self.env['res.partner'].search([('id','in',partner_ids)])
        self.env['custom.team'].search([]).unlink()
        
        for partner in partners:
            existing = self.search([('partner_id', '=', partner.id)])
            if not existing:
                self.create({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                    'phone': partner.phone,
                    'agency_id': 'mg-' + str(partner.id)
                })
        return True