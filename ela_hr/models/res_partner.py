# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    crm_lead_ids = fields.One2many("crm.lead", string='Job', tracking=True)

    def _compute_stage_ids(self):
        #right_ids = self.env['project.task.rights'].search([('username_ids.id','=',self.id)])
        stage_ids = self.env['hr.recruitment.stage'].search([(1,'=',1)])
        #stage_ids = []
        #for right in right_ids:
        #    for fase in right.project_task_fases:
        #        stage_ids.append(fase.id)
        for record in self:
            record.stage_ids = stage_ids
            #record.stage_ids = [1,3,4]