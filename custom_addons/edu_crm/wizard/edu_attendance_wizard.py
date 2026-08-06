from odoo import fields, models


class EduAttendanceWizard(models.TransientModel):
    _name = 'edu.attendance.wizard'
    _description = 'Quick Attendance Wizard'

    class_id = fields.Many2one('edu.class', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)

    def action_create_attendance(self):
        self.ensure_one()
        attendance = self.env['edu.attendance'].create({
            'class_id': self.class_id.id,
            'date': self.date,
            'line_ids': [
                (0, 0, {'student_id': student.id, 'status': 'present'})
                for student in self.class_id.student_ids
            ],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.attendance',
            'view_mode': 'form',
            'res_id': attendance.id,
        }
