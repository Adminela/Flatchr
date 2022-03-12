# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError

class ProjectTask(models.Model):
    _inherit = "project.task"

    applicant_id = fields.Many2one("hr.applicant", string='Applicant', tracking=True)
    
    # Formation
    #formation = fields.Selection(related="applicant_id.formation", compute="_compute_formation", inverse="_set_formation")
    certification = fields.Selection(related="applicant_id.certification", readonly=False, tracking=True, store=True)
    dispositif = fields.Selection(related="applicant_id.dispositif", readonly=False, tracking=True, store=True)
    accompagnement = fields.Boolean(related="applicant_id.accompagnement", readonly=False, tracking=True, store=True)
    connaissance = fields.Boolean(related="applicant_id.connaissance", readonly=False, tracking=True, store=True)
    case_number = fields.Char(related="applicant_id.case_number", readonly=False, tracking=True, store=True)
    niveau = fields.Selection(related="applicant_id.niveau", readonly=False, tracking=True, store=True)
    nombre_dheures = fields.Integer(related="applicant_id.nombre_dheures", readonly=False, tracking=True, store=True)
    date_entree_call = fields.Date(related="applicant_id.date_entree_call", readonly=False, tracking=True, store=True)
    date_inscription = fields.Date(related="applicant_id.date_inscription", readonly=False, tracking=True, store=True)
    # Pédagogique
    login = fields.Char(related="applicant_id.login", readonly=False, tracking=True, store=True)
    mot_de_passe = fields.Char(related="applicant_id.mot_de_passe", readonly=False, tracking=True, store=True)
    date_entree = fields.Date(related="applicant_id.date_entree", readonly=False, tracking=True, store=True)
    workhour_available_ids = fields.Many2many(related="applicant_id.workhour_available_ids", readonly=False, tracking=True)
    plateforme = fields.Selection(related="applicant_id.plateforme", readonly=False, tracking=True, store=True)
    motivation_appreciation = fields.Selection(related="applicant_id.motivation_appreciation", readonly=False, tracking=True, store=True)
    date_fin = fields.Date(related="applicant_id.date_fin", readonly=False, tracking=True, store=True)
    test_result = fields.Char(related="applicant_id.test_result", readonly=False, tracking=True, store=True)
    ligne_suivi_ids = fields.One2many(related="applicant_id.ligne_suivi_ids", readonly=False, tracking=True)
    prix_formation = fields.Float(related="applicant_id.prix_formation", readonly=False, tracking=True, store=True)
    solde_formation = fields.Float(related="applicant_id.solde_formation", readonly=False, tracking=True, store=True)
    in_formation = fields.Boolean(related="applicant_id.in_formation", readonly=False, tracking=True, store=True)
    payment_state = fields.Selection(related="applicant_id.payment_state", readonly=False, tracking=True, store=True)

    @api.onchange("stage_id", "in_formation")
    def _onchange_stage_id(self):
        for record in self:
            if record.stage_id.is_move_applicant:
                record.applicant_id.stage_id = record.stage_id.stage_id

            if record.stage_id.to_paiement and record.in_formation:
                if not record.payment_state:
                    record.payment_state = 'to_be_sold'
