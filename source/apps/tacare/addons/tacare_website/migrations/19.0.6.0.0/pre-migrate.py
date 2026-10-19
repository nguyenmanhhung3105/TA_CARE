"""Keep profile IDs/data; remove only the obsolete one-profile-per-user constraint."""
from odoo.tools import sql


def migrate(cr, version):
    # The previous child targets a photo node removed from the new parent.
    # Disable it during parent validation; its XML is updated/reactivated below.
    cr.execute("""UPDATE ir_ui_view SET active = false WHERE id IN (
        SELECT res_id FROM ir_model_data WHERE module = 'tacare_website'
        AND name = 'work_hub_home' AND model = 'ir.ui.view')""")
    name = 'tacare_profile_unique_user'
    if sql.constraint_definition(cr, 'tacare_profile', name):
        sql.drop_constraint(cr, 'tacare_profile', name)
