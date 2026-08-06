from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EduFeePaymentWizard(models.TransientModel):
    _name = 'edu.fee.payment.wizard'
    _description = 'Record Fee Payment'

    fee_id = fields.Many2one('edu.fee', required=True)
    student_id = fields.Many2one(related='fee_id.student_id', readonly=True)
    balance = fields.Float(related='fee_id.balance', readonly=True)
    amount = fields.Float(required=True)
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    payment_method = fields.Selection([
        ('cash', 'Cash'), ('bank', 'Bank Transfer'), ('online', 'Online'),
        ('cheque', 'Cheque'), ('upi', 'UPI'),
    ], default='cash', required=True)
    reference = fields.Char(string='Receipt Number')
    notes = fields.Char()

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Payment amount must be positive.')
            if rec.amount > rec.balance:
                raise ValidationError('Payment amount cannot exceed the outstanding balance.')

    def action_confirm_payment(self):
        self.ensure_one()
        self.env['edu.fee.payment'].create({
            'fee_id': self.fee_id.id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_method': self.payment_method,
            'reference': self.reference,
            'notes': self.notes,
        })
        return {'type': 'ir.actions.act_window_close'}
