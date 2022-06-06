# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context
from collections import defaultdict


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    nrp = fields.Boolean(string='NRP', tracking=True)
    nrp_previous_activity_type_id = fields.Many2one('mail.activity.type', string='NRP Previous Activity Type', readonly=True)

    def action_feedback(self, feedback=False, nrp=False, attachment_ids=None):
        if nrp:
            self.nrp = True
            self = self.with_context(clean_context(self.env.context))
            messages, next_activities = self._action_done_nrp(feedback=feedback, attachment_ids=attachment_ids)
            return messages.ids and messages.ids[0] or False
                
        return super(MailActivity, self).action_feedback(feedback, attachment_ids)

    def _action_done_nrp(self, feedback=False, attachment_ids=None):
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            # extract value to generate next activities
            vals = activity.with_context(activity_previous_deadline=activity.date_deadline)._prepare_next_activity_values_nrp()
            next_activities_values.append(vals)

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={
                    'activity': activity,
                    'feedback': feedback,
                    'display_assignee': activity.user_id != self.env.user
                },
                subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[Command.link(attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
            )

            # Moving the attachments in the message
            # TODO: Fix void res_id on attachment when you create an activity with an image
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            if message_attachments:
                message_attachments.write({
                    'res_id': activity_message.id,
                    'res_model': activity_message._name,
                })
                activity_message.attachment_ids = message_attachments
            messages |= activity_message

        next_activities = self.env['mail.activity'].create(next_activities_values)
        self.unlink()  # will unlink activity, dont access `self` after that

        return messages, next_activities

    def _prepare_next_activity_values_nrp(self):
        """ Prepare the next activity values based on the current activity record and applies _onchange methods
        :returns a dict of values for the new activity
        """
        self.ensure_one()
        vals = self.default_get(self.fields_get())

        vals.update({
            'previous_activity_type_id': self.activity_type_id.id,
            'res_id': self.res_id,
            'res_model': self.res_model,
            'res_model_id': self.env['ir.model']._get(self.res_model).id,
        })
        virtual_activity = self.new(vals)
        virtual_activity._onchange_previous_activity_type_id()
        virtual_activity._onchange_nrp_previous_activity_type_id()
        raise ValidationError("NRP : %s" %(self.activity_type_id))
        return virtual_activity._convert_to_write(virtual_activity._cache)

    def _onchange_nrp_activity_type_id(self):
        if self.nrp_activity_type_id:
            if self.nrp_activity_type_id.summary:
                self.summary = self.nrp_activity_type_id.summary
            self.date_deadline = self._calculate_date_deadline(self.nrp_activity_type_id)
            self.user_id = self.nrp_activity_type_id.default_user_id or self.env.user
            if self.nrp_activity_type_id.default_note:
                self.note = self.nrp_activity_type_id.default_note

    def _onchange_nrp_previous_activity_type_id(self):
        for record in self:
            if record.nrp_previous_activity_type_id.nrp_triggered_next_type_id:
                raise ValidationError("HELLO : %s" %(record.nrp_previous_activity_type_id.nrp_triggered_next_type_id))
                record.activity_type_id = record.nrp_previous_activity_type_id.nrp_triggered_next_type_id
