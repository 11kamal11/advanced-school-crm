from odoo import api, fields, models


class EduLeadConvertWizard(models.TransientModel):
    _name = 'edu.lead.convert.wizard'
    _description = 'Convert Lead to Applicant'

    lead_id = fields.Many2one('edu.lead', required=True)
    student_name = fields.Char(required=True)
    student_dob = fields.Date()
    gender = fields.Selection([
        ('male', 'Male'), ('female', 'Female'), ('other', 'Other'),
    ])
    address = fields.Text()
    previous_school = fields.Char()
    class_applying_id = fields.Many2one('edu.class', string='Class Applying For', required=True)
    guardian_name = fields.Char(required=True)
    guardian_phone = fields.Char()
    guardian_email = fields.Char()
    relationship = fields.Selection([
        ('father', 'Father'), ('mother', 'Mother'), ('guardian', 'Guardian'),
    ], default='guardian')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        lead = self.env['edu.lead'].browse(defaults.get('lead_id') or self.env.context.get('default_lead_id'))
        if lead:
            defaults.setdefault('student_name', lead.student_name or lead.contact_name)
            defaults.setdefault('student_dob', lead.student_dob)
            defaults.setdefault('class_applying_id', lead.class_applying_id.id)
            defaults.setdefault('guardian_name', lead.contact_name)
            defaults.setdefault('guardian_phone', lead.phone or lead.mobile)
            defaults.setdefault('guardian_email', lead.email)
        return defaults

    def action_convert(self):
        self.ensure_one()
        applicant = self.env['edu.applicant'].create({
            'lead_id': self.lead_id.id,
            'student_name': self.student_name,
            'student_dob': self.student_dob,
            'gender': self.gender,
            'address': self.address,
            'previous_school': self.previous_school,
            'class_applying_id': self.class_applying_id.id,
            'guardian_name': self.guardian_name,
            'guardian_phone': self.guardian_phone,
            'guardian_email': self.guardian_email,
            'relationship': self.relationship,
        })
        self.lead_id.write({'state': 'converted', 'applicant_id': applicant.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.applicant',
            'view_mode': 'form',
            'res_id': applicant.id,
        }
