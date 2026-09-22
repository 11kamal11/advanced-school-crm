from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal


class EduPortal(CustomerPortal):

    def _get_guardian_students(self):
        guardians = request.env['edu.guardian'].sudo().search(
            [('partner_id', '=', request.env.user.partner_id.id)])
        return guardians.student_ids

    def _get_student_or_404(self, student_id):
        student = self._get_guardian_students().filtered(lambda s: s.id == student_id)
        if not student:
            raise request.not_found()
        return student

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'children_count' in counters:
            values['children_count'] = len(self._get_guardian_students())
        return values

    @http.route('/my/children', type='http', auth='user', website=True)
    def portal_children(self, **kwargs):
        values = self._prepare_portal_layout_values()
        values.update({
            'students': self._get_guardian_students(),
            'page_name': 'children',
        })
        return request.render('edu_crm.portal_my_children', values)

    @http.route('/my/children/<int:student_id>', type='http', auth='user', website=True)
    def portal_child_dashboard(self, student_id, **kwargs):
        student = self._get_student_or_404(student_id)
        announcements = request.env['edu.announcement'].sudo().search([
            ('is_portal_visible', '=', True),
            '|', ('audience', 'in', ['all', 'students']),
                 ('class_ids', 'in', student.class_id.ids),
        ], order='publish_date desc', limit=5)
        upcoming_exams = request.env['edu.exam'].sudo().search([
            ('class_id', '=', student.class_id.id),
            ('state', 'in', ['draft', 'ongoing']),
        ], order='exam_date', limit=5)
        values = self._prepare_portal_layout_values()
        values.update({
            'student': student,
            'announcements': announcements,
            'upcoming_exams': upcoming_exams,
            'page_name': 'child_dashboard',
        })
        return request.render('edu_crm.portal_child_dashboard', values)

    @http.route('/my/children/<int:student_id>/attendance', type='http', auth='user', website=True)
    def portal_child_attendance(self, student_id, **kwargs):
        student = self._get_student_or_404(student_id)
        lines = request.env['edu.attendance.line'].sudo().search(
            [('student_id', '=', student.id)], order='date desc')
        values = self._prepare_portal_layout_values()
        values.update({'student': student, 'lines': lines, 'page_name': 'child_attendance'})
        return request.render('edu_crm.portal_child_attendance', values)

    @http.route('/my/children/<int:student_id>/exams', type='http', auth='user', website=True)
    def portal_child_exams(self, student_id, **kwargs):
        student = self._get_student_or_404(student_id)
        results = request.env['edu.exam.result'].sudo().search(
            [('student_id', '=', student.id)], order='create_date desc')
        values = self._prepare_portal_layout_values()
        values.update({'student': student, 'results': results, 'page_name': 'child_exams'})
        return request.render('edu_crm.portal_child_exams', values)

    @http.route('/my/children/<int:student_id>/fees', type='http', auth='user', website=True)
    def portal_child_fees(self, student_id, **kwargs):
        student = self._get_student_or_404(student_id)
        fees = request.env['edu.fee'].sudo().search(
            [('student_id', '=', student.id)], order='due_date desc')
        values = self._prepare_portal_layout_values()
        values.update({'student': student, 'fees': fees, 'page_name': 'child_fees'})
        return request.render('edu_crm.portal_child_fees', values)

    @http.route('/my/children/<int:student_id>/fees/<int:fee_id>/pay', type='http', auth='user', website=True)
    def portal_pay_fee(self, student_id, fee_id, **kwargs):
        student = self._get_student_or_404(student_id)
        fee = request.env['edu.fee'].sudo().browse(fee_id)
        if not fee.exists() or fee.student_id.id != student.id:
            raise request.not_found()
        if fee.balance <= 0 or fee.state in ('paid', 'waived'):
            return request.redirect(f'/my/children/{student.id}/fees')

        currency_id = fee.currency_id.id or request.env.company.currency_id.id
        return request.redirect(
            f'/payment/pay?reference=EDUFEE-{fee.id}&amount={fee.balance}&currency_id={currency_id}'
        )

    @http.route('/my/leave-requests', type='http', auth='user', website=True)
    def portal_leave_requests(self, **kwargs):
        students = self._get_guardian_students()
        leaves = request.env['edu.leave.request'].sudo().search(
            [('student_id', 'in', students.ids)], order='create_date desc')
        values = self._prepare_portal_layout_values()
        values.update({'leaves': leaves, 'page_name': 'leave_requests'})
        return request.render('edu_crm.portal_leave_requests', values)

    @http.route('/my/leave-requests/new', type='http', auth='user', website=True, methods=['GET'])
    def portal_leave_request_new_form(self, **kwargs):
        values = self._prepare_portal_layout_values()
        values.update({
            'students': self._get_guardian_students(),
            'page_name': 'leave_request_new',
            'error': kwargs.get('error'),
        })
        return request.render('edu_crm.portal_leave_request_form', values)

    @http.route('/my/leave-requests/new/submit', type='http', auth='user', website=True,
                methods=['POST'], csrf=True)
    def portal_leave_request_submit(self, **post):
        try:
            student_id = int(post.get('student_id', 0))
        except (TypeError, ValueError):
            return request.redirect('/my/leave-requests/new?error=1')
        student = self._get_student_or_404(student_id)

        if not (post.get('date_from') and post.get('date_to') and (post.get('reason') or '').strip()):
            return request.redirect('/my/leave-requests/new?error=1')

        try:
            leave = request.env['edu.leave.request'].sudo().create({
                'applicant_type': 'student',
                'student_id': student.id,
                'leave_type': post.get('leave_type', 'other'),
                'date_from': post.get('date_from'),
                'date_to': post.get('date_to'),
                'reason': post.get('reason', '').strip(),
            })
            leave.action_submit()
        except (ValueError, TypeError, ValidationError):
            return request.redirect('/my/leave-requests/new?error=1')
        return request.redirect('/my/leave-requests')

    @http.route('/my/announcements', type='http', auth='user', website=True)
    def portal_announcements(self, **kwargs):
        students = self._get_guardian_students()
        class_ids = students.mapped('class_id').ids
        announcements = request.env['edu.announcement'].sudo().search([
            ('is_portal_visible', '=', True),
            '|', ('audience', 'in', ['all', 'students']),
                 ('class_ids', 'in', class_ids),
        ], order='publish_date desc')
        values = self._prepare_portal_layout_values()
        values.update({'announcements': announcements, 'page_name': 'announcements'})
        return request.render('edu_crm.portal_announcements', values)
