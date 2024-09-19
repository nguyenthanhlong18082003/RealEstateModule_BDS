from odoo import fields, models, api
import logging
from odoo.http import request

_logger = logging.getLogger(__name__)

class FriendPartnerDetails(models.Model):
    _inherit = "res.partner"

    friend_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="friend_partner_rel",
        column1="parent_partner_id",
        column2="child_partner_id",
        string="Friend",
        ondelete="cascade"
    )

    co_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="co_partner_rel",
        column1="parent_partner_id",
        column2="child_partner_id",
        string="Co-Partner",
        # domain="[('id', 'in', friend_partner_ids)]",
        ondelete="cascade"
    )

    team_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="team_partner_rel",
        column1="parent_partner_id",
        column2="child_partner_id",
        string="Team",
        # domain="[('id', 'in', co_partner_ids)]",
        ondelete="cascade",
    )

    def unlink_partner(self):
        id = self.env.context.get("remove_partner_id")
        type = self.env.context.get("partner_type")
        user = self.env['res.users'].sudo().search(
            [('id','=',self.env.user.id)]
        )
        exist_in_co_partner = id in user.co_partner_ids.ids
        exist_in_team = id in user.team_partner_ids.ids
        # remove but dont delete record
        if type == "friend":
            user.write({
                'friend_partner_ids': [(3, id)],
                'co_partner_ids': [(3, id)] if exist_in_co_partner else [],
                'team_partner_ids': [(3, id)] if exist_in_team else [],
            })
        elif type == "co_partner":
            user.write({
                'co_partner_ids': [(3, id)] if exist_in_co_partner else [],
                'team_partner_ids': [(3, id)] if exist_in_team else [],
            })
        elif type == "team":
            user.write({
                'team_partner_ids': [(3, id)] if exist_in_team else [],
            })

        partner = self.env['res.users'].sudo().search(
            [('partner_id','=',id)]
        )
        _logger.info("\n\n\n<<<<<<<< %s >>>>>>>>\n\n",user.partner_id.id)
        exist_in_co_partner = user.partner_id.id in partner.co_partner_ids.ids
        exist_in_team = user.partner_id.id in partner.team_partner_ids.ids
        # remove but dont delete record
        if type == "friend":
            partner.write({
                'friend_partner_ids': [(3, user.partner_id.id)],
                'co_partner_ids': [(3, user.partner_id.id)] if exist_in_co_partner else [],
                'team_partner_ids': [(3, user.partner_id.id)] if exist_in_team else [],
            })
        elif type == "co_partner":
            partner.write({
                'co_partner_ids': [(3, user.partner_id.id)] if exist_in_co_partner else [],
                'team_partner_ids': [(3, user.partner_id.id)] if exist_in_team else [],
            })
        elif type == "team":
            partner.write({
                'team_partner_ids': [(3, user.partner_id.id)] if exist_in_team else [],
            })
        return self.show_partner_list()

    def get_partner_domain(self,type):
        partner = self.env['res.partner'].browse(self.env.user.partner_id.id)
        partner_ids = []
        partner_list = []
        if type == "friend":
            partner_list = partner.friend_partner_ids.ids
        elif type == "co_partner":
            partner_list = partner.co_partner_ids.ids
        elif type == "team":
            partner_list = partner.team_partner_ids.ids

        for partner_id in partner_list:
            partner_ids.append(partner_id)
        domain = [('id','in',partner_ids)]
        return domain

    @api.model
    def show_partner_list(self):
        partner_type = self.env.context.get("partner_type","")
        action = {}
        if partner_type == "friend":
            action = self.show_friend_list()
        elif partner_type == "co_partner":
            action = self.show_co_partner_list()
        elif partner_type == "team":
            action = self.show_team_list()
        return action

    @api.model
    def show_friend_list(self):
        context = {"partner_type": "friend"}
        view_kanban_id = self.env.ref('base.res_partner_kanban_view').id
        view_tree_id = self.env.ref('base.view_partner_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
        }
        action.update({
            'name': 'Bạn Bè',
            'view_mode': 'kanban,tree',
            'views': [[view_kanban_id, 'kanban'], [view_tree_id, 'tree']],
            'domain': self.get_partner_domain("friend"),
            'context': context
        })
        return action

    @api.model    
    def show_co_partner_list(self):
        context = {"partner_type": "co_partner"}
        view_kanban_id = self.env.ref('base.res_partner_kanban_view').id
        view_tree_id = self.env.ref('base.view_partner_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
        }
        action.update({
            'name': 'Đối Tác',
            'view_mode': 'kanban,tree',
            'views': [[view_kanban_id, 'kanban'], [view_tree_id, 'tree']],
            'domain': self.get_partner_domain("co_partner"),
            'context': context
        })
        return action

    @api.model    
    def show_team_list(self):
        context = {"partner_type": "team"}
        view_kanban_id = self.env.ref('base.res_partner_kanban_view').id
        view_tree_id = self.env.ref('base.view_partner_tree').id
        action = {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
        }
        action.update({
            'name': 'Công Ty',
            'view_mode': 'kanban,tree',
            'views': [[view_kanban_id, 'kanban'], [view_tree_id, 'tree']],
            'domain': self.get_partner_domain("team"),
            'context': context
        })
        return action
        