from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EduAnnouncement(models.Model):
    _name = 'edu.announcement'
    _description = 'Announcement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'publish_date desc, create_date desc'

    name = fields.Char(required=True, tracking=True)
    body = fields.Html()
    audience = fields.Selection([
        ('all', 'Everyone'),
        ('teachers', 'Teachers'),
        ('students', 'Students'),
        ('class', 'Specific Class'),
    ], default='all', required=True, tracking=True)
    class_ids = fields.Many2many('edu.class', string='Classes')
    priority = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent'),
    ], default='medium', tracking=True)
    publish_date = fields.Datetime(default=fields.Datetime.now, tracking=True)
    expiry_date = fields.Date(tracking=True)
    # Use the standard Odoo `active` field so archive/unarchive works automatically
    active = fields.Boolean(default=True, tracking=True)
    is_portal_visible = fields.Boolean(
        default=True,
        string='Visible on Portal',
        help='Visible to parents/students on the portal',
        tracking=True,
    )
    attachment = fields.Binary(attachment=True)
    attachment_name = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('audience', 'class_ids')
    def _check_class_audience(self):
        for rec in self:
            if rec.audience == 'class' and not rec.class_ids:
                raise ValidationError(
                    'Please select at least one class when audience is "Specific Class".'
                )

    def _cron_deactivate_expired(self):
        today = fields.Date.context_today(self)
        expired = self.search([('active', '=', True), ('expiry_date', '<', today)])
        expired.write({'active': False})
