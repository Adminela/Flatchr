# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    opportunity_applicant_ids = fields.One2many('hr.applicant.crm', compute='_compute_opportunity_applicant_ids')
    
    def _compute_opportunity_applicant_ids(self):
        for record in self:
            record.opportunity_applicant_ids = record.opportunity_ids.mapped('candidat_crm_suggested_ids')
    