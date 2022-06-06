# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from datetime import date

SUGGESTED_STAGE_NAME='Suggeré'
PRESENTED_STAGE_NAME='CV Présenté'
SEND_RDV_STAGE_NAME='Envoyé en RDV'


class HrApplicantCrm(models.Model):
    _name = "hr.applicant.crm"
    _inherit = ['mail.thread.cc',
                'mail.activity.mixin']
    _description = "Hr applicant crm"
    _order = "id"
    _primary_email = 'email_from'
    _mailing_enabled = True
    
    applicant_id = fields.Many2one("hr.applicant", required=True, string='Candidat')
    email_from = fields.Char(related="crm_id.email_from", string="Email", store=True)
    crm_id = fields.Many2one("crm.lead", required=True, string='Opportunité')
    stage_id = fields.Many2one("hr.applicant.crm.stage", string="Étape")
    stage_sequence = fields.Integer(related="stage_id.sequence", string="Stage sequence", store=True)
    last_stage_date = fields.Date(string="Date de la dernière étape", compute="_compute_last_stage_date", readonly=True, store=True)
    response = fields.Selection([
        ("ok", "Accepté"),
        ("ko", "Refusé"),
        ],
        'Réponse employeur',
    )
    response_date = fields.Date(string="Date de résponse", compute="_compute_response_date", readonly=True, store=True)

    @api.depends("stage_id")
    def _compute_last_stage_date(self):
        for record in self:
            if record.stage_id:
                record.last_stage_date = date.today()
            else:
                record.last_stage_date = False

    @api.depends("response")
    def _compute_response_date(self):
        for record in self:
            if record.response:
                record.response_date = date.today()
            else:
                record.response_date = False

    def _reset_stage(self):
        for record in self:
            stage_ids = self.env['hr.applicant.crm.stage'].search([(1, '=', 1),], order='sequence asc', limit=1).ids
            
            record.stage_id = stage_ids[0] if stage_ids else False

    def present_cv(self):
        for record in self:
            record.stage_id = self.env['hr.applicant.crm.stage'].search([('name', '=', PRESENTED_STAGE_NAME)], limit=1)

    def send_rdv(self):
        for record in self:
            record.stage_id = self.env['hr.applicant.crm.stage'].search([('name', '=', SEND_RDV_STAGE_NAME)], limit=1)

    def accept(self):
        for record in self:
            record.response = 'ok'

    def refuse(self):
        for record in self:
            record.response = 'ko'


class HrApplicantCrmStage(models.Model):
    _name = "hr.applicant.crm.stage"
    _description = "Hr applicant crm stage"
    _order = "sequence, id"

    sequence = fields.Integer("Séquence", default=1)
    name = fields.Char("Nom", required=True)
