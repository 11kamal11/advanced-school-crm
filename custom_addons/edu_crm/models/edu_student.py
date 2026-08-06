from dateutil.relativedelta import relativedelta

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EduStudent(models.Model):
    _name = 'edu.student'
    _description = 'Student'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    student_code = fields.Char(readonly=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', string='Contact')
    image = fields.Binary()
    email = fields.Char()
    phone = fields.Char()
    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'),
    ])
    date_of_birth = fields.Date()
    age = fields.Integer(compute='_compute_age', store=True)
    blood_group = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'), ('o+', 'O+'), ('o-', 'O-'),
    ])
    address = fields.Text()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string='State/Province')
    country_id = fields.Many2one('res.country')

    class_id = fields.Many2one('edu.class', tracking=True)
    roll_number = fields.Integer()
    academic_year_id = fields.Many2one('edu.academic.year')
    admission_date = fields.Date(default=fields.Date.context_today)

    guardian_ids = fields.Many2many('edu.guardian', string='Guardians')
    applicant_id = fields.Many2one('edu.applicant', readonly=True, copy=False)

    attendance_line_ids = fields.One2many('edu.attendance.line', 'student_id')
    exam_result_ids = fields.One2many('edu.exam.result', 'student_id')
    fee_ids = fields.One2many('edu.fee', 'student_id')
    leave_request_ids = fields.One2many('edu.leave.request', 'student_id')

    attendance_percentage = fields.Float(compute='_compute_attendance_percentage', store=True)
    total_fees_due = fields.Float(compute='_compute_total_fees_due')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
        ('alumni', 'Alumni'),
    ], default='draft', required=True, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _student_code_uniq = models.Constraint('unique(student_code)', 'This student code already exists.')

    @api.constrains('date_of_birth')
    def _check_dob(self):
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth > fields.Date.context_today(rec):
                raise ValidationError('Date of birth cannot be in the future.')

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.age = relativedelta(today, rec.date_of_birth).years if rec.date_of_birth else 0

    @api.depends('attendance_line_ids.status')
    def _compute_attendance_percentage(self):
        for rec in self:
            lines = rec.attendance_line_ids
            total = len(lines)
            present = len(lines.filtered(lambda line_: line_.status in ('present', 'late')))
            rec.attendance_percentage = (present / total * 100) if total else 0.0

    @api.depends('fee_ids.balance')
    def _compute_total_fees_due(self):
        for rec in self:
            rec.total_fees_due = sum(rec.fee_ids.mapped('balance'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('student_code', 'New') == 'New':
                vals['student_code'] = self.env['ir.sequence'].sudo().next_by_code('edu.student') or 'New'
        return super().create(vals_list)

    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = f'/my/children/{rec.id}'

    def action_activate(self):
        self.write({'state': 'active'})

    def action_suspend(self):
        self.write({'state': 'suspended'})

    def action_graduate(self):
        self.write({'state': 'graduated'})

    def action_alumni(self):
        self.write({'state': 'alumni'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
