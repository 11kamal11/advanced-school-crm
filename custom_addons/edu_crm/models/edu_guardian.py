from odoo import fields, models, api


class EduGuardian(models.Model):
    _name = 'edu.guardian'
    _description = 'Guardian / Parent'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(related='partner_id.name', store=True, readonly=True)
    partner_id = fields.Many2one('res.partner', required=True, tracking=True)
    student_ids = fields.Many2many('edu.student', string='Children')
    relationship = fields.Selection([
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    ], default='guardian', required=True)
    phone = fields.Char(related='partner_id.phone', readonly=False)
    email = fields.Char(related='partner_id.email', readonly=False)
    occupation = fields.Char()
    has_portal_access = fields.Boolean(compute='_compute_has_portal_access')
    active = fields.Boolean(default=True)

    _partner_uniq = models.Constraint('unique(partner_id)', 'This contact is already registered as a guardian.')

    @api.depends('partner_id.user_ids', 'partner_id.user_ids.active')
    def _compute_has_portal_access(self):
        for rec in self:
            rec.has_portal_access = bool(rec.partner_id.user_ids)

    def action_grant_portal_access(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'portal.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_ids': [self.partner_id.id]},
        }
