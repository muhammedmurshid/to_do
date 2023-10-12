from odoo import fields, models, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


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

    batch_id = fields.Many2one('logic.base.batch', string='Batch')
    dead_line = fields.Date(string='Dead Line')
    tags_id = fields.Many2many('project.tags', string='Tags')
    current_emp_id = fields.Many2one('hr.employee', string='Current Employee',
                                     default=lambda self: self.env.user.employee_id)
    coworkers_ids = fields.Many2many('res.users', string='Co-Workers')

    assigned_to = fields.Many2one('res.users', string='Assigned To', domain=[('faculty_check', '=', False)],
                                  readonly=False, required=True, )

    def _compute_get_employee(self):
        print('kkkll')
        user_crnt = self.env.user.id

        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('to_do.to_do_worker_id'):
            self.make_visible_employee = False

        else:
            self.make_visible_employee = True

    make_visible_employee = fields.Boolean(string="User", default=True, compute='_compute_get_employee')

    def _compute_get_crash_coordinator(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('to_do.to_do_coordinator'):
            self.user_crash_coordinator = True
        else:
            self.user_crash_coordinator = False

    user_crash_coordinator = fields.Boolean(string="User", compute='_compute_get_crash_coordinator')

    def _compute_get_crash_head(self):
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if res_user.has_group('to_do.to_do_crash_head'):
            self.user_crash_head = True

        else:
            self.user_crash_head = False

    user_crash_head = fields.Boolean(string="Crash Head", compute='_compute_get_crash_head')

    @api.model
    def _compute_get_account_head(self):
        print('jksha')
        res_user = self.env['res.users'].search([('id', '=', self.env.user.id)])
        print(res_user.has_group, 'group')
        if res_user.has_group('to_do.to_do_organizer'):
            self.user_accounts_head = True
        elif res_user.has_group('to_do.to_do_crash_head'):
            self.user_accounts_head = True
            print('ya')
        else:
            self.user_accounts_head = False
            print('no')

    user_accounts_head = fields.Boolean(string="User", compute='_compute_get_account_head')

    # @api.depends('name')
    # def compute_assign_to(self):
    #     if self.make_visible_employee == False:
    #         self.assigned_to = self.env.user

    @api.constrains('state')
    def chatt(self):
        if self.state == 'draft':
            msg = _(
                "Stage Changed to Draft",
            )
            self.message_post(body=msg)

        elif self.state == 'task_sent':
            msg = _(
                "Stage Changed to Task Sent",
            )
            self.message_post(body=msg)
        elif self.state == 'on_hold':
            msg = _(
                "Stage Changed to On Hold",
            )
            self.message_post(body=msg)
        elif self.state == 'in_progress':
            msg = _(
                "Stage Changed to In Progress",
            )
            self.message_post(body=msg)
        elif self.state == 'completed':
            msg = _(
                "Stage Changed to Completed",
            )
            self.message_post(body=msg)
        elif self.state == 'cancelled':
            msg = _(
                "Stage Changed to Cancelled",
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
        print(self.coworkers_ids, 'oooo')
        self.activity_schedule('to_do.activity_to_do_activity_custom', user_id=self.assigned_to.id,
                               note=f'Check on your tasks {self.assigned_to.name}')
        users = self.env['res.users'].search([('id', 'in', self.coworkers_ids.ids)])
        for i in users:
            print(i.name , 'name')
            self.activity_schedule('to_do.activity_to_do_activity_custom', user_id=i.id,
                                   note=f'Check on your tasks {i.name}')

        self.write({'state': 'task_sent'})

    def auto_activity_due_admin(self):
        ss = self.env['to_do.tasks'].search([])
        current_datetime = date.today()

        for i in ss:
            if i.dead_line:
                if current_datetime > i.dead_line:
                    if i.state in 'task_sent' or i.state in 'in_progress':
                        users = ss.env.ref('to_do.to_do_admin').users
                        for rec in users:
                            i.activity_schedule('to_do.activity_to_do_activity_custom', user_id=rec.id,
                                                note=f'Due TO DO Task')

    def _compute_display_name(self):
        for rec in self:
            if rec.project_id:
                rec.display_name = rec.name + ' - ' + rec.project_id.name
            else:
                rec.display_name = rec.name + ' - ' + 'To Do Task'

    def auto_due_tasks_remove_from_admins(self):
        ss = self.env['to_do.tasks'].search([])

        for i in ss:
            if i.state in 'completed' or i.state in 'cancelled' or i.state in 'on_hold':
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

    def action_re_assign_to_do_work(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'reassign.to_do.worker',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'name': 'Re-Assign',

        }

    # Time sheet fields
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    total_time = fields.Float(string='Total Duration')
    rating = fields.Selection([
        ('0', 'None'), ('1', 'Poor'), ('2', 'Fair'), ('3', 'Good'), ('4', 'Very Good'), ('5', 'Excellent')],
    )

    @api.depends('from_time', 'to_time')
    def _compute_time_difference(self):
        for record in self:
            if record.from_time and record.to_time:
                # Convert the datetime fields to datetime objects
                date_str1 = record.from_time.strftime("%Y-%m-%d %H:%M:%S")
                date_str2 = record.to_time.strftime("%Y-%m-%d %H:%M:%S")

                # Convert the strings back to datetime objects
                date_time1 = datetime.strptime(date_str1, "%Y-%m-%d %H:%M:%S")
                date_time2 = datetime.strptime(date_str2, "%Y-%m-%d %H:%M:%S")

                # Calculate the time difference
                time_diff = date_time2 - date_time1

                # Extract days, hours, and minutes
                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                # Format the result as a string
                time_difference_str = f"{days} days, {hours} hours, {minutes} minutes"
                record.total_time = time_difference_str
            else:
                record.total_time = False


class ReassignToDoWorker(models.TransientModel):
    _name = 'reassign.to_do.worker'

    assign_to_new = fields.Many2one('res.users', string='Assign To New Worker', domain=[('faculty_check', '=', False)])

    def action_assign(self):
        to_do = self.env['to_do.tasks'].search([('id', '=', self.env.context['active_id'])])
        if self.assign_to_new:
            to_do.assigned_to = self.assign_to_new
            to_do.state = 'task_sent'
            to_do.activity_schedule('to_do.activity_to_do_activity_custom', user_id=self.assign_to_new.id,
                                    note=f'Check on your tasks {self.assign_to_new.name}')
        else:
            raise UserError('Please Select User')
