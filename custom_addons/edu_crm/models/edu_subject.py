from odoo import fields, models


class EduSubject(models.Model):
    _name = 'edu.subject'
    _description = 'Subject'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    class_ids = fields.Many2many('edu.class', string='Classes')
    teacher_ids = fields.Many2many('edu.teacher', string='Teachers')
    credit_hours = fields.Integer(default=3)
    subject_type = fields.Selection([
        ('theory', 'Theory'),
        ('practical', 'Practical'),
        ('both', 'Theory & Practical'),
    ], default='theory', required=True)
    is_elective = fields.Boolean()
    description = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _code_uniq = models.Constraint('unique(code)', 'This subject code already exists.')
