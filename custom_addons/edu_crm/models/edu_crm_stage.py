from odoo import fields, models


class EduCrmStage(models.Model):
    _name = 'edu.crm.stage'
    _description = 'Admission Pipeline Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(help='Folded in the kanban view when there are no records to show.')
    is_won = fields.Boolean(help='This stage represents a converted/won lead.')
