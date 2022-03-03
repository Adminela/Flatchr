# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _


class HrRecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"

    is_create_project_task = fields.Boolean(string='Créer formation', tracking=True)
                