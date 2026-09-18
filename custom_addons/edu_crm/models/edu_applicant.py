from odoo import fields, models, api


class EduApplicant(models.Model):
    _name = 'edu.applicant'
    _description = 'Admission Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    lead_id = fields.Many2one('edu.lead', readonly=True)

    student_name = fields.Char(required=True, tracking=True)
    student_dob = fields.Date(string='Date of Birth')
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

    birth_certificate = fields.Binary()
    birth_certificate_filename = fields.Char()
    previous_marksheet = fields.Binary()
    previous_marksheet_filename = fields.Char()
    photo = fields.Binary()

    state = fields.Selection([
        ('submitted', 'Submitted'),
        ('document_verification', 'Document Verification'),
        ('interview', 'Interview'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='submitted', required=True, tracking=True)
    rejection_reason = fields.Text()
    student_id = fields.Many2one('edu.student', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].sudo().next_by_code('edu.applicant') or 'New'
        applicants = super().create(vals_list)
        template = self.env.ref('edu_crm.mail_template_application_received', raise_if_not_found=False)
        if template:
            for applicant in applicants:
                if applicant.guardian_email:
                    template.send_mail(applicant.id, force_send=False)
        return applicants

    def action_start_verification(self):
        self.write({'state': 'document_verification'})

    def action_schedule_interview(self):
        self.write({'state': 'interview'})

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_enroll(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.applicant.enroll.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_applicant_id': self.id},
        }
