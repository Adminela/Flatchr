# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrApplicantDuplicateWizard(models.TransientModel):
    _name = 'hr.applicant.duplicate.wizard'

    applicant_ids = fields.Many2many('hr.applicant', string='Candidats')
    remaining_applicant_ids = fields.Many2many('hr.applicant', 'remaining_applicant_rel', string='Duplicate candidats')
    state = fields.Selection([
        ('start', 'Start'),
        ('pending', 'Pending'),
        ('finished', 'Finished')],
        'Etat',
        readonly=True,
        required=True,
        default='start'
    )
    user_id = fields.Many2one('res.users', 'Recruteur')
    pages = fields.Integer(string='Total pages', tracking=True)
    current_page = fields.Integer(string='Page courante', tracking=True)

    def is_integer_list(self, ids):
        return all(isinstance(i, int) for i in ids)

    def assign_applicant(self):
        if not self.user_id:
            raise ValidationError("Il faut selectionner un recruteur avant de lancer l'assignation")
        self.applicant_ids.write({'user_id' : self.user_id.id})
        self.next_cb()
        return self._next_screen()

    def next_cb(self):
        for applicant_id in self.applicant_ids:
            self.remaining_applicant_ids = [(3, applicant_id.id)]
        
        if self.remaining_applicant_ids:
            self.applicant_ids = self.env['hr.applicant'].search([('email_from', '=', self.remaining_applicant_ids[0].email_from)])
        else:
            self.applicant_ids = False
            self.state = 'finished'

        return self._next_screen()

    def start_process_cb(self):
        self.remaining_applicant_ids = self.env['hr.applicant'].browse(self._context.get('active_ids', False))
        self.applicant_ids = self.remaining_applicant_ids.filtered(lambda app: app.application_count == 0)
        
        self.pages = len(self.remaining_applicant_ids.filtered(lambda app: app.application_count > 0)) + 1

        self.state = 'pending'

        return self._next_screen()

    def close_cb(self):
        return {'type': 'ir.actions.act_window_close'}

    def _next_screen(self):
        self.refresh()
        self.current_page += 1
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'limit': 1000,
            'target': 'new',
        }
