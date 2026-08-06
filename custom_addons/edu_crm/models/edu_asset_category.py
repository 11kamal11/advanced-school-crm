from odoo import fields, models


class EduAssetCategory(models.Model):
    _name = 'edu.asset.category'
    _description = 'Asset Category'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    _name_uniq = models.Constraint('unique(name)', 'This asset category already exists.')
