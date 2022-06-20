# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context
from collections import defaultdict
from dateutil.relativedelta import relativedelta

class MailActivity(models.Model):
    _inherit = 'mail.activity'

    def _get_model_selection(self):
        return super(MailActivity, self)._get_model_selection()

    nrp = fields.Boolean(string='NRP')
    nrp_chaining_type = fields.Selection(related='activity_type_id.nrp_chaining_type', readonly=True)
    nrp_mail_template_ids = fields.Many2many(related='activity_type_id.nrp_mail_template_ids', readonly=True)
    nrp_next_activity_type_id = fields.Many2one(related='activity_type_id.nrp_triggered_next_type_id', readonly=True)
    nrp_next_activity_res_model = fields.Selection(selection=_get_model_selection, string='Related next NRP Document Model', index=True, related='nrp_next_activity_type_id.res_model', compute_sudo=True, store=True, readonly=True)
    nrp_next_activity_res_id = fields.Many2oneReference(string='Related NRP Document ID', index=True, compute="_compute_nrp_next_activity_res_id", required=True, model_field='nrp_next_activity_res_model')
    next_activity_type_id = fields.Many2one(related='activity_type_id.triggered_next_type_id', readonly=True)
    next_activity_res_model = fields.Selection(selection=_get_model_selection, string='Related next Document Model', index=True, related='next_activity_type_id.res_model', compute_sudo=True, store=True, readonly=True)
    next_activity_res_id = fields.Many2oneReference(string='Related Document ID', index=True, compute="_compute_next_activity_res_id", required=True, model_field='nrp_next_activity_res_model')
    from_nrp = fields.Boolean(string='FROM NRP')
    activity_type_id = fields.Many2one(domain=[])

    res_id_origin = fields.Integer(string='Enregistrement d\'origine')
    res_model_origin = fields.Selection(related='previous_activity_type_id.res_model', string="Modèle", store=True)
    required_field = fields.Boolean(string='Champs Invisible', compute='_compute_required_field')
    res_field = fields.Many2one('ir.model.fields', string='Champs', domain="[('model_id', '=', res_model_origin), ('relation', '=', res_model)]")

    nrp_recommended_activity_type_id = fields.Many2one('mail.activity.type', string="NRP Recommended Activity Type")

    @api.depends('previous_activity_type_id', 'previous_activity_type_id.res_model', 'res_model')
    def _compute_required_field(self):
        for record in self:
            if record.res_model and record.previous_activity_type_id.res_model and record.previous_activity_type_id.res_model != record.res_model:
                record.required_field = True
            else:
                record.required_field = False

    def _compute_nrp_next_activity_res_id(self):
        for record in self:
            if record.res_model and record.nrp_next_activity_res_model and record.res_model != record.nrp_next_activity_res_model:
                related_object = record.env[record.res_model].browse(record.res_id)
                related_object_next_name = related_object.activity_type_id.nrp_next_activity_res_field.name
                record.nrp_next_activity_res_id = related_object[related_object_next_name].id
            else:
                record.nrp_next_activity_res_id = record.res_id

    def _compute_next_activity_res_id(self):
        for record in self:
            if record.res_model and record.next_activity_res_model and record.next_activity_res_model != record.res_model:
                related_object = record.env[record.res_model].browse(record.res_id)
                related_object_next_name = related_object.activity_type_id.next_activity_res_field.name
                record.next_activity_res_id = related_object[related_object_next_name].id
            else:
                record.next_activity_res_id = record.res_id

    def action_feedback(self, feedback=False, nrp=False, attachment_ids=None):
        if nrp:
            for nrp_mail_template_id in self.nrp_mail_template_ids:
                mail_id = nrp_mail_template_id.sudo().send_mail(self.res_id, force_send=True)
            messages, next_activities = self.with_context(nrp=True)._action_done_nrp(feedback=feedback, attachment_ids=attachment_ids)
            return messages.ids and messages.ids[0] or False
                
        return super(MailActivity, self).action_feedback(feedback, attachment_ids)

    def _calculate_date_deadline(self, activity_type):
        if self._context.get('nrp'):
            base = fields.Date.context_today(self)
            if activity_type.nrp_delay_from == 'previous_activity' and 'activity_previous_deadline' in self.env.context:
                base = fields.Date.from_string(self.env.context.get('activity_previous_deadline'))
            return base + relativedelta(**{activity_type.nrp_delay_unit: activity_type.nrp_delay_count})
        else:
            return super(MailActivity, self)._calculate_date_deadline(activity_type)

    def _onchange_nrp_previous_activity_type_id(self):
        for record in self:
            if record.previous_activity_type_id.nrp_triggered_next_type_id:
                record.activity_type_id = record.previous_activity_type_id.nrp_triggered_next_type_id

    def _prepare_next_activity_values(self):
        """ Prepare the next activity values based on the current activity record and applies _onchange methods
        :returns a dict of values for the new activity
        """
        self.ensure_one()
        vals = self.default_get(self.fields_get())

        if self.nrp:
            if not self.nrp_next_activity_res_id:
                related_object = self.env[self.res_model].browse(self.res_id)
                related_object_next_name = related_object.activity_type_id.nrp_next_activity_res_field.name
                raise ValidationError("Le champs '%s' n'est pas renseigné" %(related_object.activity_type_id.nrp_next_activity_res_field.field_description))

            res_id = self.nrp_next_activity_res_id
            res_model = self.nrp_next_activity_res_model

        elif not self.nrp:
            if not self.nrp_next_activity_res_id:
                related_object = self.env[self.res_model].browse(self.res_id)
                related_object_next_name = related_object.activity_type_id.next_activity_res_field.name
                raise ValidationError("Le champs '%s' n'est pas renseigné" %(related_object.activity_type_id.nrp_next_activity_res_field.field_description))

            res_id = self.next_activity_res_id
            res_model = self.next_activity_res_model

        else:
            res_id = self.res_id
            res_model = self.res_model

        vals.update({
            'previous_activity_type_id': self.activity_type_id.id,
            'res_id': res_id,
            'res_model': res_model,
            'res_model_id': self.env['ir.model']._get(res_model).id,
        })
        virtual_activity = self.new(vals)
        
        if self.nrp:
            virtual_activity._onchange_nrp_previous_activity_type_id()
            virtual_activity._onchange_activity_type_id()
        else:
            virtual_activity._onchange_previous_activity_type_id()
            virtual_activity._onchange_activity_type_id()

        return virtual_activity._convert_to_write(virtual_activity._cache)

    def _action_done_nrp(self, feedback=False, attachment_ids=None):
        self.nrp = True
        # marking as 'done'
        messages = self.env["mail.message"]
        next_activities_values = []
        for activity in self:
            # extract value to generate next activities
            if activity.nrp_chaining_type == 'trigger':
                vals = activity.with_context(activity_previous_deadline=activity.date_deadline)._prepare_next_activity_values()
                next_activities_values.append(vals)

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            activity.done = True
            activity.active = False
            activity.date_done = fields.Date.today()
            record.message_post_with_view(
                "mail.message_activity_done",
                values={
                    "activity": activity,
                    "feedback": feedback,
                    "display_assignee": activity.user_id != self.env.user,
                },
                subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                    "mail.mt_activities"
                ),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[
                    Command.link(attachment_id) for attachment_id in attachment_ids
                ]
                if attachment_ids
                else [],
            )
            messages |= record.message_ids[0]

        next_activities = self.env["mail.activity"].create(next_activities_values)

        return messages, next_activities

    @api.onchange('nrp_recommended_activity_type_id', 'recommended_activity_type_id', 'res_field')
    def _onchange_recommended_activity_type_id(self):
        if self.from_nrp:
            if self.nrp_recommended_activity_type_id:
                self.activity_type_id = self.nrp_recommended_activity_type_id
        else:
            super(MailActivity, self)._onchange_recommended_activity_type_id()

        
        if not self.res_id_origin:
            self.res_id_origin = self.res_id

        if self.recommended_activity_type_id:            
            self.res_model = self.activity_type_id.res_model
            self.res_model_id = self.env['ir.model']._get(self.res_model).id
            
            if self.previous_activity_type_id.res_model != self.res_model:
                related_object = self.env[self.previous_activity_type_id.res_model].browse(self.res_id_origin)
                related_object_next_name = self.res_field.name
                self.res_id = related_object[related_object_next_name].id
                if not self.res_id:
                    raise ValidationError("Le champs '%s' n'est pas renseigné" %(self.res_field.field_description))
            else:
                self.res_id = self.res_id_origin

    def action_nrp_feedback_schedule_next(self, feedback=False):
        ctx = dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=self.activity_type_id.id,
            activity_previous_deadline=self.date_deadline,
            default_res_id=self.res_id,
            default_res_model=self.res_model,
            default_from_nrp=True,
        )
        messages, next_activities = self._action_done_nrp(feedback=feedback)  # will unlink activity, dont access self after that
        if next_activities:
            return False
        return {
            'name': _('Schedule an Activity'),
            'context': ctx,
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('previous_activity_type_id')
    def _compute_has_recommended_activities(self):
        for record in self:
            if record.from_nrp:
                record.has_recommended_activities = bool(record.previous_activity_type_id.nrp_suggested_next_type_ids)
            else:
                record.has_recommended_activities = bool(record.previous_activity_type_id.suggested_next_type_ids)
            