from odoo import http
from odoo.http import request


class EduWebsiteLead(http.Controller):
    """Turns the public 'Contact Us' page into a real admissions-lead
    capture form instead of a decorative, non-submitting page."""

    @http.route('/contact-us/submit', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def contact_us_submit(self, **post):
        contact_name = (post.get('contact_name') or '').strip()
        email = (post.get('email') or '').strip()
        phone = (post.get('phone') or '').strip()
        school_name = (post.get('school_name') or '').strip()
        topic = (post.get('topic') or '').strip()
        message = (post.get('message') or '').strip()

        if not contact_name or not email:
            return request.redirect('/contact-us?form_error=1#edu-contact-form-anchor')

        description_parts = []
        if school_name:
            description_parts.append('School / Organization: %s' % school_name)
        if topic:
            description_parts.append('Topic: %s' % topic)
        if message:
            description_parts.append(message)

        vals = {
            'name': 'Website Inquiry - %s' % contact_name,
            'contact_name': contact_name,
            'email': email,
            'phone': phone,
            'description': '\n'.join(description_parts),
            'is_from_website': True,
        }

        source = request.env.ref('edu_crm.utm_source_website', raise_if_not_found=False)
        if source:
            vals['source_id'] = source.id

        # sudo(): the public website visitor has no create rights on edu.lead;
        # only the fields explicitly whitelisted above are ever written.
        request.env['edu.lead'].sudo().create(vals)

        return request.redirect('/contact-us?form_success=1#edu-contact-form-anchor')
