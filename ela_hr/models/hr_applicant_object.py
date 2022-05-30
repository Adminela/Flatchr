# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class HrApplicantCertification(models.Model):
    _name = "hr.applicant.certification"
    _description = "Hr applicant certification"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantDispositif(models.Model):
    _name = "hr.applicant.dispositif"
    _description = "Hr applicant dispositif"
    _order = "name"

    name = fields.Char("Name", required=True)

    
class HrApplicantNiveau(models.Model):
    _name = "hr.applicant.niveau"
    _description = "Hr applicant niveau"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantPlateforme(models.Model):
    _name = "hr.applicant.plateforme"
    _description = "Hr applicant plateforme"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantMobilite(models.Model):
    _name = "hr.applicant.mobilite"
    _description = "Hr applicant mobilite"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantHeureSemaine(models.Model):
    _name = "hr.applicant.heure.semaine"
    _description = "Hr applicant heure semaine"
    _order = "sequence, id"

    name = fields.Char("Name", required=True)
    sequence = fields.Integer("Séquence", default=1)


class HrApplicantSituation(models.Model):
    _name = "hr.applicant.situation"
    _description = "Hr applicant situation"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantSecteur(models.Model):
    _name = "hr.applicant.secteur"
    _description = "Hr applicant secteur"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantFiliere(models.Model):
    _name = "hr.applicant.filiere"
    _description = "Hr applicant filiere"
    _order = "name"

    name = fields.Char("Name", required=True)


class HrApplicantMetier(models.Model):
    _name = "hr.applicant.metier"
    _description = "Hr applicant metier"
    _order = "name"

    name = fields.Char("Name", required=True)
