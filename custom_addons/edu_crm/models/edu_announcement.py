from odoo import fields, models


class EduAnnouncement(models.Model):
    _name = 'edu.announcement'
    _description = 'Announcement'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(required=True, tracking=True)
    body = fields.Html()
    audience = fields.Selection([
        ('all', 'Everyone'),
        ('teachers', 'Teachers'),
        ('students', 'Students'),
        ('class', 'Specific Class'),
    ], default='all', required=True)
    class_ids = fields.Many2many('edu.class', string='Classes')
    priority = fields.Selection([
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent'),
    ], default='medium')
    publish_date = fields.Datetime(default=fields.Datetime.now)
    expiry_date = fields.Date()
    is_active = fields.Boolean(default=True)
    is_portal_visible = fields.Boolean(default=True, help='Visible to parents/students on the portal')
    attachment = fields.Binary()
    attachment_name = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def _cron_deactivate_expired(self):
        today = fields.Date.context_today(self)
        self.search([('is_active', '=', True), ('expiry_date', '<', today)]).write({'is_active': False})
