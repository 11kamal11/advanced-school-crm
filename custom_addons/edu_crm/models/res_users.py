from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        dashboard_action = self.env.ref('edu_crm.action_edu_dashboard', raise_if_not_found=False)
        if dashboard_action:
            for vals in vals_list:
                # Only set the dashboard home action for internal (non-portal, non-public) users.
                # share=True means portal or public user — they must not get a backend action.
                if not vals.get('share', False):
                    vals.setdefault('action_id', dashboard_action.id)
        return super().create(vals_list)
