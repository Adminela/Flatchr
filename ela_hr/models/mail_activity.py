# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    nrp = fields.Boolean(string='NRP', tracking=True)
    
    def action_done_NRP(self):
        self.nrp = True
        self.action_done()

    def _action_done(self, feedback=False, nrp=False, attachment_ids=None):
        #raise ValidationError("%s - %s" %(feedback, nrp))
        return super(MailActivity, self)._action_done(feedback, attachment_ids)