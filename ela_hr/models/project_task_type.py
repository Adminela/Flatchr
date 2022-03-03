# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    is_move_applicant_hr = fields.Boolean(string='Déplacer à l\'étape RH', tracking=True)
