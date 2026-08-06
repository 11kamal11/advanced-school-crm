from odoo import fields, models


class EduLeadLostReason(models.Model):
    _name = 'edu.lead.lost.reason'
    _description = 'Admission Lead Lost Reason'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
