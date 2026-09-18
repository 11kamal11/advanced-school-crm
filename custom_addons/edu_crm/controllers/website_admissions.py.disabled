from werkzeug.exceptions import BadRequest

from odoo import http
from odoo.http import request


class WebsiteAdmissions(http.Controller):

    @http.route('/admissions', type='http', auth='public', website=True, sitemap=True)
    def admissions_home(self, **kwargs):
        Student = request.env['edu.student'].sudo()
        Teacher = request.env['edu.teacher'].sudo()
        programs = request.env['edu.program'].sudo().search(
            [('is_published', '=', True)], order='sequence, name', limit=3)
        faculty = Teacher.search([('is_published', '=', True)], order='name', limit=3)
        stats = {
            'students': Student.search_count([('state', '=', 'active')]),
            'teachers': Teacher.search_count([('state', '=', 'active')]),
            'programs': request.env['edu.program'].sudo().search_count([('is_published', '=', True)]),
        }
        return request.render('edu_crm.admissions_home', {
            'programs': programs,
            'faculty': faculty,
            'stats': stats,
        })

    @http.route('/admissions/programs', type='http', auth='public', website=True, sitemap=True)
    def admissions_programs(self, **kwargs):
        programs = request.env['edu.program'].sudo().search(
            [('is_published', '=', True)], order='sequence, name')
        return request.render('edu_crm.admissions_programs', {'programs': programs})

    @http.route('/admissions/programs/<int:program_id>', type='http',
                auth='public', website=True, sitemap=True)
    def admissions_program_detail(self, program_id, **kwargs):
        program = request.env['edu.program'].sudo().browse(program_id)
        is_admin = request.env.user.has_group('edu_crm.group_edu_admin')
        if not program.exists() or (not program.is_published and not is_admin):
            raise request.not_found()
        return request.render('edu_crm.admissions_program_detail', {'program': program})

    @http.route('/admissions/faculty', type='http', auth='public', website=True, sitemap=True)
    def admissions_faculty(self, **kwargs):
        faculty = request.env['edu.teacher'].sudo().search(
            [('is_published', '=', True)], order='name')
        return request.render('edu_crm.admissions_faculty', {'faculty': faculty})

    @http.route('/admissions/faculty/<int:teacher_id>', type='http',
                auth='public', website=True, sitemap=True)
    def admissions_faculty_detail(self, teacher_id, **kwargs):
        teacher = request.env['edu.teacher'].sudo().browse(teacher_id)
        is_admin = request.env.user.has_group('edu_crm.group_edu_admin')
        if not teacher.exists() or (not teacher.is_published and not is_admin):
            raise request.not_found()
        return request.render('edu_crm.admissions_faculty_detail', {'teacher': teacher})

    @http.route('/admissions/inquiry', type='http', auth='public', website=True, sitemap=True)
    def admissions_inquiry_form(self, **kwargs):
        classes = request.env['edu.class'].sudo().search([], order='name')
        return request.render('edu_crm.admissions_inquiry_form', {
            'classes': classes,
            'error': kwargs.get('error'),
            'form_data': kwargs,
        })

    @http.route('/admissions/inquiry/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def admissions_inquiry_submit(self, **post):
        required = ['contact_name', 'phone', 'student_name']
        missing = [f for f in required if not (post.get(f) or '').strip()]
        if missing:
            return request.redirect('/admissions/inquiry?error=missing_fields')

        website_source = request.env.ref('edu_crm.utm_source_website', raise_if_not_found=False)
        class_applying_id = int(post['class_applying_id']) if post.get('class_applying_id') else False

        try:
            lead = request.env['edu.lead'].sudo().create({
                'contact_name': post.get('contact_name', '').strip(),
                'email': post.get('email', '').strip(),
                'phone': post.get('phone', '').strip(),
                'student_name': post.get('student_name', '').strip(),
                'class_applying_id': class_applying_id,
                'description': post.get('message', '').strip(),
                'is_from_website': True,
                'source_id': website_source.id if website_source else False,
            })
        except (ValueError, TypeError):
            raise BadRequest('Invalid form data')

        template = request.env.ref('edu_crm.mail_template_new_lead_frontdesk', raise_if_not_found=False)
        frontdesk_emails = list(filter(None, request.env['res.users'].sudo().search(
            [('all_group_ids', 'in', request.env.ref('edu_crm.group_edu_frontdesk').id)]
        ).mapped('email')))
        if template and frontdesk_emails:
            template.sudo().send_mail(lead.id, force_send=False, email_values={
                'email_to': ','.join(frontdesk_emails),
            })

        return request.render('edu_crm.admissions_inquiry_thank_you', {'lead': lead})
