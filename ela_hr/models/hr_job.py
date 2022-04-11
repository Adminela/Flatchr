# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrJob(models.Model):
    _inherit = 'hr.job'

    active_ela = fields.Boolean(string='Active ELA', tracking=True, default=True)

    def set_inactive(self):
        for record in self:
            record.active_ela = False

    def set_active(self):
        for record in self:
            record.active_ela = True