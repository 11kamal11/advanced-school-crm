from odoo import fields, models, api
from odoo.exceptions import AccessError


class EduDashboard(models.TransientModel):
    _name = 'edu.dashboard'
    _description = 'School CRM Dashboard'

    student_count = fields.Integer(readonly=True)
    teacher_count = fields.Integer(readonly=True)
    class_count = fields.Integer(readonly=True)
    lead_count = fields.Integer(readonly=True)
    applicant_count = fields.Integer(readonly=True)
    fee_due_count = fields.Integer(readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)
    fee_due_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    leave_pending_count = fields.Integer(readonly=True)
    asset_count = fields.Integer(readonly=True)
    asset_checked_out_count = fields.Integer(readonly=True)
    announcement_count = fields.Integer(readonly=True)

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = 'Dashboard'

    def _safe_count(self, model, domain=None):
        try:
            return self.env[model].search_count(domain or [])
        except AccessError:
            return 0

    def _safe_sum(self, model, domain, field):
        """Aggregate via read_group (single SQL SUM) instead of fetching all records."""
        try:
            groups = self.env[model].read_group(domain, [field], [])
            return groups[0][field] if groups else 0.0
        except AccessError:
            return 0.0

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        company_id = self.env.company.id
        cid = ('company_id', '=', company_id)
        defaults.update({
            'currency_id': self.env.company.currency_id.id,
            'student_count': self._safe_count('edu.student', [cid, ('state', '=', 'active')]),
            'teacher_count': self._safe_count('edu.teacher', [cid, ('state', '=', 'active')]),
            'class_count': self._safe_count('edu.class', [cid]),
            'lead_count': self._safe_count('edu.lead', [cid, ('state', 'not in', ('converted', 'lost'))]),
            'applicant_count': self._safe_count('edu.applicant', [cid, ('state', 'not in', ('approved', 'rejected'))]),
            'fee_due_count': self._safe_count('edu.fee', [cid, ('state', 'in', ('pending', 'partial', 'overdue'))]),
            'fee_due_amount': self._safe_sum(
                'edu.fee', [cid, ('state', 'in', ('pending', 'partial', 'overdue'))], 'balance'),
            'leave_pending_count': self._safe_count('edu.leave.request', [cid, ('state', '=', 'submitted')]),
            'asset_count': self._safe_count('edu.asset', [cid]),
            'asset_checked_out_count': self._safe_count('edu.asset', [cid, ('status', '=', 'assigned')]),
            'announcement_count': self._safe_count('edu.announcement', [cid, ('active', '=', True)]),
        })
        return defaults
