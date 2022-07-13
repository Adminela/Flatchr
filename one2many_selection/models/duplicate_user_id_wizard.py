# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrApplicantDuplicateWizard(models.TransientModel):
    _inherit = 'hr.applicant.duplicate.wizard'

    # Demo method that will delete your sale orde line as you select and press delete
    @api.model
    def archive_hr_applicant(self, selected_ids):
        hr_applicant = self.env['hr.applicant'].sudo()
        hr_applicant_ids = hr_applicant.browse(selected_ids)
        for hr_applicant_id in hr_applicant_ids:
            hr_applicant_id.write({'active' : False})
        return False

    @api.model
    def assign_hr_applicant(self, selected_ids, recruteur):
        hr_applicant = self.env['hr.applicant'].sudo()
        hr_applicant_ids = hr_applicant.browse(selected_ids)
        #for hr_applicant_id in hr_applicant_ids:
            #hr_applicant_id.write({'user_id' : recruteur})
        _logger.info("****************************** %s" %self.user_id)
        return False