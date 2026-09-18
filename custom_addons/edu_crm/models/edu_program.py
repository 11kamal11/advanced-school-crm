from odoo import fields, models


class EduProgram(models.Model):
    _name = 'edu.program'
    _description = 'Academic Program'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char()
    tagline = fields.Char(help='Short one-line summary shown on program cards.')
    description = fields.Html()
    image = fields.Binary()
    sequence = fields.Integer(default=10)
    class_ids = fields.One2many('edu.class', 'program_id', string='Classes')
    active = fields.Boolean(default=True)

