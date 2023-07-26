from odoo import fields, models, api, _
from datetime import datetime, date


class ToDoTasks(models.Model):
    _name = 'to_do.tasks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Task'

    name = fields.Char(string='Name', required=True)
    priority = fields.Selection([
        ('normal', 'Normal'), ('urgent', 'Urgent')
    ], string='Priority', default='normal')
    kanban_state = fields.Selection([
        ('progress', 'In Progress'), ('done', 'Done'), ('blocked', 'Blocked')
    ], string='Status')
    state = fields.Selection([
        ('draft', 'Draft'), ('task_sent', 'Task Sent'), ('in_progress', 'In Progress'), ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    project_id = fields.Many2one('project.project', string='Project')
    assigned_to = fields.Many2one('res.users', string='Assigned To', required=True)
    dead_line = fields.Date(string='Dead Line')
    tags_id = fields.Many2many('project.tags', string='Tags')

    @api.constrains('state')
    def chatt(self):
        msg = _(
            "Stage Changed" + " to " + self.state,
        )
        self.message_post(body=msg)

    def action_done(self):
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        activity_id.action_feedback(feedback=f'Completed')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        other_activity_ids.unlink()
        self.write({'state': 'completed'})

    def action_cancel(self):
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        activity_id.action_feedback(feedback=f'Cancelled')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        other_activity_ids.unlink()
        self.write({'state': 'cancelled'})

    def action_in_progress(self):
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        activity_id.action_feedback(feedback=f'In Progress')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        other_activity_ids.unlink()
        self.write({'state': 'in_progress'})

    def action_on_hold(self):
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        activity_id.action_feedback(feedback=f'On Hold')
        other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
            'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
        other_activity_ids.unlink()
        self.write({'state': 'on_hold'})

    def action_task_sent(self):
        self.activity_schedule('to_do.activity_to_do_activity_custom', user_id=self.assigned_to.id,
                               note=f'Check on your tasks {self.assigned_to.name}')
        self.write({'state': 'task_sent'})

    def auto_activity_due_admin(self):
        ss = self.env['to_do.tasks'].search([])
        current_datetime = date.today()

        for i in ss:
            if i.dead_line:
                if current_datetime > i.dead_line:
                    if i.state in 'task_sent' or i.state in 'in_progress' or i.state in 'on_hold':
                        users = ss.env.ref('to_do.to_do_admin').users
                        for rec in users:
                            i.activity_schedule('to_do.activity_to_do_activity_custom', user_id=rec.id,
                                                note=f'Due Task')

    def auto_due_tasks_remove_from_admins(self):
        ss = self.env['to_do.tasks'].search([])

        for i in ss:
            if i.state in 'completed' or i.state in 'cancelled':
                activity_id = self.env['mail.activity'].search(
                    [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                        'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
                if i.state == 'completed':
                    activity_id.action_feedback(feedback=f'Tasks are complete')
                elif i.state == 'cancelled':
                    activity_id.action_feedback(feedback=f'Tasks are cancelled')
                other_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), (
                    'activity_type_id', '=', self.env.ref('to_do.activity_to_do_activity_custom').id)])
                other_activity_ids.unlink()
