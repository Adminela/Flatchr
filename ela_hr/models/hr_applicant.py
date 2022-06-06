# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta, date, datetime
from odoo import fields, api, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import logging
import json

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _name = 'hr.applicant'
    _inherit = ['hr.applicant','mail.thread.phone']

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
    login = fields.Char(string='Login', tracking=True, groups="ela_hr.group_hide_password")
    mot_de_passe = fields.Char(string='Mot de passe', tracking=True, groups="ela_hr.group_hide_password")
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
        'Motivation / Appréciation', default="niveau_1",
        tracking=True
    )
    date_fin = fields.Date(string='Date de fin', tracking=True)
    test_result = fields.Char(string='Résultat test', tracking=True)
    ligne_suivi_ids = fields.One2many('hr.applicant.hour.progress', inverse_name='applicant_id', string='Tabeau de suivi')
    #Autres
    priority = fields.Selection(string='Priority')
    appreciation = fields.Selection([
        ("niveau_1", "Niveau 1"),
        ("niveau_2", "Niveau 2"),
        ("niveau_3", "Niveau 3"),
        ("niveau_4", "Niveau 4"),
        ("niveau_5", "Niveau 5"),
        ("niveau_6", "Niveau 6"),
        ],
        'Appréciation', default="niveau_1",
        tracking=True
    )
    comptage = fields.Integer(string='Comptage', tracking=True)
    date_naissance = fields.Date(string='Date de naissance', tracking=True)
    genre = fields.Selection([
        ("monsieur", "Monsieur"),
        ("madame", "Madame"),
        ],
        'Genre',
        tracking=True
    )
    lieu_naissance = fields.Char(string='Lieu de naissance', tracking=True)
    skill_ids = fields.Many2many("hr.applicant.skill", string='Compétence', ondelete="restrict", tracking=True)
    # Recrutement
    workzone_ids = fields.Many2many("hr.applicant.workzone", string='Zone de travail', ondelete="restrict", tracking=True)
    code_postal = fields.Char(string='Code postal', tracking=True)
    workhour_ids = fields.Many2many("hr.applicant.workhour", string='Horaire de travail', ondelete="restrict", tracking=True)
    mobilite = fields.Many2one("hr.applicant.mobilite", string='Mobilité',tracking=True)
    heure_semaine = fields.Many2one("hr.applicant.heure.semaine", string='Heure / semaine',tracking=True)
    appreciation_hr = fields.Selection([
        ("niveau_1", "Niveau 1"),
        ("niveau_2", "Niveau 2"),
        ("niveau_3", "Niveau 3"),
        ("niveau_4", "Niveau 4"),
        ("niveau_5", "Niveau 5"),
        ("niveau_6", "Niveau 6"),
        ],
        'Appréciation RH', default="niveau_1",
        tracking=True
    )
    nomenclature_cv = fields.Char(string='Nomenclature CV', tracking=True)
    experience_id = fields.Many2one("hr.applicant.experience", string='Expériences', ondelete="restrict", tracking=True)
    contract_type_ids = fields.Many2many("hr.applicant.contract.type", string='Type de contrat proposé', ondelete="restrict", tracking=True)
    salaire_minimum_min = fields.Float(string='Salaire Minimum de', tracking=True)
    salaire_minimum_max = fields.Float(string='à', tracking=True)
    benefit_wished_ids = fields.Many2many("hr.applicant.benefit", 'benefit_wished_applicant_rel', string='Avantages souhaités', ondelete="restrict", tracking=True)
    situation = fields.Many2one("hr.applicant.situation", string='Situation',tracking=True)
    statut = fields.Char(string='Statut', tracking=True)
    email_from = fields.Char(tracking=True)
    partner_phone = fields.Char(tracking=True)
    is_premium = fields.Boolean(string='CV Premium', tracking=True)
    prix_formation = fields.Float(string='Prix formation', tracking=True, groups="ela_hr.group_hide_prices")
    solde_formation = fields.Float(string='Solde', tracking=True, groups="ela_hr.group_hide_prices")
    in_formation = fields.Boolean(string='Rentré en formation', tracking=True)

    payment_state = fields.Selection([
        ("to_be_sold", "À payer"),
        ("sold", "Payé"),
        ],
        'État du paiement',
        tracking=True
    )
    to_be_sold_date = fields.Date(string='Date à payer', compute='_compute_to_be_sold_date', store=True, tracking=True)
    sold_date = fields.Date(string='Date de paiement', compute='_compute_to_be_sold_date', store=True, tracking=True)

    stage_domain = fields.Char(string='Stage domain', compute='_compute_stage_domain')
    active_ela = fields.Boolean(string='Active ELA', tracking=True, default=True)

    #secteur_ids = fields.Many2many("hr.applicant.secteur", string='Secteur d\'activité', ondelete="restrict", tracking=True)
    #filiere_ids = fields.Many2many("hr.applicant.filiere", string='Filière', ondelete="restrict", tracking=True)
    #metier_ids = fields.Many2many("hr.applicant.metier", string='Métier', ondelete="restrict", tracking=True)

    scoring = fields.Integer(string='Scoring', compute='_compute_scoring', store=True)
    scoring_1 = fields.Integer(string='Scoring', compute='_compute_scoring', store=True)
    scoring_2 = fields.Integer(string='Scoring', compute='_compute_scoring', store=True)
    scoring_3 = fields.Integer(string='Scoring', compute='_compute_scoring', store=True)
    scoring_4 = fields.Integer(string='Scoring', compute='_compute_scoring', store=True)
    scoring_5 = fields.Integer(string='Scoring', compute='_compute_scoring', store=True)

    #crm_suggested_ids = fields.One2many('hr.applicant.crm', inverse_name='applicant_id', string='Jobs proposés')s
    crm_ids = fields.One2many('hr.applicant.crm', inverse_name='applicant_id', string='CVs présentés')
    crm_suggested_nb = fields.Integer(string='# Suggestion', compute="_compute_nbs", store=True)
    crm_presented_nb = fields.Integer(string='# Présentations CVs', compute="_compute_nbs", store=True)
    crm_sent_nb = fields.Integer(string='# Envois en RDV', compute="_compute_nbs", store=True)
    
    nb_nrp = fields.Integer(string='Nombre de NRP', compute='_compute_nb_nrp', store=True)
    nb_nrp_rappel = fields.Integer(string='Nombre de NRP rappel', compute='_compute_nb_nrp', store=True)

    show_suggest_button = fields.Boolean(string='Affcher button de suggestion', compute='_compute_show_suggest_button')
    activities_count = fields.Integer(compute='_compute_activities_count')

    _sql_constraints = [
        ('uniq_nomenclature_cv', 'unique(nomenclature_cv)', "'ATTENTION' Cette nomenclature CV existe déjà !")
    ]

    @api.depends("activity_ids", "activity_ids.nrp")
    def _compute_nb_nrp(self):
        for record in self:
            if record.with_context(active_test=False).activity_ids:
                record.nb_nrp = 0 #len(record.with_context(active_test=False).activity_ids.filtered(lambda act: 'Appeler' in act.activity_type_id.name))
                record.nb_nrp_rappel = 0 #len(record.with_context(active_test=False).activity_ids.filtered(lambda act: 'Rappeler' in act.activity_type_id.name))
                #raise ValidationError(record.with_context(active_test=False).activity_ids.filtered(lambda act: 'Appeler' in act.activity_type_id.name))

    @api.depends("crm_ids", "crm_ids.stage_id")
    def _compute_nbs(self):
        for record in self:
            record.crm_suggested_nb = len(record.crm_ids.filtered(lambda c: c.stage_id.sequence >= 0))
            record.crm_presented_nb = len(record.crm_ids.filtered(lambda c: c.stage_id.sequence >= 1))
            record.crm_sent_nb = len(record.crm_ids.filtered(lambda c: c.stage_id.sequence >= 2))

    @api.depends("payment_state")
    def _compute_to_be_sold_date(self):
        for record in self:
            if record.payment_state == 'to_be_sold':
                record.to_be_sold_date = date.today()
                record.sold_date = False
            elif record.payment_state == 'sold':
                record.to_be_sold_date = record.to_be_sold_date
                record.sold_date = date.today()
            else:
                record.to_be_sold_date = False
                record.sold_date = False

    @api.depends("crm_ids")
    def _compute_show_suggest_button(self):
        for record in self:
            if record._context.get('crm_id', False):
                if not record._context.get('crm_id') in record.crm_ids.mapped('crm_id').ids:
                    record.show_suggest_button = True
                else:
                    record.show_suggest_button = False
            else:
                record.show_suggest_button = False

    @api.depends("name")
    def _compute_stage_domain(self):
        for record in self:
            if record._context.get('is_job_ready', False):
                record.stage_domain = json.dumps([('is_job_ready', '=', True)])
            elif record._context.get('is_candidats_portfolio', False):
                record.stage_domain = json.dumps([('is_candidats_portfolio', '=', True)])
            else:
                record.stage_domain = json.dumps([(1, '=', 1)])

    def _compute_scoring(self):
        for record in self:
            scoring = 0
            if record._context.get('crm_id', False):
                crm_id = self.env['crm.lead'].browse(record._context.get('crm_id', False))

                for workzone_id in record.workzone_ids:
                    if workzone_id in crm_id.workzone_ids:
                        scoring += crm_id.workzone_ids_score

                if crm_id.code_postal == record.code_postal:
                    scoring += crm_id.code_postal_score

                if crm_id.workhour_ids_score:
                    for workhour_id in record.workhour_ids:
                        if workhour_id in crm_id.workhour_ids:
                            scoring += crm_id.workhour_ids_score

                if crm_id.mobilite == record.mobilite:
                    scoring += crm_id.mobilite_score

                if record.heure_semaine.sequence >= crm_id.heure_semaine.sequence:
                    scoring += crm_id.heure_semaine_score

                if not crm_id.appreciation_hr:
                    scoring += crm_id.appreciation_hr_score
                elif record.appreciation_hr and record.appreciation_hr >= crm_id.appreciation_hr:
                    scoring += crm_id.appreciation_hr_score

                if record.experience_id and record.experience_id.sequence >= crm_id.experience_id.sequence:
                    scoring += crm_id.experience_id_score

                for contract_type_id in record.contract_type_ids:
                    if contract_type_id in crm_id.contract_type_ids:
                        scoring += crm_id.contract_type_ids_score
                        break

                if crm_id.salaire_propose >= record.salaire_minimum_min and crm_id.salaire_propose <= record.salaire_minimum_max:
                    scoring += crm_id.salaire_propose_score

                for offer_id in record.benefit_wished_ids:
                    if offer_id in crm_id.benefit_offered_ids:
                        scoring += crm_id.benefit_offered_ids_score

                for secteur_id in record.secteur_ids:
                    if secteur_id in crm_id.secteur_ids:
                        scoring += crm_id.secteur_ids_score
                        break

                for filiere_id in record.filiere_ids:
                    if filiere_id in crm_id.filiere_ids:
                        scoring += crm_id.filiere_ids_score
                        break

                for metier_id in record.metier_ids:
                    if metier_id in crm_id.metier_ids:
                        scoring += crm_id.metier_ids_score
                        break

                for skill_id in record.skill_ids:
                    if skill_id in crm_id.skill_ids:
                        scoring += crm_id.skill_ids_score
                        break

                for categ_id in record.categ_ids:
                    if categ_id in crm_id.categ_ids:
                        scoring += crm_id.categ_ids_score
                        break

            if self.env.user:
                if self.env.user.scoring_column == 'scoring_1':
                    record.scoring_1 = scoring
                elif self.env.user.scoring_column == 'scoring_2':
                    record.scoring_2 = scoring
                elif self.env.user.scoring_column == 'scoring_3':
                    record.scoring_3 = scoring
                elif self.env.user.scoring_column == 'scoring_4':
                    record.scoring_4 = scoring
                elif self.env.user.scoring_column == 'scoring_5':
                    record.scoring_5 = scoring

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
                count = 1
                record.date_entree = record.date_inscription
                while count <= 11:
                    record.date_entree += timedelta(days=1)
                    if not record.env['hr.applicant'].is_global_leave_or_weekend(record.date_entree):
                        count += 1
                
                while record.env['hr.applicant'].is_global_leave_or_weekend(record.date_entree):
                    record.date_entree += timedelta(days=1)
            else:
                record.date_entree = False

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        for record in self:
            if record.stage_id.is_create_project_task:
                if record.formation:
                    if not record.user_id:
                        raise ValidationError(_('Veuillez choisir un recruteur avant de déposer dans cette étape !'))
                    if record.task_id:
                        res = {}
                        res['warning'] = {
                            'title': _('Warning'), 
                            'message': _('Une formation est déjà assigné à ce candidat, aucun autre formation n\'a été crée !')}
                        return res
                else:
                    raise ValidationError(_('Veuillez remplir la formation avant de déposer dans cette étape !'))

    def action_show_task(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Project task'),
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': self.task_id.id
        }

    def _compute_activities_count(self):
        for record in self:
            record.activities_count = len(record.with_context({'active_test' : False}).activity_ids)

    def action_show_activities(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'name': _('Activités'),
            'view_mode': 'tree',
            'domain': [('res_id', '=', self.id), ('res_model', '=', 'hr.applicant')],
            'context': {
                'default_res_id': self.id,
                'default_res_model': 'hr.applicant',
                'active_test': False,
            },
        }

    def write(self,vals):
        res = super(HrApplicant, self).write(vals)
        if 'stage_id' in vals:
            if self.stage_id.is_create_project_task:
                if self.formation:
                    if not self.task_id:
                        self.task_id = self.env["project.task"].create({
                            'name' : self.partner_name,
                            'applicant_id' : self._origin.id,
                            'project_id' : self.formation.id,
                            'user_ids' : [self.user_id.id],
                        })
        return res

    @staticmethod
    def reset_applicant_hr(env):
        reset_stage_ids = env['hr.recruitment.stage'].search([('is_reset', '=', True)])

        date_expire = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)
        while env['hr.applicant'].is_global_leave_or_weekend(date_expire):
            date_expire += timedelta(days=1)
        
        applicant_ids = env['hr.applicant'].search([('stage_id', 'in', reset_stage_ids.ids),('date_last_stage_update', '<', date_expire)])
        for applicant_id in applicant_ids:
            activity_ids = applicant_id.activity_ids.filtered(lambda act: act.date_deadline >= datetime.date(datetime.now()))
            
            if not activity_ids:
                applicant_id._reset_stage()
                applicant_id.user_id = False
                env.cr.commit()

                for message_id in applicant_id.message_ids:
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
        return stages.browse(stage_ids)

    def action_makeMeeting(self):
        res = super(HrApplicant, self).action_makeMeeting()

        remove_key = res['context'].pop("default_partner_ids", None)
        return res

    def allready_suggest_candidats(self):
        pass

    def suggest_candidats(self):
        for record in self:
            if record._context.get('crm_id', False):
                hr_applicant_crm = record.env['hr.applicant.crm'].create({
                    'applicant_id' : record.id,
                    'crm_id' : record._context.get('crm_id', False),
                })

                hr_applicant_crm._reset_stage()

    @api.onchange('partner_phone', 'company_id')
    def _onchange_phone_validation(self):
        if self.partner_phone:
            self.partner_phone = self.phone_get_sanitized_number(number_fname='partner_phone', force_format='INTERNATIONAL') or self.partner_phone

    def _phone_get_number_fields(self):
        """ Use mobile or phone fields to compute sanitized phone number """
        return ['partner_phone']
