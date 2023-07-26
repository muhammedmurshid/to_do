from odoo import fields, models, api, _


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
        ('draft', 'Draft'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('cancelled', 'Cancelled')
    ], string='Status', default='draft')
    project_id = fields.Many2one('project.project', string='Project')
    assigned_to = fields.Many2one('res.users', string='Assigned To')
    dead_line = fields.Date(string='Dead Line')
    tags_id = fields.Many2many('project.tags', string='Tags')

    @api.constrains('state')
    def chatt(self):
        msg = _(
            "Stage Changed" + " to " + self.state,
        )
        self.message_post(body=msg)

    def action_done(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_in_progress(self):
        self.write({'state': 'in_progress'})
