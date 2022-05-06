# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrApplicantExperience(models.Model):
    _name = "hr.applicant.experience"
    _description = "Hr applicant experience"
    _order = "sequence, id"

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Séquence", defaut=1)
