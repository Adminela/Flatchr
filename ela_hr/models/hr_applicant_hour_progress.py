# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from datetime import date

class HrApplicantHourProgress(models.Model):
    _name = "hr.applicant.hour.progress"
    _description = "Hr hour progress"
    _order = "id, date"

    applicant_id = fields.Many2one("hr.applicant", string='Applicant', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True, default=date.today())
    hours_number = fields.Float(string='Nombre d\'heures')
    objective = fields.Float(string='Objectif')
    progress = fields.Float(string='Progress', compute="_compute_progress", store=True)

    @api.depends('hours_number', 'objective')
    def _compute_progress(self):
        for record in self:
            if record.objective != 0.0:
                record.progress = (record.hours_number / record.objective) * 100
            else:
                record.progress = 0.0
