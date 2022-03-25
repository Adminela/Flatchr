# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CalendarEvent(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        if self.env.context.get('default_task_id'):
            self = self.with_context(
                default_res_model='project.task', #res_model seems to be lost without this
                default_res_model_id=self.env.ref('project.model_project_task').id,
                default_res_id=self.env.context['default_task_id']
            )

        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to opportunity id (aka creating meeting from lead chatter)
        if 'task_id' not in defaults:
            res_model = defaults.get('res_model', False) or self.env.context.get('default_res_model')
            res_model_id = defaults.get('res_model_id', False) or self.env.context.get('default_res_model_id')
            if (res_model and res_model == 'project.task') or (res_model_id and self.env['ir.model'].sudo().browse(res_model_id).model == 'project.task'):
                defaults['task_id'] = defaults.get('res_id', False) or self.env.context.get('default_res_id', False)

        return defaults

    def _compute_is_highlighted(self):
        super(CalendarEvent, self)._compute_is_highlighted()
        task_id = self.env.context.get('active_id')
        if self.env.context.get('active_model') == 'project.task' and task_id:
            for event in self:
                if event.task_id.id == task_id:
                    event.is_highlighted = True


    task_id = fields.Many2one('project.task', string="Tâche", index=True, ondelete='set null')