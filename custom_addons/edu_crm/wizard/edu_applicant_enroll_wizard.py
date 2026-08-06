from odoo import api, fields, models


class EduApplicantEnrollWizard(models.TransientModel):
    _name = 'edu.applicant.enroll.wizard'
    _description = 'Enroll Applicant as Student'

    applicant_id = fields.Many2one('edu.applicant', required=True)
    class_id = fields.Many2one('edu.class', required=True)
    academic_year_id = fields.Many2one('edu.academic.year')
    roll_number = fields.Integer()
    admission_date = fields.Date(required=True, default=fields.Date.context_today)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        applicant = self.env['edu.applicant'].browse(
            defaults.get('applicant_id') or self.env.context.get('default_applicant_id'))
        if applicant:
            defaults.setdefault('class_id', applicant.class_applying_id.id)
        return defaults

    def _find_or_create_guardian(self, applicant):
        partner = False
        if applicant.guardian_email:
            partner = self.env['res.partner'].search([('email', '=', applicant.guardian_email)], limit=1)
        if not partner:
            partner = self.env['res.partner'].create({
                'name': applicant.guardian_name,
                'email': applicant.guardian_email,
                'phone': applicant.guardian_phone,
            })
        guardian = self.env['edu.guardian'].search([('partner_id', '=', partner.id)], limit=1)
        if not guardian:
            guardian = self.env['edu.guardian'].create({
                'partner_id': partner.id,
                'relationship': applicant.relationship or 'guardian',
            })
        return guardian

    def action_enroll(self):
        self.ensure_one()
        applicant = self.applicant_id
        guardian = self._find_or_create_guardian(applicant)
        student = self.env['edu.student'].create({
            'name': applicant.student_name,
            'date_of_birth': applicant.student_dob,
            'gender': applicant.gender,
            'address': applicant.address,
            'class_id': self.class_id.id,
            'roll_number': self.roll_number,
            'academic_year_id': self.academic_year_id.id,
            'admission_date': self.admission_date,
            'guardian_ids': [(4, guardian.id)],
            'applicant_id': applicant.id,
            'state': 'active',
        })
        applicant.write({'student_id': student.id})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.student',
            'view_mode': 'form',
            'res_id': student.id,
        }
