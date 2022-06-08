# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context
from collections import defaultdict


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    nrp = fields.Boolean(string='NRP')
    nrp_previous_activity_type_id = fields.Many2one('mail.activity.type', string='NRP Previous Activity Type', readonly=True)
