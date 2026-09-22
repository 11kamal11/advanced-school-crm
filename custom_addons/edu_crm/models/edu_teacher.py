from odoo import fields, models, api


class EduTeacher(models.Model):
    _name = 'edu.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    employee_code = fields.Char(readonly=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', string='Contact')
    user_id = fields.Many2one('res.users', string='Related User',
                               help='Backend user account this teacher logs in with, used for record-level access.')
    image = fields.Image(max_width=1024, max_height=1024)
    email = fields.Char(required=True, tracking=True)
    phone = fields.Char()
    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'),
    ])
    date_of_birth = fields.Date()
    address = fields.Text()
    qualification = fields.Char()
    experience_years = fields.Integer()
    specialization = fields.Char()
    bio = fields.Html(help='Shown on the public faculty profile page.')
    date_of_joining = fields.Date(default=fields.Date.context_today)
    subject_ids = fields.Many2many('edu.subject', string='Subjects')
    class_ids = fields.One2many('edu.class', 'class_teacher_id', string='Classes (as Class Teacher)')
    subject_count = fields.Integer(compute='_compute_counts')
    class_count = fields.Integer(compute='_compute_counts')
    leave_count = fields.Integer(compute='_compute_leave_count')
    state = fields.Selection([
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('resigned', 'Resigned'),
    ], default='active', required=True, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _email_company_uniq = models.Constraint(
        'unique(email, company_id)',
        'A teacher with this email already exists in this company.',
    )
    _employee_code_uniq = models.Constraint('unique(employee_code)', 'This employee code already exists.')

    @api.depends('subject_ids', 'class_ids')
    def _compute_counts(self):
        for rec in self:
            rec.subject_count = len(rec.subject_ids)
            rec.class_count = len(rec.class_ids)

    def _compute_leave_count(self):
        for rec in self:
            rec.leave_count = self.env['edu.leave.request'].search_count(
                [('teacher_id', '=', rec.id)]
            )

    def action_view_teacher_leaves(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Leave Requests',
            'res_model': 'edu.leave.request',
            'view_mode': 'list,form',
            'domain': [('teacher_id', '=', self.id)],
            'context': {'default_teacher_id': self.id, 'default_applicant_type': 'teacher'},
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('employee_code', 'New') == 'New':
                vals['employee_code'] = self.env['ir.sequence'].sudo().next_by_code('edu.teacher') or 'New'
        return super().create(vals_list)

    def action_set_on_leave(self):
        self.write({'state': 'on_leave'})

    def action_set_active(self):
        self.write({'state': 'active'})

    def action_set_resigned(self):
        self.write({'state': 'resigned'})

