from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class EduLeaveRequest(models.Model):
    _name = 'edu.leave.request'
    _description = 'Leave Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'create_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    applicant_type = fields.Selection([
        ('student', 'Student'), ('teacher', 'Teacher'),
    ], default='student', required=True)
    student_id = fields.Many2one('edu.student')
    teacher_id = fields.Many2one('edu.teacher')
    leave_type = fields.Selection([
        ('sick', 'Sick'), ('personal', 'Personal'), ('family', 'Family'),
        ('medical', 'Medical'), ('other', 'Other'),
    ], default='sick', required=True, tracking=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    days = fields.Integer(compute='_compute_days', store=True)
    reason = fields.Text(required=True)
    attachment = fields.Binary()
    attachment_name = fields.Char()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', required=True, tracking=True)
    approver_id = fields.Many2one('res.users', readonly=True)
    review_date = fields.Datetime(readonly=True)
    rejection_reason = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('applicant_type', 'student_id', 'teacher_id')
    def _check_applicant(self):
        for rec in self:
            if rec.applicant_type == 'student' and not rec.student_id:
                raise ValidationError('Please select the student this leave request is for.')
            if rec.applicant_type == 'teacher' and not rec.teacher_id:
                raise ValidationError('Please select the teacher this leave request is for.')

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_to < rec.date_from:
                raise ValidationError('The end date cannot be before the start date.')

    @api.depends('date_from', 'date_to')
    def _compute_days(self):
        for rec in self:
            rec.days = (rec.date_to - rec.date_from).days + 1 if rec.date_from and rec.date_to else 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].sudo().next_by_code('edu.leave.request') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        self.write({'state': 'submitted'})

    def _check_not_self_review(self):
        for rec in self:
            if rec.applicant_type == 'teacher' and rec.teacher_id.user_id.id == self.env.user.id:
                raise UserError('You cannot approve or reject your own leave request.')

    def action_approve(self):
        self._check_not_self_review()
        self.write({'state': 'approved', 'approver_id': self.env.user.id, 'review_date': fields.Datetime.now()})
        self._send_status_email()

    def action_reject(self):
        self._check_not_self_review()
        self.write({'state': 'rejected', 'approver_id': self.env.user.id, 'review_date': fields.Datetime.now()})
        self._send_status_email()

    def _send_status_email(self):
        template = self.env.ref('edu_crm.mail_template_leave_status', raise_if_not_found=False)
        if not template:
            return
        for leave in self:
            if leave.applicant_type == 'student' and leave.student_id.guardian_ids.mapped('email'):
                template.send_mail(leave.id, force_send=False)

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = '/my/leave-requests'
