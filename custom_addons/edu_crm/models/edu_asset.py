from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

CONDITIONS = [
    ('new', 'New'),
    ('good', 'Good'),
    ('fair', 'Fair'),
    ('poor', 'Poor'),
    ('damaged', 'Damaged'),
]


class EduAsset(models.Model):
    _name = 'edu.asset'
    _description = 'School Asset'
    _inherit = ['mail.thread']
    _order = 'name'

    name = fields.Char(required=True, tracking=True, help='e.g. Dell Latitude 5420 #12')
    asset_code = fields.Char(readonly=True, copy=False, default='New')
    category_id = fields.Many2one('edu.asset.category', required=True)
    serial_number = fields.Char()
    purchase_date = fields.Date()
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    purchase_cost = fields.Monetary(currency_field='currency_id')
    warranty_expiry = fields.Date()
    condition = fields.Selection(CONDITIONS, default='new', required=True, tracking=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('under_maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('lost', 'Lost'),
    ], default='available', required=True, tracking=True)
    default_location = fields.Char(help='Where this asset normally lives when not checked out, '
                                         'e.g. Computer Lab, Staff Room')
    assigned_teacher_id = fields.Many2one('edu.teacher', string='Currently Assigned To',
                                           readonly=True, copy=False, tracking=True)
    checkout_ids = fields.One2many('edu.asset.checkout', 'asset_id', string='Checkout History')
    checkout_count = fields.Integer(compute='_compute_checkout_count')
    notes = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)

    _asset_code_uniq = models.Constraint('unique(asset_code)', 'This asset code already exists.')

    @api.depends('checkout_ids')
    def _compute_checkout_count(self):
        for rec in self:
            rec.checkout_count = len(rec.checkout_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('asset_code', 'New') == 'New':
                vals['asset_code'] = self.env['ir.sequence'].sudo().next_by_code('edu.asset') or 'New'
        return super().create(vals_list)

    def action_checkout(self):
        self.ensure_one()
        if self.status != 'available':
            raise UserError('Only available assets can be checked out.')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edu.asset.checkout.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_asset_id': self.id},
        }

    def action_set_maintenance(self):
        for rec in self:
            if rec.status == 'assigned':
                raise UserError(f'{rec.name} is currently checked out; return it before sending it for maintenance.')
        self.write({'status': 'under_maintenance'})

    def action_set_available(self):
        self.write({'status': 'available'})

    def action_set_retired(self):
        self.write({'status': 'retired'})

    def action_set_lost(self):
        self.write({'status': 'lost'})


class EduAssetCheckout(models.Model):
    _name = 'edu.asset.checkout'
    _description = 'Asset Checkout / Return Log'
    _order = 'checkout_date desc'

    asset_id = fields.Many2one('edu.asset', required=True, ondelete='cascade')
    teacher_id = fields.Many2one('edu.teacher', required=True, string='Checked Out To')
    checkout_date = fields.Datetime(required=True, default=fields.Datetime.now)
    expected_return_date = fields.Date()
    return_date = fields.Datetime(copy=False)
    condition_on_checkout = fields.Selection(CONDITIONS, required=True)
    condition_on_return = fields.Selection(CONDITIONS, copy=False)
    notes = fields.Char()
    state = fields.Selection([
        ('checked_out', 'Checked Out'),
        ('returned', 'Returned'),
    ], default='checked_out', required=True, copy=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('asset_id', 'state')
    def _check_single_open_checkout(self):
        for rec in self:
            if rec.state != 'checked_out':
                continue
            other_open = self.search_count([
                ('asset_id', '=', rec.asset_id.id),
                ('state', '=', 'checked_out'),
                ('id', '!=', rec.id),
            ])
            if other_open:
                raise ValidationError(f'{rec.asset_id.name} is already checked out to someone else.')

    def action_return(self):
        self.ensure_one()
        if self.state != 'checked_out':
            raise UserError('This checkout has already been returned.')
        if not self.condition_on_return:
            raise UserError('Please record the condition of the asset on return before confirming.')
        self.write({
            'state': 'returned',
            'return_date': fields.Datetime.now(),
        })
        self.asset_id.write({'status': 'available', 'assigned_teacher_id': False})
