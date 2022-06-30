# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _


class ProjectTaskType(models.Model):
    _inherit = ["project.task.type", 'mail.thread']
    _name = "project.task.type"

    stage_id = fields.Many2one("hr.recruitment.stage", string='Étape de déplacement', ondelete='restrict', tracking=True)
    to_paiement = fields.Boolean(string='Mettre à payer', help='Si cochée, le candidat sera mentionné "À payer" s\'il est tagué "Rentré en formation"', tracking=True)
    cancel = fields.Boolean(string='Archiver candidat', help='Si cochée, le candidat sera archivé et le commercial en charge notifié', tracking=True)
    annulation_titulaire = fields.Boolean(string='Annulation titulaire', help='Si cochée, le candidat sera placé dans l\'état e paiment "A retirer"' , tracking=True)
