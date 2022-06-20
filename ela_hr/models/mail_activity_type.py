# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MailActivityType(models.Model):
    _inherit = 'mail.activity.type'

    def _get_model_selection(self):
        return super(MailActivityType, self)._get_model_selection()

    many2one_model_ids = fields.Many2many('ir.model', compute='_compute_many2one_model_ids')

    nrp = fields.Boolean(string='NRP')
    nrp_chaining_type = fields.Selection([('suggest', 'Suggest Next Activity'), ('trigger', 'Trigger Next Activity')], string="Chaining Type", required=True, default="suggest")

    nrp_triggered_next_type_id = fields.Many2one('mail.activity.type', string='Activité par défaut', compute='_compute_nrp_triggered_next_type_id',
        inverse='_inverse_nrp_triggered_next_type_id', store=True, readonly=False, ondelete='restrict')
    nrp_suggested_next_type_ids = fields.Many2many('mail.activity.type', 'nrp_mail_activity_rel', 'activity_id', 'recommended_id', string='Activités recommandées',
        compute='_compute_nrp_suggested_next_type_ids', inverse='_inverse_nrp_suggested_next_type_ids', store=True, readonly=False)
    nrp_previous_type_ids = fields.Many2many(
        'mail.activity.type', 'nrp_mail_activity_rel', 'recommended_id', 'activity_id',
        domain="['|', ('res_model', '=', False), ('res_model', '=', res_model)]",
        string='NRP Preceding Activities')

    nrp_next_activity_res_model = fields.Selection(selection=_get_model_selection, compute='_compute_nrp_next_activity_res_model', string="Modèle de la prochaine activité NRP", store=True)
    nrp_next_activity_res_field = fields.Many2one('ir.model.fields', string='Champs NRP', domain="[('model_id', '=', res_model), ('relation', '=', nrp_next_activity_res_model)]")
    required_nrp_field = fields.Boolean(string='Champs NRP Invisible', compute='_compute_required_nrp_field')
    nrp_mail_template_ids = fields.Many2many('mail.template','nrp_mail_activity_mail_template_rel', string='Modèles d\'email')

    nrp_delay_count = fields.Integer('NRP Date prévue', default=0)
    nrp_delay_unit = fields.Selection([
        ('days', 'days'),
        ('weeks', 'weeks'),
        ('months', 'months')], string="NRP Delay units", help="Unit of delay", required=True, default='days')
    nrp_delay_from = fields.Selection([('current_date', 'after completion date'), ('previous_activity', 'after previous activity deadline')], 
                                      string="NRP Delay from", help="Type of delay", required=True, default='previous_activity')

    triggered_next_type_id = fields.Many2one(domain=[])
    suggested_next_type_ids = fields.Many2many(domain=[])
    next_activity_res_model =  fields.Selection(selection=_get_model_selection, compute='_compute_next_activity_res_model', string="Modèle de la prochaine activité", store=True)
    next_activity_res_field = fields.Many2one('ir.model.fields', string='Champs', domain="[('model_id', '=', res_model), ('relation', '=', next_activity_res_model)]")
    required_field = fields.Boolean(string='Champs Invisible', compute='_compute_required_field')



    @api.onchange('many2one_model_ids')
    def _onchange_many2one_model_ids(self):
        self.nrp_triggered_next_type_id = False
        return {
            'domain': {
                'nrp_triggered_next_type_id': ['|', '|', ('res_model', 'in', self.many2one_model_ids.mapped('model')), ('res_model', '=', self.res_model), ('res_model', '=', False)],
                'triggered_next_type_id': ['|', '|', ('res_model', 'in', self.many2one_model_ids.mapped('model')), ('res_model', '=', self.res_model), ('res_model', '=', False)],
                'nrp_suggested_next_type_ids': ['|', '|', ('res_model', 'in', self.many2one_model_ids.mapped('model')), ('res_model', '=', self.res_model), ('res_model', '=', False)],
                'suggested_next_type_ids': ['|', '|', ('res_model', 'in', self.many2one_model_ids.mapped('model')), ('res_model', '=', self.res_model), ('res_model', '=', False)],
            }
        }

    @api.depends('nrp_chaining_type')
    def _compute_nrp_suggested_next_type_ids(self):
        """suggested_next_type_ids and triggered_next_type_id should be mutually exclusive"""
        for activity_type in self:
            if activity_type.nrp_chaining_type == 'trigger':
                activity_type.nrp_suggested_next_type_ids = False

    def _inverse_nrp_suggested_next_type_ids(self):
        for activity_type in self:
            if activity_type.nrp_suggested_next_type_ids:
                activity_type.nrp_chaining_type = 'suggest'

    @api.depends('res_model')
    def _compute_many2one_model_ids(self):
        for record in self:
            if record.res_model:
                ralations = record.env['ir.model'].search([('model', '=', record.res_model)]).field_id.filtered(lambda f: f.ttype == 'many2one').mapped('relation')
                model_ids = record.env['ir.model'].search([('model', 'in', ralations)])
                #raise ValidationError(models)
                record.many2one_model_ids = model_ids
            else:
                record.many2one_model_ids = False

    @api.depends('nrp_chaining_type')
    def _compute_nrp_triggered_next_type_id(self):
        for activity_type in self:
            if activity_type.nrp_chaining_type == 'suggest':
                activity_type.nrp_triggered_next_type_id = False

    def _inverse_nrp_triggered_next_type_id(self):
        for activity_type in self:
            if activity_type.nrp_triggered_next_type_id:
                activity_type.nrp_chaining_type = 'trigger'
            else:
                activity_type.nrp_chaining_type = 'suggest'

    @api.depends('nrp_triggered_next_type_id', 'nrp_triggered_next_type_id.res_model', 'res_model')
    def _compute_nrp_next_activity_res_model(self):
        for record in self:
            if record.nrp_triggered_next_type_id.res_model and not record.res_model:
                raise ValidationError("Pour avoir un modèle pour la prochaine activité, il faut que le modèle de ce type d'activité soit défini")
            else:
                record.nrp_next_activity_res_model = record.nrp_triggered_next_type_id.res_model

    @api.depends('triggered_next_type_id', 'triggered_next_type_id.res_model', 'res_model')
    def _compute_next_activity_res_model(self):
        for record in self:
            if record.triggered_next_type_id.res_model and not record.res_model:
                #record.next_activity_res_model = 'TEST2'
                raise ValidationError("il faut choisir d'abord un modèle pour ce type d'activité")
            else:
                record.next_activity_res_model = record.triggered_next_type_id.res_model

    @api.depends('nrp_next_activity_res_model', 'res_model')
    def _compute_required_nrp_field(self):
        for record in self:
            if record.res_model != record.nrp_next_activity_res_model and record.nrp_next_activity_res_model:
                record.required_nrp_field = True
            else:
                record.required_nrp_field = False

    @api.depends('next_activity_res_model', 'res_model')
    def _compute_required_field(self):
        for record in self:
            if record.res_model != record.next_activity_res_model and record.next_activity_res_model:
                record.required_field = True
            else:
                record.required_field = False
