"""Compatibility lookup for the retired local matching fixture.

Existing account-owned IDs and provenance keys stay valid. Creating synthetic
profiles/contacts is no longer allowed by the owner; use the normal owner form.
"""
from odoo.exceptions import ValidationError
from .map_test_profiles import account

LOGINS = ('ungvien1@tacare.vn', 'ungvien2@tacare.vn', 'student.test@tuhoso.com')
PREFIX = 'matching-20261024-'
CATEGORY_CODES = ('cleaning', 'cooking', 'loading', 'garden', 'farm', 'repair', 'tutoring', 'digital', 'pets')


def prepare_matching_demo(env, apply=False):
    if env.cr.dbname != 'tacare_local':
        raise ValidationError('Công cụ này chỉ dùng trên tacare_local.')
    sites = env['website'].sudo().search([('care_site_kind', 'in', ['khovieclam', 'tuhoso', 'tacare'])])
    if len(sites) != 3 or any('.localhost' not in (s.domain or '') for s in sites):
        raise ValidationError('Chỉ tạo mẫu trong bộ ba website localhost.')
    accounts = [account(env, key) for key in ('provider_home', 'provider_green', 'provider_manual')]
    if any(len(u) != 1 or not u.active or u.tacare_account_role != 'candidate' for u in accounts):
        raise ValidationError('Thiếu tài khoản cá nhân demo đã được chỉ định.')
    kho = sites.filtered(lambda s: s.care_site_kind == 'khovieclam')
    jobs = env['hr.job'].sudo().search([('website_id', '=', kho.id), ('company_id', '=', kho.company_id.id),
        ('care_opportunity_kind', '=', 'flexible'), ('tacare_status', '=', 'published'), ('is_published', '=', True),
        ('care_remaining_slots', '>', 0), ('flex_pay_unit', '!=', 'trip')], order='id')
    selected = []
    for code in CATEGORY_CODES:
        job = jobs.filtered(lambda j: j.flex_category_id.code == code)[:1]
        if job:
            selected.append((job, 'fit'))
    if not selected:
        raise ValidationError('Không có tin thời vụ mẫu đang mở.')
    selected += [(j, 'conflict') for j, _ in selected[:3]]
    result = []
    for i, (job, variant) in enumerate(selected):
        user = accounts[i % len(accounts)]
        key = PREFIX + str(job.id) + '-' + variant
        profiles = env['tacare.profile'].sudo()
        profile = profiles.search([('flex_demo_key', '=', key)])
        if profile:
            if len(profile) != 1 or profile.user_id != user or profile.source_job_id != job:
                raise ValidationError('Mẫu đã tồn tại nhưng không đúng chủ hoặc tin tham khảo.')
            result.append((job.id, profile.id, variant))
            continue
        if not apply:
            result.append((job.id, False, variant))
            continue
        raise ValidationError('Không tự tạo thêm hồ sơ demo. Tạo hồ sơ thông thường từ tài khoản hiện có.')
    return result
