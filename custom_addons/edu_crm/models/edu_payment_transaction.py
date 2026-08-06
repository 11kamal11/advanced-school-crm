import re

from odoo import fields, models

FEE_REFERENCE_RE = re.compile(r'^EDUFEE-(\d+)')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _post_process(self):
        super()._post_process()
        for tx in self:
            tx._edu_reconcile_fee_payment()

    def _edu_reconcile_fee_payment(self):
        self.ensure_one()
        if self.state != 'done':
            return
        match = FEE_REFERENCE_RE.match(self.reference or '')
        if not match:
            return  # Not one of ours -- leave other transactions untouched.

        fee = self.env['edu.fee'].sudo().browse(int(match.group(1)))
        if not fee.exists() or fee.state in ('paid', 'waived'):
            return
        already_reconciled = self.env['edu.fee.payment'].sudo().search_count(
            [('transaction_id', '=', self.id)])
        if already_reconciled:
            return  # Already processed; avoid double-crediting on a re-run.

        amount = min(self.amount, fee.balance)
        if amount <= 0:
            return

        self.env['edu.fee.payment'].sudo().create({
            'fee_id': fee.id,
            'amount': amount,
            'payment_date': fields.Date.context_today(self),
            'payment_method': 'online',
            'reference': self.reference,
            'notes': f'Paid online via {self.provider_id.name}.',
            'transaction_id': self.id,
        })
