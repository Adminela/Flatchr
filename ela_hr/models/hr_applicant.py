# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta, date, datetime
from odoo import fields, api, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    # Import champs Studio
    # Formation
    formation = fields.Many2one("project.project", string='Formation', tracking=True)
    task_id = fields.Many2one("project.task", string='Tâche', tracking=True)
    task_stage_id = fields.Many2one(related="task_id.stage_id", string="Étape de formation", readonly=False, tracking=True, store=True)
    certification = fields.Many2one("hr.applicant.certification", string='Certification',tracking=True)
    dispositif = fields.Many2one("hr.applicant.dispositif", string='Dispositif',tracking=True)
    accompagnement = fields.Boolean(string='Accompagnement', tracking=True)
    connaissance = fields.Boolean(string='Connaissance', tracking=True)
    case_number = fields.Char(string='N° de dossier', tracking=True)
    niveau = fields.Many2one("hr.applicant.niveau", string='Niveau',tracking=True)
    nombre_dheures = fields.Integer(string='Nombre d\'heures', tracking=True)
    date_entree_call = fields.Date(string='Date entrée call', tracking=True)
    date_inscription = fields.Date(string='Date d\'inscription', tracking=True)
    # Pédagogique
    login = fields.Char(string='Login', tracking=True)
    mot_de_passe = fields.Char(string='Mot de passe', tracking=True)
    date_entree = fields.Date(string='Date d\'entrée', compute="_compute_date_entree", store=True, tracking=True)
    workhour_available_ids = fields.Many2many("hr.applicant.workhour.available", string='Horaire disponible', ondelete="restrict", tracking=True)
    plateforme = fields.Many2one("hr.applicant.plateforme", string='Plateforme',tracking=True)
    motivation_appreciation = fields.Selection([
        ("niveau_1", "Niveau 1"),
        ("niveau_2", "Niveau 2"),
        ("niveau_3", "Niveau 3"),
        ("niveau_4", "Niveau 4"),
        ("niveau_5", "Niveau 5"),
        ("niveau_6", "Niveau 6"),
        ],
        'Motivation / Appréciation',
        tracking=True
    )
    date_fin = fields.Date(string='Date de fin', tracking=True)
    test_result = fields.Char(string='Résultat test', tracking=True)
    ligne_suivi_ids = fields.One2many('hr.applicant.hour.progress', inverse_name='applicant_id', string='Tabeau de suivi', tracking=True)
    #Autres
    appreciation = fields.Selection([
        ("niveau_1", "Niveau 1"),
        ("niveau_2", "Niveau 2"),
        ("niveau_3", "Niveau 3"),
        ("niveau_4", "Niveau 4"),
        ("niveau_5", "Niveau 5"),
        ("niveau_6", "Niveau 6"),
        ],
        'Appréciation',
        tracking=True
    )
    appreciation_hr = fields.Selection([
        ("niveau_1", "Niveau 1"),
        ("niveau_2", "Niveau 2"),
        ("niveau_3", "Niveau 3"),
        ("niveau_4", "Niveau 4"),
        ("niveau_5", "Niveau 5"),
        ("niveau_6", "Niveau 6"),
        ],
        'Appréciation RH',
        tracking=True
    )
    benefit_wished_ids = fields.Many2many("hr.applicant.benefit", 'benefit_wished_applicant_rel', string='Avantages souhaités', ondelete="restrict", tracking=True)
    benefit_offered_ids = fields.Many2many("hr.applicant.benefit", 'benefit_offered_applicant_rel', string='Avantages proposés', ondelete="restrict", tracking=True)
    comptage = fields.Integer(string='Comptage', tracking=True)
    date_naissance = fields.Date(string='Date de naissance', tracking=True)
    genre = fields.Selection([
        ("monsieur", "Monsieur"),
        ("madame", "Madame"),
        ],
        'Genre',
        tracking=True
    )
    heure_semaine = fields.Many2one("hr.applicant.heure.semaine", string='Heure / semaine',tracking=True)
    workhour_ids = fields.Many2many("hr.applicant.workhour", string='Horaire de travail', ondelete="restrict", tracking=True)
    lieu_naissance = fields.Char(string='Lieu de naissance', tracking=True)
    skill_ids = fields.Many2many("hr.applicant.skill", string='Compétence', ondelete="restrict", tracking=True)
    workzone_ids = fields.Many2many("hr.applicant.workzone", string='Zone de travail', ondelete="restrict", tracking=True)
    mobilite = fields.Many2one("hr.applicant.mobilite", string='Mobilité',tracking=True)
    salaire_minimum = fields.Integer(string='Salaire Minimum', tracking=True)
    salaire_propose = fields.Integer(string='Salaire proposé', tracking=True)
    situation = fields.Many2one("hr.applicant.situation", string='Situation',tracking=True)
    statut = fields.Char(string='Statut', tracking=True)
    contract_type_ids = fields.Many2many("hr.applicant.contract.type", string='Type de contrat proposé', ondelete="restrict", tracking=True)
    email_from = fields.Char(tracking=True)
    partner_phone = fields.Char(tracking=True)
    is_premium = fields.Boolean(string='CV Premium', tracking=True)
    prix_formation = fields.Float(string='Prix formation', tracking=True)
    solde_formation = fields.Float(string='Solde', tracking=True)
    in_formation = fields.Boolean(string='Rentré en formation', tracking=True)
    payment_state = fields.Selection([
        ("to_be_sold", "À payer"),
        ("sold", "Payé"),
        ],
        'État du paiement',
        tracking=True
    )

    @api.model
    def is_global_leave_or_weekend(self, date):
        if date.weekday() == 5 or date.weekday() == 6:
            return True

        global_leaves = self.env['resource.calendar.leaves'].search([('date_from', '<=', date),('date_to', '>=', date),('resource_id', '=', False)])

        if global_leaves:
            return True

        return False

    @api.depends("date_inscription")
    def _compute_date_entree(self):
        for record in self:
            if record.date_inscription:
                record.date_entree = record.date_inscription + timedelta(days=15)
                while record.env['hr.applicant'].is_global_leave_or_weekend(record.date_entree):
                    record.date_entree += timedelta(days=1)
            else:
                record.date_entree = False

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        for record in self:
            res = {}
            if record.stage_id.is_create_project_task:
                if record.formation:
                    if not record.task_id:
                        record.task_id = self.env["project.task"].create({
                            'name' : record.partner_name,
                            'applicant_id' : record._origin.id,
                            'project_id' : record.formation.id,
                            'user_id' : record.user_id.id,
                        })
                    else:
                        res['warning'] = {
                        'title': _('Warning'), 
                        'message': _('Une formation est déjà assigné à ce candidat, aucun autre formation n\'a été crée !')}
                        return res

    def action_show_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project task'),
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': self.task_id.id
        }

    def write(self,vals):
        for record in self:
            if 'stage_id' in vals:
                stage_id = record.env['hr.recruitment.stage'].browse(vals['stage_id'])
                if stage_id.is_create_project_task:
                    if not record.formation:
                        raise ValidationError("Veuillez remplir la formation avant de déposer dans cette étape !")
        
        return super(HrApplicant, self).write(vals)

    @staticmethod
    def reset_applicant_hr(env):
        date_expire = datetime.now() - timedelta(seconds=appl.stage_id.periode)
        while record.env['hr.applicant'].is_global_leave_or_weekend(date_expire):
            #date_expire = date_expire.replace(hour=0, minute=0, second=2)
            date_expire += timedelta(days=1)
        
        all_applicants = env['hr.applicant'].search([(1, '=', 1)]).filtered(lambda appl: appl.stage_id.is_reset and (appl.date_last_stage_update < date_expire))

        for record in all_applicants:
            record._reset_stage()
            record.user_id = False
            env.cr.commit()

            for message_id in record.message_ids:
                message_id.is_manager = True

    def _reset_stage(self):
        for applicant in self:
            if applicant.job_id:
                stage_ids = self.env['hr.recruitment.stage'].search([
                    '|',
                    ('job_ids', '=', False),
                    ('job_ids', '=', applicant.job_id.id),
                    ('fold', '=', False)
                ], order='sequence asc', limit=1).ids
                applicant.stage_id = stage_ids[0] if stage_ids else False
            else:
                applicant.stage_id = False

    def toggle_premium(self):
        for record in self:
            record.is_premium = not record.is_premium

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        job_id = self._context.get('default_job_id')

        is_candidats_portfolio = self._context.get('is_candidats_portfolio')
        is_job_ready = self._context.get('is_job_ready')

        search_domain = [('job_ids', '=', False)]
        if job_id:
            search_domain = ['|', ('job_ids', '=', job_id)] + search_domain
        if stages:
            search_domain = ['|', ('id', 'in', stages.ids)] + search_domain

        if is_candidats_portfolio:
            search_domain = [('is_candidats_portfolio', '=', True)] + search_domain
        elif is_job_ready:
            search_domain = [('is_job_ready', '=', True)] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        #raise ValidationError("search_domain %s" %(search_domain))**
        return stages.browse(stage_ids)
