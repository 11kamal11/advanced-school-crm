from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EduExam(models.Model):
    _name = 'edu.exam'
    _description = 'Exam'
    _inherit = ['mail.thread']
    _order = 'exam_date desc'

    name = fields.Char(required=True, tracking=True)
    exam_type = fields.Selection([
        ('unit_test', 'Unit Test'),
        ('mid_term', 'Mid Term'),
        ('final', 'Final'),
        ('other', 'Other'),
    ], default='unit_test', required=True)
    class_id = fields.Many2one('edu.class', required=True)
    subject_id = fields.Many2one('edu.subject', required=True)
    academic_year_id = fields.Many2one('edu.academic.year')
    exam_date = fields.Date(required=True)
    max_marks = fields.Float(default=100.0, required=True)
    passing_marks = fields.Float(default=35.0, required=True)
    description = fields.Text()
    result_ids = fields.One2many('edu.exam.result', 'exam_id', string='Results')
    state = fields.Selection([
        ('draft', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True)
    average_marks = fields.Float(compute='_compute_stats', store=True)
    pass_percentage = fields.Float(compute='_compute_stats', store=True)
    highest_marks = fields.Float(compute='_compute_stats', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('passing_marks', 'max_marks')
    def _check_marks(self):
        for rec in self:
            if rec.passing_marks > rec.max_marks:
                raise ValidationError('Passing marks cannot exceed maximum marks.')

    @api.depends('result_ids.marks_obtained', 'result_ids.is_passed')
    def _compute_stats(self):
        for rec in self:
            results = rec.result_ids
            total = len(results)
            rec.average_marks = sum(results.mapped('marks_obtained')) / total if total else 0.0
            rec.highest_marks = max(results.mapped('marks_obtained')) if results else 0.0
            passed = len(results.filtered('is_passed'))
            rec.pass_percentage = (passed / total * 100) if total else 0.0

    def action_start(self):
        self.write({'state': 'ongoing'})

    def action_complete(self):
        self.write({'state': 'completed'})
        template = self.env.ref('edu_crm.mail_template_exam_result', raise_if_not_found=False)
        if template:
            for exam in self:
                for result in exam.result_ids:
                    if result.student_id.guardian_ids.mapped('email'):
                        template.send_mail(result.id, force_send=False)

    def action_cancel(self):
        self.write({'state': 'cancelled'})


class EduExamResult(models.Model):
    _name = 'edu.exam.result'
    _description = 'Exam Result'
    _inherit = ['portal.mixin']
    _order = 'marks_obtained desc'

    exam_id = fields.Many2one('edu.exam', required=True, ondelete='cascade')
    student_id = fields.Many2one('edu.student', required=True)
    marks_obtained = fields.Float(required=True)
    percentage = fields.Float(compute='_compute_grade', store=True)
    grade = fields.Char(compute='_compute_grade', store=True)
    is_passed = fields.Boolean(compute='_compute_grade', store=True)
    remarks = fields.Text()

    _exam_student_uniq = models.Constraint(
        'unique(exam_id, student_id)',
        'This student already has a result recorded for this exam.',
    )

    @api.constrains('marks_obtained', 'exam_id')
    def _check_marks_obtained(self):
        for rec in self:
            if rec.marks_obtained < 0:
                raise ValidationError('Marks obtained cannot be negative.')
            if rec.marks_obtained > rec.exam_id.max_marks:
                raise ValidationError('Marks obtained cannot exceed the exam maximum marks.')

    @api.depends('marks_obtained', 'exam_id.max_marks', 'exam_id.passing_marks')
    def _compute_grade(self):
        for rec in self:
            max_marks = rec.exam_id.max_marks or 1.0
            pct = rec.marks_obtained / max_marks * 100
            rec.percentage = pct
            rec.is_passed = rec.marks_obtained >= rec.exam_id.passing_marks
            if pct >= 90:
                rec.grade = 'A+'
            elif pct >= 80:
                rec.grade = 'A'
            elif pct >= 70:
                rec.grade = 'B+'
            elif pct >= 60:
                rec.grade = 'B'
            elif pct >= 50:
                rec.grade = 'C'
            elif pct >= 35:
                rec.grade = 'D'
            else:
                rec.grade = 'F'

    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = f'/my/children/{rec.student_id.id}/exams'
