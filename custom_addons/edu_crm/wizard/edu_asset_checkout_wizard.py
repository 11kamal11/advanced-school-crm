from odoo import api, fields, models


class EduAssetCheckoutWizard(models.TransientModel):
    _name = 'edu.asset.checkout.wizard'
    _description = 'Check Out Asset'

    asset_id = fields.Many2one('edu.asset', required=True)
    teacher_id = fields.Many2one('edu.teacher', required=True, string='Check Out To')
    expected_return_date = fields.Date()
    condition_on_checkout = fields.Selection([
        ('new', 'New'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('damaged', 'Damaged'),
    ], required=True)
    notes = fields.Char()

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        asset = self.env['edu.asset'].browse(defaults.get('asset_id') or self.env.context.get('default_asset_id'))
        if asset:
            defaults.setdefault('condition_on_checkout', asset.condition)
        return defaults

    def action_confirm_checkout(self):
        self.ensure_one()
        self.env['edu.asset.checkout'].create({
            'asset_id': self.asset_id.id,
            'teacher_id': self.teacher_id.id,
            'expected_return_date': self.expected_return_date,
            'condition_on_checkout': self.condition_on_checkout,
            'notes': self.notes,
        })
        self.asset_id.write({'status': 'assigned', 'assigned_teacher_id': self.teacher_id.id})
        return {'type': 'ir.actions.act_window_close'}
