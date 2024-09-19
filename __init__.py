# Part of Odoo. See LICENSE file for full copyright and licensing details.
from . import models
from . import controllers
from . import hooks

from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    env['custom.friend.partner'].add_all_partners()