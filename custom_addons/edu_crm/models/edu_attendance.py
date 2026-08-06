from odoo import fields, models, api


class EduAttendance(models.Model):
    _name = 'edu.attendance'
    _description = 'Attendance Session'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    class_id = fields.Many2one('edu.class', required=True, tracking=True)
    subject_id = fields.Many2one('edu.subject')
    date = fields.Date(required=True, default=fields.Date.context_today)
    teacher_id = fields.Many2one('edu.teacher')
    line_ids = fields.One2many('edu.attendance.line', 'attendance_id', string='Students')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], default='draft', required=True, tracking=True)
    total_present = fields.Integer(compute='_compute_stats', store=True)
    total_absent = fields.Integer(compute='_compute_stats', store=True)
    total_late = fields.Integer(compute='_compute_stats', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    _class_date_uniq = models.Constraint(
        'unique(class_id, date)',
        'An attendance session for this class and date already exists.',
    )

    @api.depends('line_ids.status')
    def _compute_stats(self):
        for rec in self:
            rec.total_present = len(rec.line_ids.filtered(lambda l: l.status == 'present'))
            rec.total_absent = len(rec.line_ids.filtered(lambda l: l.status == 'absent'))
            rec.total_late = len(rec.line_ids.filtered(lambda l: l.status == 'late'))

    @api.onchange('class_id')
    def _onchange_class_id(self):
        if self.class_id:
            self.line_ids = [(5, 0, 0)] + [
                (0, 0, {'student_id': student.id, 'status': 'present'})
                for student in self.class_id.student_ids
            ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].sudo().next_by_code('edu.attendance') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_draft(self):
        self.write({'state': 'draft'})


class EduAttendanceLine(models.Model):
    _name = 'edu.attendance.line'
    _description = 'Attendance Line'

    attendance_id = fields.Many2one('edu.attendance', required=True, ondelete='cascade')
    student_id = fields.Many2one('edu.student', required=True)
    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ], required=True, default='present')
    remarks = fields.Char()
    date = fields.Date(related='attendance_id.date', store=True)
    class_id = fields.Many2one(related='attendance_id.class_id', store=True)

    _attendance_student_uniq = models.Constraint(
        'unique(attendance_id, student_id)',
        'This student already has an attendance entry for this session.',
    )
