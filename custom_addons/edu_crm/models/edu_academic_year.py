from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EduAcademicYear(models.Model):
    _name = 'edu.academic.year'
    _description = 'Academic Year'
    _order = 'date_start desc'

    name = fields.Char(required=True, help='e.g. 2026-2027')
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)

    _name_uniq = models.Constraint('unique(name)', 'This academic year already exists.')

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for year in self:
            if year.date_end <= year.date_start:
                raise ValidationError('The end date must be after the start date.')
