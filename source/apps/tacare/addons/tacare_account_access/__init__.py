from . import models
from . import controllers


def post_init_hook(env):
    """Assign explicit functional groups to pre-existing accounts on fresh install."""
    users = env['res.users'].sudo().search([('tacare_account_role', 'in', ['business', 'candidate'])])
    users._tacare_sync_role_groups()
