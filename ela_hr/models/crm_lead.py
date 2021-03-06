# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from lxml import etree
from ast import literal_eval
from odoo.osv import expression

class CrmLead(models.Model):
    _inherit = "crm.lead"

    # Recrutement
    workzone_ids = fields.Many2many("hr.applicant.workzone", string='Zone de travail', ondelete="restrict")
    workzone_ids_score = fields.Integer(string='Zones de travail score')
    code_postal = fields.Char(string='Code postal', tracking=True)
    code_postal_score = fields.Integer(string='Code postal score')
    workhour_ids = fields.Many2many("hr.applicant.workhour", string='Horaire de travail', ondelete="restrict")
    workhour_ids_score = fields.Integer(string='Horaires de travail score')
    mobilite = fields.Many2one("hr.applicant.mobilite", string='Mobilité')
    mobilite_score = fields.Integer(string='Mobilité score')
    heure_semaine = fields.Many2one("hr.applicant.heure.semaine", string='Heure / semaine')
    heure_semaine_score = fields.Integer(string='Heure / semaine score')
    appreciation_hr = fields.Selection([
        ("niveau_1", "Niveau 1"),
        ("niveau_2", "Niveau 2"),
        ("niveau_3", "Niveau 3"),
        ("niveau_4", "Niveau 4"),
        ("niveau_5", "Niveau 5"),
        ("niveau_6", "Niveau 6"),
        ],
        'Appréciation RH', default="niveau_1"
    )
    appreciation_hr_score = fields.Integer(string='Appréciation RH score')
    experience_id = fields.Many2one("hr.applicant.experience", string='Expériences', ondelete="restrict")
    experience_id_score = fields.Integer(string='Expériences score')
    contract_type_ids = fields.Many2many("hr.applicant.contract.type", string='Types de contrats proposé', ondelete="restrict")
    contract_type_ids_score = fields.Integer(string='Types de contrats proposé score')
    salaire_propose = fields.Float(string='Salaire proposé')
    salaire_propose_score = fields.Integer(string='Salaire proposé score')
    benefit_offered_ids = fields.Many2many("hr.applicant.benefit", 'benefit_offered_crm_rel', string='Avantages proposés', ondelete="restrict")
    benefit_offered_ids_score = fields.Integer(string='Avantages proposés score')

    secteur_ids = fields.Many2many("hr.activity", string='Secteurs d\'activité', ondelete="restrict", tracking=True)
    secteur_ids_score = fields.Integer(string='Secteurs d\'activité score')
    filiere_ids = fields.Many2many("hr.channel", string='Filières', ondelete="restrict", tracking=True)
    filiere_ids_score = fields.Integer(string='Filières score')
    metier_ids = fields.Many2many("hr.metier", string='Métiers souhaités', ondelete="restrict", tracking=True)
    metier_ids_score = fields.Integer(string='Métiers souhaités score')
    skill_ids = fields.Many2many("hr.applicant.skill", string='Hard skills', ondelete="restrict", tracking=True)
    skill_ids_score = fields.Integer(string='Compétences score')
    metier_experience_score_ids = fields.One2many('hr.applicant.metier.experience.score', inverse_name='crm_id', string='Expériences')

    categ_ids = fields.Many2many("hr.applicant.category", string='Soft skills', ondelete="restrict", tracking=True)
    categ_ids_score = fields.Integer(string='Etiquettes score')

    candidat_crm_suggested_ids = fields.One2many('hr.applicant.crm', inverse_name='crm_id', domain=[('stage_id.sequence', '=', 0)], string='Candidats proposés')
    candidat_crm_presented_ids = fields.One2many('hr.applicant.crm', inverse_name='crm_id', domain=[('stage_id.sequence', '!=', 0)], string='Candidats présentés')
    candidat_suggested_nb = fields.Integer(string='# Suggérés', compute="_compute_nbs", store=True)
    candidat_presented_nb = fields.Integer(string='# CVs présentés', compute="_compute_nbs", store=True)
    candidat_sent_nb = fields.Integer(string='# Envoyés en RDV', compute="_compute_nbs", store=True)
    
    child_ids = fields.One2many(related='partner_id.child_ids', string='Contacts & Adresses')
    privileged_interlocutor_id = fields.Many2one("res.partner", string='Interlocuteur privilégié', ondelete="restrict")

    @api.depends("candidat_crm_suggested_ids", "candidat_crm_suggested_ids.stage_id")
    def _compute_nbs(self):
        for record in self:
            record.candidat_suggested_nb = len(record.candidat_crm_suggested_ids.filtered(lambda c: c.stage_id.sequence >= 0))
            record.candidat_presented_nb = len(record.candidat_crm_presented_ids.filtered(lambda c: c.stage_id.sequence >= 1))
            record.candidat_sent_nb = len(record.candidat_crm_presented_ids.filtered(lambda c: c.stage_id.sequence >= 2))
            
    def action_candidat_suggested(self):
        search_view = self.env.ref('ela_hr.ela_hr_hr_applicant_view_search_ter')

        context = {}
        search_domain = []
        domain = []
        search_view_arch = """
            <search string="Candidats">
                <field string="Applicant" name="partner_name" 
                    filter_domain="['|', '|', '|', '|', '|', ('name', 'ilike', self), ('partner_name', 'ilike', self), 
                    ('email_from', 'ilike', self),('case_number', 'ilike', self),('nomenclature_cv', 'ilike', self),('partner_phone', 'ilike', self)]"/>
                <field name="workzone_ids"/>
                <field name="code_postal"/>
                <field name="workhour_ids"/>
                <field name="mobilite"/>
                <field name="heure_semaine"/>
                <field name="appreciation_hr"/>
                <!--<field name="experience_id"/>-->
                <field name="contract_type_ids"/>
                <field name="salaire_minimum_min"/>
                <field name="salaire_minimum_max"/>
                <field name="benefit_wished_ids"/>
                <field name="secteur_ids"/>
                <field name="filiere_ids"/>
                <field name="metier_ids"/>
                <field name="skill_ids"/>
                <field name="categ_ids"/>
            """

        if self.workzone_ids_score:
            search_domain = expression.AND([search_domain, [('workzone_ids', 'in', self.workzone_ids.ids)]])
            search_view_arch += """
                <filter string="Zones de travail contient %s" name="workzone_ids_filter" domain="[('workzone_ids', 'in', %s)]"/>
            """%(self.workzone_ids.mapped("name"), self.workzone_ids.ids)
            context.update({'search_default_workzone_ids' : self.workzone_ids.ids})

        if self.code_postal_score:
            search_domain = expression.OR([search_domain, [('code_postal', '=', self.code_postal)]])
            search_view_arch += """
                <filter string="Code postal est égale à '%s'" name="code_postal_filter" domain="[('code_postal', '=', '%s')]"/>
            """%(self.code_postal, self.code_postal)
            context.update({'search_default_code_postal_filter' : 1})

        if self.workhour_ids_score:
            search_domain = expression.OR([search_domain, [('workhour_ids', 'in', self.workhour_ids.ids)]])
            search_view_arch += """
                <filter string="Horaires de travail contient %s" name="workhour_ids_filter" domain="[('workhour_ids', 'in', %s)]"/>
            """%(self.workhour_ids.mapped("name"), self.workhour_ids.ids)
            context.update({'search_default_workhour_ids_filter' : 1})

        if self.mobilite_score:
            search_domain = expression.OR([search_domain, [('mobilite', '=', self.mobilite.id)]])
            search_view_arch += """
                <filter string="Mobilité est égale à '%s'" name="mobilite_filter" domain="[('mobilite', '=', %s)]"/>
            """%(self.mobilite.name, self.mobilite.id)
            context.update({'search_default_mobilite_filter' : 1})

        if self.heure_semaine_score:
            search_domain = expression.OR([search_domain, [('heure_semaine.sequence', '>=', self.heure_semaine.sequence)]])
            search_view_arch += """
                <filter string="Heure / semaine est supérieure ou égale à '%s'" name="heure_semaine_filter" domain="[('heure_semaine.sequence', '>=', %s)]"/>
            """%(self.heure_semaine.name, self.heure_semaine.sequence)
            context.update({'search_default_heure_semaine_filter' : 1})

        if self.appreciation_hr_score:
            search_domain = expression.OR([search_domain, [('appreciation_hr', '>=', self.appreciation_hr)]])
            search_view_arch += """
                <filter string="Appréciation RH est supérieure ou égale à '%s'" name="appreciation_hr_filter" domain="[('appreciation_hr', '>=', '%s')]"/>
            """%(self.appreciation_hr, self.appreciation_hr)
            context.update({'search_default_appreciation_hr_filter' : 1})

        #if self.experience_id_score:
        #    search_domain = expression.OR([search_domain, [('experience_id.sequence', '>=', self.experience_id.sequence)]])
        #    search_view_arch += """
        #        <filter string="Expérience est supérieure ou égale à '%s'" name="experience_id_filter" domain="[('experience_id.sequence', '>=', %s)]"/>
        #    """%(self.experience_id.name, self.experience_id.sequence)
        #    #context.update({'search_default_experience_id_filter' : 1})

        if self.contract_type_ids_score:
            search_domain = expression.OR([search_domain, [('contract_type_ids', 'in', self.contract_type_ids.ids)]])
            search_view_arch += """
                <filter string="Types de contrats contient %s" name="contract_type_ids_filter" domain="[('contract_type_ids', 'in', %s)]"/>
            """%(self.contract_type_ids.mapped("name"), self.contract_type_ids.ids)
            context.update({'search_default_contract_type_ids_filter' : 1})

        if self.salaire_propose_score:
            search_domain = expression.OR([search_domain, [('salaire_minimum_min', '<=', self.salaire_propose), ('salaire_minimum_max', '>=', self.salaire_propose)]])
            search_view_arch += """
                <filter string="Salaire minimum est inférieur à '%s' et salaire maximum est supérieur '%s'" name="salaire_propose_filter" domain="[('salaire_minimum_max', '&gt;=', %s),('salaire_minimum_min', '&lt;=', %s)]"/>
            """%(self.salaire_propose, self.salaire_propose, self.salaire_propose, self.salaire_propose)
            context.update({'search_default_salaire_propose_filter' : 1})

        if self.benefit_offered_ids_score:
            search_domain = expression.OR([search_domain, [('benefit_wished_ids', 'in', self.benefit_offered_ids.ids)]])
            search_view_arch += """
                <filter string="Avantages proposés contient %s" name="benefit_offered_ids_filter" domain="[('benefit_wished_ids', 'in', %s)]"/>
            """%(self.benefit_offered_ids.mapped("name"), self.benefit_offered_ids.ids)
            context.update({'search_default_benefit_offered_ids_filter' : 1})

        if self.secteur_ids_score:
            search_domain = expression.OR([search_domain, [('secteur_ids', 'in', self.secteur_ids.ids)]])
            search_view_arch += """
                <filter string="Secteurs d'activités contient %s" name="secteur_ids_filter" domain="[('secteur_ids', 'in', %s)]"/>
            """%(self.secteur_ids.mapped("name"), self.secteur_ids.ids)
            context.update({'search_default_secteur_ids_filter' : 1})

        if self.filiere_ids_score:
            search_domain = expression.OR([search_domain, [('filiere_ids', 'in', self.filiere_ids.ids)]])
            search_view_arch += """
                <filter string="Filières contient %s" name="filiere_ids_filter" domain="[('filiere_ids', 'in', %s)]"/>
            """%(self.filiere_ids.mapped("name"), self.filiere_ids.ids)
            context.update({'search_default_filiere_ids_filter' : 1})

        if self.metier_ids_score:
            final_metier_names = []
            for metier_name in self.metier_ids.mapped("name"):
                final_metier_names.append(metier_name.replace('&','&amp;').replace('\'','&apos;'))
            search_domain = expression.OR([search_domain, [('metier_ids', 'in', self.metier_ids.ids)]])
            search_view_arch += """
                <filter string="Métiers contient %s" name="metier_ids_filter" domain="[('metier_ids', 'in', %s)]"/>
            """%(final_metier_names, self.metier_ids.ids)
            context.update({'search_default_metier_ids_filter' : 1})

        if self.skill_ids_score:
            search_domain = expression.OR([search_domain, [('skill_ids', 'in', self.skill_ids.ids)]])
            search_view_arch += """
                <filter string="Compétences contient %s" name="skill_ids_filter" domain="[('skill_ids', 'in', %s)]"/>
            """%(self.skill_ids.mapped("name"), self.skill_ids.ids)
            context.update({'search_default_skill_ids_filter' : 1})

        if self.categ_ids_score:
            final_categ_names = []
            for categ_name in self.categ_ids.mapped("name"):
                final_categ_names.append(categ_name.replace('&','&amp;').replace('\'','&apos;'))
            search_domain = expression.OR([search_domain, [('categ_ids', 'in', self.categ_ids.ids)]])
            search_view_arch += """
                <filter string="Compétences contient %s" name="categ_ids_filter" domain="[('categ_ids', 'in', %s)]"/>
            """%(final_categ_names, self.categ_ids.ids)
            context.update({'search_default_categ_ids_filter' : 1})

        if context == {}:
            search_view_arch += """
                <filter string="Aucun résultat n'est disponible, les scores de l'offre sont à zéro" name="none_filter" domain="[('code_postal', '=', 999999999999)]"/>
            """
            context.update({'search_default_none_filter' : 1})

        context.update({'crm_id' : self.id})
        domain = [('workzone_ids', 'in', self.workzone_ids.ids)]

        if self.env.user:
            if self.env.user.scoring_column == 'scoring_1':
                context.update({'show_scoring_1' : True})
                domain = expression.OR([domain, [('scoring_1', '!=', 0)]])
                search_view_arch += """
                    <filter string="Expérience par métier" name="scoring_filter" domain="[('scoring_1', '!=', 0)]"/>
                """
                context.update({'scoring_filter' : 1})
            elif self.env.user.scoring_column == 'scoring_2':
                context.update({'show_scoring_2' : True})
                domain = expression.OR([domain, [('scoring_2', '!=', 0)]])
                search_view_arch += """
                    <filter string="Expérience par métier" name="scoring_filter" domain="[('scoring_2', '!=', 0)]"/>
                """
            elif self.env.user.scoring_column == 'scoring_3':
                context.update({'show_scoring_3' : True})
                domain = expression.OR([domain, [('scoring_3', '!=', 0)]])
                search_view_arch += """
                    <filter string="Expérience par métier" name="scoring_filter" domain="[('scoring_3', '!=', 0)]"/>
                """
            elif self.env.user.scoring_column == 'scoring_4':
                context.update({'show_scoring_4' : True})
                domain = expression.OR([domain, [('scoring_4', '!=', 0)]])
                search_view_arch += """
                    <filter string="Expérience par métier" name="scoring_filter" domain="[('scoring_4', '!=', 0)]"/>
                """
            elif self.env.user.scoring_column == 'scoring_5':
                context.update({'show_scoring_5' : True})
                domain = expression.OR([domain, [('scoring_5', '!=', 0)]])
                search_view_arch += """
                    <filter string="Expérience par métier" name="scoring_filter" domain="[('scoring_5', '!=', 0)]"/>
                """
            else:
                raise ValidationError("Veuillez contacter votre administrateur pour choisir une colonne de scorring pour votre Utilisateur")
                
            context.update({'search_default_scoring_filter' : 1})

        search_view_arch += """
                <group expand="0" string="Group By">
                    <filter string="Code postal" name="code_postal" domain="[]" context="{'group_by': 'code_postal'}"/>
                    <filter string="Mobilité" name="mobilite" domain="[]" context="{'group_by': 'mobilite'}"/>
                    <filter string="Heure / Semaine" name="heure_semaine" domain="[]" context="{'group_by': 'heure_semaine'}"/>
                    <filter string="Appréciation RH" name="appreciation_hr" domain="[]" context="{'group_by': 'appreciation_hr'}"/>
                    <!--<filter string="Expérience" name="experience_id" domain="[]" context="{'group_by': 'experience_id'}"/>-->
                </group>
            </search>"""

        search_view.arch = search_view_arch

        #if search_domain:
        #    self.env['hr.applicant'].search(search_domain).with_context(crm_id=self.id)._compute_scoring()

        #self.env['hr.applicant'].search([(1, '=', 1)]).with_context(crm_id=self.id)._compute_scoring()
        self.env['hr.applicant'].search(domain).with_context(crm_id=self.id)._compute_scoring()

        return {
            'name': _('Suggérer candidats'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'views': [(self.env.ref('ela_hr.ela_hr_crm_case_tree_view_job_crm').id, 'list'), (False, 'form')],
            'search_view_id': search_view.id,
            'res_model': 'hr.applicant',
            'target': 'self',
            'context': context,
        }
