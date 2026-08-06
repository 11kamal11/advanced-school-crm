from odoo import fields, models, api


class EduTeacher(models.Model):
    _name = 'edu.teacher'
    _description = 'Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin']
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    employee_code = fields.Char(readonly=True, copy=False, default='New')
    partner_id = fields.Many2one('res.partner', string='Contact')
    user_id = fields.Many2one('res.users', string='Related User',
                               help='Backend user account this teacher logs in with, used for record-level access.')
    image = fields.Binary()
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
    state = fields.Selection([
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('resigned', 'Resigned'),
    ], default='active', required=True, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _email_uniq = models.Constraint('unique(email)', 'A teacher with this email already exists.')
    _employee_code_uniq = models.Constraint('unique(employee_code)', 'This employee code already exists.')

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

    @api.depends_context('lang')
    def _compute_website_url(self):
        super()._compute_website_url()
        for rec in self:
            rec.website_url = f'/admissions/faculty/{rec.id}'
