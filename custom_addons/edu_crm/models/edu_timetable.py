from odoo import fields, models, api
from odoo.exceptions import ValidationError

DAYS = [
    ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
    ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'),
]


class EduTimetable(models.Model):
    _name = 'edu.timetable'
    _description = 'Timetable Slot'
    _order = 'day_of_week, start_time'

    class_id = fields.Many2one('edu.class', required=True, ondelete='cascade')
    subject_id = fields.Many2one('edu.subject', required=True)
    teacher_id = fields.Many2one('edu.teacher')
    day_of_week = fields.Selection(DAYS, required=True)
    start_time = fields.Float(required=True)
    end_time = fields.Float(required=True)
    room = fields.Char()
    academic_year_id = fields.Many2one('edu.academic.year')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('start_time', 'end_time')
    def _check_times(self):
        for rec in self:
            if not (0 <= rec.start_time < rec.end_time <= 24):
                raise ValidationError('Start time must be before end time, both within a single day.')

    @api.constrains('class_id', 'teacher_id', 'room', 'day_of_week', 'start_time', 'end_time')
    def _check_overlap(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('day_of_week', '=', rec.day_of_week),
                ('start_time', '<', rec.end_time),
                ('end_time', '>', rec.start_time),
            ]
            if self.search_count(domain + [('class_id', '=', rec.class_id.id)]):
                raise ValidationError('This class already has another slot overlapping this time.')
            if rec.teacher_id and self.search_count(domain + [('teacher_id', '=', rec.teacher_id.id)]):
                raise ValidationError('This teacher is already booked for an overlapping slot.')
            if rec.room and self.search_count(domain + [('room', '=', rec.room)]):
                raise ValidationError('This room is already booked for an overlapping slot.')
