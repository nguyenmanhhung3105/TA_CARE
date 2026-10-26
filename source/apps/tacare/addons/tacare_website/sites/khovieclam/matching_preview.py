"""Anonymous homepage projections; never return provider records or pair IDs."""
from odoo import fields


def matching_previews(env):
    """At most two public needs with a current, consented algorithm suggestion.

    The owner authorized this marketing projection, not public profile access.
    Privileged reads stay inside this function: only published job fields and
    the existence of a qualifying suggestion leave it. Private profile values,
    reasons, identities and identifiers are deliberately absent from the result.
    No consent is created, widened or renewed by reading the homepage.
    """
    websites = env['website'].sudo()
    kho = websites.search([('domain', 'ilike', 'khovieclam')], limit=1)
    tu = websites.search([('domain', 'ilike', 'tuhoso')], limit=1)
    if not kho or not tu:
        return []
    jobs = env['hr.job'].sudo().search([
        ('website_id', '=', kho.id), ('company_id', '=', kho.company_id.id),
        ('care_opportunity_kind', '=', 'flexible'), ('tacare_status', '=', 'published'),
        ('is_published', '=', True), ('care_remaining_slots', '>', 0),
        ('care_matching_enabled', '=', True), ('tacare_owner_user_id.active', '=', True),
        '|', ('tacare_deadline', '=', False), ('tacare_deadline', '>=', fields.Date.today()),
    ], order='write_date desc, id desc', limit=40)
    profiles = env['tacare.profile'].sudo().search([
        ('company_id', '=', tu.company_id.id), ('care_recruitment_enabled', '=', False),
        ('visible', '=', True), ('status', '=', 'active'), ('scope', '!=', 'private'),
        ('user_id.active', '=', True),
    ], order='id desc', limit=200)
    consents = env['care.consent'].sudo().search([
        ('profile_id', 'in', profiles.ids), ('state', '=', 'granted'),
        ('purpose', 'in', ['discovery', 'matching']),
    ])
    by_profile = {profile.id: [] for profile in profiles}
    for consent in consents:
        by_profile[consent.profile_id.id].append(consent)

    previews, categories = [], set()
    for job in jobs:
        if not job.tacare_owner_partner_id or job.flex_category_id.id in categories:
            continue
        for profile in profiles:
            if profile.user_id == job.tacare_owner_user_id:
                continue
            grants = by_profile[profile.id]
            if not all(any(c.is_current(purpose, job.tacare_owner_partner_id, field)
                           for c in grants) for purpose, field in [
                               ('discovery', 'profile'), ('matching', 'profile'),
                               ('matching', 'skills')]):
                continue
            reason = job._care_compare_profile(profile, allow_profile=True, allow_skills=True)
            if not reason.get('eligible') or not reason.get('rank'):
                continue
            previews.append({
                'job_title': job.name, 'category': job.flex_category_id.name,
                'photo': job._care_photo_url(),
                'region': job.flex_region_id.name or job._flex_label('flex_mode'),
                'schedule': job._flex_label('flex_schedule'),
                'price': job._flex_price_label(),
            })
            categories.add(job.flex_category_id.id)
            break
        if len(previews) == 2:
            break
    return previews
