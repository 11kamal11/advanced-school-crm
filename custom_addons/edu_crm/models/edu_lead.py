from odoo import fields, models, api


class EduLead(models.Model):
    _name = 'edu.lead'
    _description = 'Admission Inquiry (Lead)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(required=True, default='New Inquiry')
    contact_name = fields.Char(required=True, tracking=True)
    email = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    partner_id = fields.Many2one('res.partner')

    student_name = fields.Char(string='Prospective Student')
    student_dob = fields.Date(string='Student Date of Birth')
    class_applying_id = fields.Many2one('edu.class', string='Class Applying For')
    academic_year_id = fields.Many2one('edu.academic.year')

    stage_id = fields.Many2one('edu.crm.stage', tracking=True, group_expand='_read_group_stage_ids',
                                default=lambda self: self.env['edu.crm.stage'].search([], order='sequence', limit=1))
    source_id = fields.Many2one('utm.source')
    medium_id = fields.Many2one('utm.medium')
    campaign_id = fields.Many2one('utm.campaign')
    is_from_website = fields.Boolean(readonly=True)

    priority = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'),
    ], default='medium', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned To', tracking=True,
                               default=lambda self: self.env.user)
    description = fields.Text()
    active = fields.Boolean(default=True)
    lost_reason_id = fields.Many2one('edu.lead.lost.reason')
    state = fields.Selection([
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ], default='new', required=True, tracking=True)
    applicant_id = fields.Many2one('edu.applicant', readonly=True, copy=False)
    kanban_state = fields.Selection([
        ('normal', 'In Progress'), ('done', 'Ready'), ('blocked', 'Blocked'),
    ], default='normal')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return stages.search([], order='sequence')

    def action_mark_contacted(self):
        self.write({'state': 'contacted'})

    def action_mark_qualified(self):
        self.write({'state': 'qualified'})

    def action_convert_to_applicant(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.lead.convert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_lead_id': self.id},
        }

    def action_lost(self):
        self.write({'state': 'lost', 'active': False})

    def action_restore(self):
        self.write({'state': 'new', 'active': True, 'lost_reason_id': False})
