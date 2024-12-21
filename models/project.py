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
                               ('closed', 'Closed'), ('rejected', 'Rejected')], tracking=1, string="Status",
                              default='new_request')
    approver_id = fields.Many2one('res.users', string="Approver",
                                  default=lambda self: self.env.user.employee_id.parent_id.user_id)
    project_type = fields.Selection(
        [('changing_management', 'Changing Management'), ('patching_management', 'Patching Management')],
        string="Project Type", )
    server_name = fields.Selection([('odoo_server', 'Odoo Server'), ('punching_server', 'Punching Server')],
                                   string="Server Name")
    server_id = fields.Char(string="Server ID")
    version_from = fields.Char(string="Version (From)")
    version_to = fields.Char(string="Version (To)")
    patch_name = fields.Char(string="Patch Name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    comments = fields.Text(string="Comments")
    patching_status = fields.Selection(
        [('request_logged', 'Request Logged'), ('pending_approval', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'),
         ('deployment_in_progress', 'Deployment In progress'), ('completed', 'Completed')], string="Patch Status")

    @api.onchange('project_type')
    def _onchange_project_type(self):
        if self.project_type == 'changing_management':
            self.server_name = False
            self.server_id = False
            self.version_to = False
            self.version_from = False
            self.patch_name = False
            self.start_date = False
            self.end_date = False
            self.comments = False
        if self.project_type == 'patching_management':
            self.testing_summary = False
            self.code_review_notes = False
            self.change_description = False

    @api.onchange('patching_status','project_type')
    def _onchange_patching(self):
        if self.project_type:
            if self.project_type == 'patching_management':
                print('hi')
                self.status = False
                if not self.patching_status:
                    self.patching_status = 'request_logged'
            if self.project_type == 'changing_management':
                self.patching_status = False
                if not self.status:
                    self.status = 'new_request'

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

    def action_patch_sent_to_approve(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Pending Approval')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.patching_status = 'pending_approval'

    def action_head_approve(self):
        if self.approver_id:
            if self.env.user.id == self.approver_id.id:
                stage = self.env['project.task.type'].sudo().search([('name', '=', 'Approved')], limit=1)
                if stage:
                    self.stage_id = stage.id
                self.patching_status = 'approved'
            else:
                raise ValidationError(_('Only the Head of Department can approve this action.'))

        else:
            raise ValidationError(_('Please Add Approver.'))

    def action_head_refuse(self):
        if self.approver_id:
            if self.env.user.id == self.approver_id.id:
                stage = self.env['project.task.type'].sudo().search([('name', '=', 'Rejected')], limit=1)
                if stage:
                    self.stage_id = stage.id
                self.patching_status = 'rejected'
            else:
                raise ValidationError(_('Only the Head of Department can reject this action.'))
        else:
            raise ValidationError(_('Please Add Approver.'))

    def action_deployment_in_progress(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Deployment in Progress')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.patching_status = 'deployment_in_progress'

    def action_completed(self):
        stage = self.env['project.task.type'].sudo().search([('name', '=', 'Completed')], limit=1)
        if stage:
            self.stage_id = stage.id
        self.patching_status = 'completed'
