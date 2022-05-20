# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = "project.task"

    applicant_id = fields.Many2one("hr.applicant", string='Applicant', tracking=True)
    email_from = fields.Char(related="applicant_id.email_from", readonly=False, tracking=True, store=True)
    partner_phone = fields.Char(related="applicant_id.partner_phone", readonly=False, tracking=True, store=True)
    date_naissance = fields.Date(related="applicant_id.date_naissance", readonly=False, tracking=True, store=True)
    
    # Formation
    certification = fields.Many2one(related="applicant_id.certification", readonly=False, tracking=True, store=True)
    dispositif = fields.Many2one(related="applicant_id.dispositif", readonly=False, tracking=True, store=True)
    accompagnement = fields.Boolean(related="applicant_id.accompagnement", readonly=False, tracking=True, store=True)
    connaissance = fields.Boolean(related="applicant_id.connaissance", readonly=False, tracking=True, store=True)
    case_number = fields.Char(related="applicant_id.case_number", readonly=False, tracking=True, store=True)
    niveau = fields.Many2one(related="applicant_id.niveau", readonly=False, tracking=True, store=True)
    nombre_dheures = fields.Integer(related="applicant_id.nombre_dheures", readonly=False, tracking=True, store=True)
    date_entree_call = fields.Date(related="applicant_id.date_entree_call", readonly=False, tracking=True, store=True)
    date_inscription = fields.Date(related="applicant_id.date_inscription", readonly=False, tracking=True, store=True)
    # Pédagogique
    login = fields.Char(related="applicant_id.login", readonly=False, tracking=True, store=True, groups="ela_hr.group_hide_password")
    mot_de_passe = fields.Char(related="applicant_id.mot_de_passe", readonly=False, tracking=True, store=True, groups="ela_hr.group_hide_password")
    date_entree = fields.Date(related="applicant_id.date_entree", readonly=False, tracking=True, store=True)
    workhour_available_ids = fields.Many2many(related="applicant_id.workhour_available_ids", readonly=False, tracking=True)
    plateforme = fields.Many2one(related="applicant_id.plateforme", readonly=False, tracking=True, store=True)
    motivation_appreciation = fields.Selection(related="applicant_id.motivation_appreciation", readonly=False, tracking=True, store=True)
    date_fin = fields.Date(related="applicant_id.date_fin", readonly=False, tracking=True, store=True)
    test_result = fields.Char(related="applicant_id.test_result", readonly=False, tracking=True, store=True)
    ligne_suivi_ids = fields.One2many(related="applicant_id.ligne_suivi_ids", readonly=False)
    prix_formation = fields.Float(related="applicant_id.prix_formation", readonly=False, tracking=True, store=True, groups="ela_hr.group_hide_prices")
    solde_formation = fields.Float(related="applicant_id.solde_formation", readonly=False, tracking=True, store=True, groups="ela_hr.group_hide_prices")
    in_formation = fields.Boolean(related="applicant_id.in_formation", readonly=False, tracking=True, store=True)
    payment_state = fields.Selection(related="applicant_id.payment_state", readonly=False, tracking=True, store=True)

    meeting_count = fields.Integer(compute='_compute_meeting_count', help='Meeting Count')
    active_ela = fields.Boolean(related="applicant_id.active_ela", readonly=False, tracking=True)

    @api.onchange("stage_id", "in_formation")
    def _onchange_stage_id(self):
        for record in self:
            if record.stage_id.stage_id:
                record.applicant_id.stage_id = record.stage_id.stage_id

            if record.stage_id.to_paiement and record.in_formation:
                if not record.payment_state:
                    record.payment_state = 'to_be_sold'

            if record.applicant_id:
                if record.stage_id.cancel:
                    record.applicant_id.active_ela = False
                else:
                        record.applicant_id.active_ela = True

    def _compute_meeting_count(self):
        if self.applicant_id.ids:
            meeting_data = self.env['calendar.event'].sudo().read_group(
                [('task_id', 'in', self.ids)],
                ['task_id'],
                ['task_id']
            )
            mapped_data = {m['task_id'][0]: m['task_id_count'] for m in meeting_data}
        else:
            mapped_data = dict()
        for task in self:
            task.meeting_count = mapped_data.get(task.id, 0)

    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.partner_id | self.user_ids.partner_id

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window']._for_xml_id('calendar.action_calendar_event')
        res['context'] = {
            'default_task_id': self.id,
            'default_partner_ids': partners.ids,
            #'default_user_ids': self.env.uid,
            'default_name': self.name,
            'default_categ_ids': category and [category.id] or False,
        }
        return res
