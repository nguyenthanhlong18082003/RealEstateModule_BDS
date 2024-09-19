from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)
class SentFriendRequest(models.Model):
    _name = "sent.friend.request"
    _description = "Sent Friend Request Manager"
    
    sent_request = fields.Many2one( # User mà bản thân đang yêu cầu kết bạn
        comodel_name="res.partner",
        string="Send Friend Request",
        ondelete="cascade",
        required=True
    )

    def cancel_request(self):
        request_id = self.env.context.get("sent_request_id")
        current_partner = self.env.user.partner_id
        for request in self:
            if request.id == request_id:
                friend_request = self.env['friend.request'].sudo().search([('request_target','=',request.sent_request.id),('request_partner','=',current_partner.id)])
                friend_request.unlink()
                request.unlink()

class FriendRequest(models.Model):
    _name = "friend.request"
    _description = "Friend Request Manager"
    
    request_target = fields.Many2one(
        comodel_name="res.partner",
        string="Friend Request",
        ondelete="cascade",
        required=True
    )

    request_partner = fields.Many2one(
        comodel_name="res.partner",
        string="Request User",
        ondelete="cascade",
        required=True
    )

    def get_domain(self):
        domain =[('request_target','=',self.env.user.partner_id.id)]
        return domain

    @api.model
    def show_list(self):
        context = {}
        view_kanban_id = self.env.ref('RealEstateModule_BDS.custom_friend_request_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'friend.request',
        }
        action.update({
            'name': 'Friend Request',
            'view_mode': 'kanban',
            'views': [[view_kanban_id, 'kanban']],
            'domain': [('request_target','=',self.env.user.partner_id.id)],
            'context': context
        })
        return action

    def accept_request(self):
        request_id = self.env.context.get("request_id")
        for request in self:
            if request.id == request_id:
                targetUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_target.id)]
                )
                requestUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_partner.id)]
                )
                targetUser.write({'friend_partner_ids': [(4, requestUser.id)]})
                requestUser.write({'friend_partner_ids': [(4, targetUser.id)]})
                
                sent_request_user = self.env['res.users'].sudo().search(
                    [('partner_id','=',request.request_partner.id)]
                )
                sent_request = self.env['sent.friend.request'].sudo().search(
                    [('create_uid','=',sent_request_user.id),('sent_request','=',targetUser.id)]
                )
                sent_request.unlink()
                request.unlink()
        return self.show_list()

    def reject_request(self):
        request_id = self.env.context.get("request_id")
        target_user = None
        request_user = None
        for request in self:
            if request.id == request_id:
                target_user = request.request_target.user_id
                request_user = request.request_partner.user_id

                sent_request_user = self.env['res.users'].sudo().search(
                    [('partner_id','=',request.request_partner.id)]
                )
                targetUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_target.id)]
                )
                sent_request = self.env['sent.friend.request'].sudo().search(
                    [('create_uid','=',sent_request_user.id),('sent_request','=',targetUser.id)]
                )
                sent_request.unlink()
                request.unlink()
        if target_user:
            self.send_message_to_user(target_user,f'{request_user} đã từ chối kết bạn')

    def send_message_to_user(self, user_id, message_body):

        # Find the target user
        user = self.env['res.users'].browse(user_id)

        # Create the message
        message = f"**Message from OdooBot:**\n{message_body}"

        # Send the message to the user
        user.partner_id.message_post(
            body=message,
            author_id=self.env.ref('base.user_root').id,  # Or use the OdooBot user ID
            message_type='comment',
            subtype_id=self.env.ref('mail.mt_comment').id
        )

class SentPartnerRequest(models.Model):
    _name = "sent.partner.request"
    _description = "Sent Partner Request Manager"
    
    sent_request = fields.Many2one( # Danh sách những người bản thân đang yêu cầu kết bạn
        comodel_name="res.partner",
        string="Send Partner Request",
        ondelete="cascade",
        required=True
    )

    def cancel_request(self):
        request_id = self.env.context.get("sent_request_id")
        current_partner = self.env.user.partner_id
        for request in self:
            if request.id == request_id:
                partner_request = self.env['partner.request'].sudo().search([('request_target','=',request.sent_request.id),('request_partner','=',current_partner.id)])
                partner_request
                request.unlink()

class PartnerRequest(models.Model):
    _name = "partner.request"
    _description = "Partner Request Manager"
    
    request_target = fields.Many2one(
        comodel_name="res.partner",
        string="Partner Request",
        ondelete="cascade",
        required=True
    )

    request_partner = fields.Many2one(
        comodel_name="res.partner",
        string="Request User",
        ondelete="cascade",
        required=True
    )

    def get_domain(self):
        domain =[('request_target','=',self.env.user.partner_id.id)]
        return domain

    @api.model
    def show_list(self):
        context = {}
        view_kanban_id = self.env.ref('RealEstateModule_BDS.custom_partner_request_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'partner.request',
        }
        action.update({
            'name': 'Partner Request',
            'view_mode': 'kanban',
            'views': [[view_kanban_id, 'kanban']],
            'domain': [('request_target','=',self.env.user.partner_id.id)],
            'context': context
        })
        return action

    def accept_request(self):
        request_id = self.env.context.get("request_id")
        for request in self:
            if request.id == request_id:
                targetUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_target.id)]
                )
                requestUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_partner.id)]
                )
                targetUser.write({'co_partner_ids': [(4, requestUser.id)]})
                requestUser.write({'co_partner_ids': [(4, targetUser.id)]})
                
                sent_request_user = self.env['res.users'].sudo().search(
                    [('partner_id','=',request.request_partner.id)]
                )
                sent_request = self.env['sent.partner.request'].sudo().search(
                    [('create_uid','=',sent_request_user.id),('sent_request','=',targetUser.id)]
                )
                sent_request.unlink()
                request.unlink()
        return self.show_list()

    def reject_request(self):
        request_id = self.env.context.get("request_id")
        target_user = None
        request_user = None
        for request in self:
            if request.id == request_id:
                target_user = request.request_target.user_id
                request_user = request.request_partner.user_id

                sent_request_user = self.env['res.users'].sudo().search(
                    [('partner_id','=',request.request_partner.id)]
                )
                targetUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_target.id)]
                )
                sent_request = self.env['sent.partner.request'].sudo().search(
                    [('create_uid','=',sent_request_user.id),('sent_request','=',targetUser.id)]
                )
                sent_request.unlink()
                request.unlink()

class SentTeamRequest(models.Model):
    _name = "sent.team.request"
    _description = "Sent Team Request Manager"
    
    sent_request = fields.Many2one( # Danh sách những người bản thân đang yêu cầu kết bạn
        comodel_name="res.partner",
        string="Send Team Request",
        ondelete="cascade",
        required=True
    )

    def cancel_request(self):
        request_id = self.env.context.get("sent_request_id")
        current_partner = self.env.user.partner_id
        for request in self:
            if request.id == request_id:
                partner_request = self.env['team.request'].sudo().search([('request_target','=',request.sent_request.id),('request_partner','=',current_partner.id)])
                partner_request
                request.unlink()

class TeamRequest(models.Model):
    _name = "team.request"
    _description = "Team Request Manager"
    
    request_target = fields.Many2one(
        comodel_name="res.partner",
        string="Team Request",
        ondelete="cascade",
        required=True
    )

    request_partner = fields.Many2one(
        comodel_name="res.partner",
        string="Request User",
        ondelete="cascade",
        required=True
    )

    def get_domain(self):
        domain =[('request_target','=',self.env.user.partner_id.id)]
        return domain

    @api.model
    def show_list(self):
        context = {}
        view_kanban_id = self.env.ref('RealEstateModule_BDS.custom_team_request_form_view').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'team.request',
        }
        action.update({
            'name': 'Team Request',
            'view_mode': 'kanban',
            'views': [[view_kanban_id, 'kanban']],
            'domain': [('request_target','=',self.env.user.partner_id.id)],
            'context': context
        })
        return action

    def accept_request(self):
        request_id = self.env.context.get("request_id")
        for request in self:
            if request.id == request_id:
                targetUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_target.id)]
                )
                requestUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_partner.id)]
                )
                targetUser.write({'team_partner_ids': [(4, requestUser.id)]})
                requestUser.write({'team_partner_ids': [(4, targetUser.id)]})
                
                sent_request_user = self.env['res.users'].sudo().search(
                    [('partner_id','=',request.request_partner.id)]
                )
                sent_request = self.env['sent.team.request'].sudo().search(
                    [('create_uid','=',sent_request_user.id),('sent_request','=',targetUser.id)]
                )
                sent_request.unlink()
                request.unlink()
        return self.show_list()

    def reject_request(self):
        request_id = self.env.context.get("request_id")
        target_user = None
        request_user = None
        for request in self:
            if request.id == request_id:
                target_user = request.request_target.user_id
                request_user = request.request_partner.user_id

                sent_request_user = self.env['res.users'].sudo().search(
                    [('partner_id','=',request.request_partner.id)]
                )
                targetUser = self.env['res.partner'].sudo().search(
                    [('id','=',request.request_target.id)]
                )
                sent_request = self.env['sent.team.request'].sudo().search(
                    [('create_uid','=',sent_request_user.id),('sent_request','=',targetUser.id)]
                )
                sent_request.unlink()
                request.unlink()