from odoo import fields, models, api


class EduClass(models.Model):
    _name = 'edu.class'
    _description = 'Class / Section'
    _inherit = ['mail.thread']
    _order = 'name, section'

    name = fields.Char(required=True, tracking=True, help='e.g. Grade 5')
    code = fields.Char(required=True)
    section = fields.Char(default='A')
    academic_year_id = fields.Many2one('edu.academic.year', required=True, tracking=True)
    class_teacher_id = fields.Many2one('edu.teacher', string='Class Teacher', tracking=True)
    program_id = fields.Many2one('edu.program', string='Program')
    subject_ids = fields.Many2many('edu.subject', string='Subjects')
    student_ids = fields.One2many('edu.student', 'class_id', string='Students')
    capacity = fields.Integer(default=40)
    student_count = fields.Integer(compute='_compute_student_count', store=True)
    is_full = fields.Boolean(compute='_compute_is_full', store=True)
    attendance_count = fields.Integer(compute='_compute_attendance_count')
    exam_count = fields.Integer(compute='_compute_exam_count')
    description = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _name_section_year_uniq = models.Constraint(
        'unique(name, section, academic_year_id)',
        'A class with this name, section and academic year already exists.',
    )

    @api.depends('student_ids', 'student_ids.active')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

    @api.depends('student_count', 'capacity')
    def _compute_is_full(self):
        for rec in self:
            rec.is_full = rec.capacity > 0 and rec.student_count >= rec.capacity

    def _compute_attendance_count(self):
        for rec in self:
            rec.attendance_count = self.env['edu.attendance'].search_count(
                [('class_id', '=', rec.id)]
            )

    def _compute_exam_count(self):
        for rec in self:
            rec.exam_count = self.env['edu.exam'].search_count(
                [('class_id', '=', rec.id)]
            )

    def action_view_class_attendance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Attendance',
            'res_model': 'edu.attendance',
            'view_mode': 'list,form',
            'domain': [('class_id', '=', self.id)],
            'context': {'default_class_id': self.id},
        }

    def action_view_class_exams(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Exams',
            'res_model': 'edu.exam',
            'view_mode': 'list,form',
            'domain': [('class_id', '=', self.id)],
            'context': {'default_class_id': self.id},
        }

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.name} - {rec.section}'
