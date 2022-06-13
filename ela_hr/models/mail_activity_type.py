# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    def _get_model_selection(self):
        return super(MailActivityType, self)._get_model_selection()

    nrp = fields.Boolean(string='NRP')
    nrp_next_activity_res_model = fields.Selection(selection=_get_model_selection, string="Modèle de la prochaine activité")
    nrp_next_activity_res_field = fields.Many2one('ir.model.fields', string='Champs', domain="[('model_id', '=', res_model), ('relation', '=', nrp_next_activity_res_model)]")
    next_activity_res_model = fields.Selection(selection=_get_model_selection, string="Modèle de la prochaine activité NRP")
    next_activity_res_field = fields.Many2one('ir.model.fields', string='Champs NRP', domain="[('model_id', '=', res_model), ('relation', '=', next_activity_res_model)]")
    nrp_triggered_next_type_id = fields.Many2one('mail.activity.type', string='Prochaine activité NRP', compute='_compute_triggered_next_type_id',
        inverse='_inverse_triggered_next_type_id', store=True, readonly=False,
        domain="[('res_model', '=', nrp_next_activity_res_model)]", ondelete='restrict')
    nrp_mail_template_ids = fields.Many2many('mail.template','nrp_mail_activity_mail_template_rel', string='Modèles d\'email NRP')
    nrp_delay_count = fields.Integer('NRP Date prévue', default=0)
    nrp_delay_unit = fields.Selection([
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('months', 'months')], string="NRP Delay units", help="Unit of delay", required=True, default='days')
    nrp_delay_from = fields.Selection([('current_date', 'after completion date'), ('previous_activity', 'after previous activity deadline')], 
                                      string="NRP Delay from", help="Type of delay", required=True, default='previous_activity')
    nrp_chaining_type = fields.Selection([('suggest', 'Suggest Next Activity'), ('trigger', 'Trigger Next Activity')], string="Chaining Type", required=True, default="suggest")
