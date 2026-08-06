from . import models
from . import wizard
from . import controllers


def post_init_hook(env):
    """On a fresh install, make School CRM the landing page for every existing
    internal user (new users get this automatically via ResUsers.create)."""
    dashboard_action = env.ref('edu_crm.action_edu_dashboard', raise_if_not_found=False)
    if dashboard_action:
        env['res.users'].search([('share', '=', False)]).write({'action_id': dashboard_action.id})
