# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrApplicantWorkourAvailable(models.Model):
    _name = "hr.applicant.workhour.available"
    _description = "Hr applicant workhour available"
    _order = "name"

    name = fields.Char("Name", required=True)
