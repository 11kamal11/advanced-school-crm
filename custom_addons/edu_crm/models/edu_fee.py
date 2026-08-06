from odoo import fields, models, api
from odoo.exceptions import ValidationError

FEE_TYPES = [
    ('tuition', 'Tuition'),
    ('admission', 'Admission'),
    ('exam', 'Exam'),
    ('transport', 'Transport'),
    ('library', 'Library'),
    ('lab', 'Lab'),
    ('sports', 'Sports'),
    ('other', 'Other'),
]

PAYMENT_METHODS = [
    ('cash', 'Cash'),
    ('bank', 'Bank Transfer'),
    ('online', 'Online'),
    ('cheque', 'Cheque'),
    ('upi', 'UPI'),
]


class EduFeeStructure(models.Model):
    _name = 'edu.fee.structure'
    _description = 'Fee Structure'
    _order = 'due_date'

    name = fields.Char(required=True)
    class_id = fields.Many2one('edu.class')
    academic_year_id = fields.Many2one('edu.academic.year')
    fee_type = fields.Selection(FEE_TYPES, default='tuition', required=True)
    amount = fields.Float(required=True)
    due_date = fields.Date()


class EduFee(models.Model):
    _name = 'edu.fee'
    _description = 'Student Fee'
    _inherit = ['mail.thread', 'portal.mixin']
    _order = 'due_date desc'

    name = fields.Char(readonly=True, copy=False, default='New')
    student_id = fields.Many2one('edu.student', required=True, tracking=True)
    class_id = fields.Many2one(related='student_id.class_id', store=True)
    fee_structure_id = fields.Many2one('edu.fee.structure')
    fee_type = fields.Selection(FEE_TYPES, default='tuition', required=True, tracking=True)
    description = fields.Char()
    amount = fields.Float(required=True)
    discount = fields.Float(help='Discount percentage')
    net_amount = fields.Float(compute='_compute_amounts', store=True)
    paid_amount = fields.Float(compute='_compute_amounts', store=True, tracking=True)
    balance = fields.Float(compute='_compute_amounts', store=True)
    due_date = fields.Date(required=True)
    paid_date = fields.Date()
    payment_ids = fields.One2many('edu.fee.payment', 'fee_id')
    academic_year_id = fields.Many2one('edu.academic.year')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('waived', 'Waived'),
    ], default='pending', required=True, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('amount', 'discount', 'payment_ids.amount')
    def _compute_amounts(self):
        for rec in self:
            net = rec.amount * (1 - (rec.discount or 0.0) / 100)
            paid = sum(rec.payment_ids.mapped('amount'))
            rec.net_amount = net
            rec.paid_amount = paid
            rec.balance = net - paid

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].sudo().next_by_code('edu.fee') or 'New'
        return super().create(vals_list)

    def action_waive(self):
        self.write({'state': 'waived'})

    def action_pay(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.fee.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_fee_id': self.id},
        }

    def _cron_check_overdue(self):
        today = fields.Date.context_today(self)
        overdue = self.search([
            ('state', 'in', ('pending', 'partial')),
            ('due_date', '<', today),
        ])
        overdue.write({'state': 'overdue'})
        template = self.env.ref('edu_crm.mail_template_fee_reminder', raise_if_not_found=False)
        if template:
            for fee in overdue:
                if fee.student_id.guardian_ids.mapped('email'):
                    template.send_mail(fee.id, force_send=False)

    def _compute_access_url(self):
        super()._compute_access_url()
        for rec in self:
            rec.access_url = f'/my/children/{rec.student_id.id}/fees'


class EduFeePayment(models.Model):
    _name = 'edu.fee.payment'
    _description = 'Fee Payment'
    _order = 'payment_date desc'

    fee_id = fields.Many2one('edu.fee', required=True, ondelete='cascade')
    student_id = fields.Many2one(related='fee_id.student_id', store=True)
    amount = fields.Float(required=True)
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    payment_method = fields.Selection(PAYMENT_METHODS, default='cash', required=True)
    reference = fields.Char(string='Receipt Number')
    notes = fields.Char()
    transaction_id = fields.Many2one('payment.transaction', readonly=True, copy=False,
                                      help='Set when this payment was made online through the portal.')

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError('Payment amount must be positive.')
            if rec.fee_id.balance < 0:
                raise ValidationError('This payment would exceed the outstanding balance on the fee.')

    @api.model_create_multi
    def create(self, vals_list):
        payments = super().create(vals_list)
        for payment in payments:
            fee = payment.fee_id
            if fee.balance <= 0:
                fee.state = 'paid'
            else:
                fee.state = 'partial'
            fee.paid_date = payment.payment_date
            fee.message_post(body=f'Payment of {payment.amount} recorded ({payment.payment_method}).')
        return payments
