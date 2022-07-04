# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrApplicantExperience(models.Model):
    _name = "hr.applicant.experience"
    _description = "Hr applicant experience"
    _order = "sequence, id"

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Séquence", default=1)


class HrApplicantSkillMetier(models.Model):
    _name = "hr.applicant.metier.experience"
    _description = "Hr applicant experience metier"
    _order = "id"

    metier_id = fields.Many2one("hr.metier", string="Métier", ondelete="restrict", required=True)
    experience_id = fields.Many2one("hr.applicant.experience", string="Expérience", ondelete="restrict", required=True)
    applicant_id = fields.Many2one("hr.applicant", string="Candidat", required=True)

    _sql_constraints = [
        ('uniq_metier', 'unique(metier_id, applicant_id)', "'ATTENTION' Ce métier est déja relié au candidat !")
    ]


class HrApplicantSkillScore(models.Model):
    _name = "hr.applicant.metier.experience.score"
    _description = "Hr applicant metier experience score"
    _order = "id"

    metier_id = fields.Many2one("hr.metier", string="Métier", ondelete="restrict", required=True)
    experience_id = fields.Many2one("hr.applicant.experience", string="Expérience", ondelete="restrict", required=True)
    score = fields.Integer(string='Score')
    crm_id = fields.Many2one("crm.lead", string="Opportnité", required=True)

    _sql_constraints = [
        ('uniq_metier', 'unique(metier_id, crm_id)', "'ATTENTION' Ce métier est déja relié a l'opportunité !")
    ]
