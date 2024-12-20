from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ProjectAddFields(models.Model):
    _inherit = "project.task"

    change_description = fields.Text(string="Change Description")
    testing_summary = fields.Text(string="Testing Summary")
    code_review_notes = fields.Text(string="Code Review Notes")
    attachments = fields.Binary(string="Attachments")
    department = fields.Selection(
        [('marketing', 'Marketing'), ('sales', 'Sales'), ('it', 'IT'), ('academic', 'Academic'), ('crash', 'Crash'),
         ('digital', 'Digital'), ('accounts', 'Accounts'), ('hr', 'HR'), ('operations', 'Operations')],
        string="Department")
    status = fields.Selection([('new_request', 'New Request'), ('testing', 'Testing'), ('code_review', 'Code Review'),
                               ('approval_pending', 'Approval Pending'),
                               ('ready_for_production', 'Ready for Production'), ('production', 'Production'),
                               ('closed', 'Closed'), ('rejected', 'Rejected')], tracking=1, string="Status", default='new_request')
    approver_id = fields.Many2one('res.users', string="Approver",
                                  default=lambda self: self.env.user.employee_id.parent_id.user_id)

    def action_sent_to_test(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Testing')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.status = 'testing'

    def action_sent_to_code_review(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Code Review')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.status = 'code_review'

    def action_sent_to_approval(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Approval Pending')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.status = 'approval_pending'

    def action_ready_for_production(self):
        if self.approver_id:
            if self.env.user.id == self.approver_id.id:
                stage = self.env['project.task.type'].sudo().search([('name', '=', 'Ready for Production')], limit=1)
                if stage:
                    self.stage_id = stage.id
                self.status = 'ready_for_production'
            else:
                raise ValidationError(_('Only the Head of Department can approve this action.'))
        else:
            raise ValidationError(_('Please Add Approver.'))
    def action_production(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Production')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.status = 'production'

    def action_ticket_closed(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Closed')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.status = 'closed'

    def action_ticket_rejection(self):
        if self.approver_id:
            if self.env.user.id == self.approver_id.id:
                stage = self.env['project.task.type'].sudo().search([('name', '=', 'Rejected')], limit=1)
                if stage:
                    self.stage_id = stage.id
                self.status = 'rejected'
            else:
                raise ValidationError(_('Only the Head of Department can reject this action.'))
        else:
            raise ValidationError(_('Please Add Approver.'))
