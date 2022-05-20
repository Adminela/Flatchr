# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, api, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    scoring_column = fields.Selection([
        ("scoring_1", "Scoring 1"),
        ("scoring_2", "Scoring 2"),
        ("scoring_3", "Scoring 3"),
        ("scoring_4", "Scoring 4"),
        ("scoring_5", "Scoring 5"),
        ],
        'Colonne de scoring',
        tracking=True
    )

    _sql_constraints = [
        ('uniq_scoring_column', 'unique(scoring_column)', "'ATTENTION' Cette colonne est déja utilisée pour un autre utilisateur !")
    ]