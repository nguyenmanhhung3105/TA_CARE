"""Manual local normalization of existing account-owned marketplace records.

No account/contact/profile creation. Names and prose become ordinary product
data; existing IDs, technical provenance keys, terms, ownership and permissions
are preserved. Unused historical/QA contacts are archived, never deleted.
"""
import re
from odoo.exceptions import ValidationError

APPROVED = {'ungvien1@tacare.vn', 'ungvien2@tacare.vn', 'student.test@tuhoso.com',
            'ungvien1@tuhoso.com', 'ungvien2@tuhoso.com'}


def normalize_account_records(env, apply=False):
    if env.cr.dbname != 'tacare_local':
        raise ValidationError('Chỉ dùng trên tacare_local.')
    sites = env['website'].sudo().search([('care_site_kind', 'in', ['tacare', 'khovieclam', 'tuhoso'])])
    if len(sites) != 3 or any('.localhost' not in (s.domain or '') for s in sites):
        raise ValidationError('Chỉ dùng cho bộ website localhost đã kiểm tra.')
    users = env['res.users'].sudo().with_context(active_test=False)
    profiles = env['tacare.profile'].sudo().search([
        '|', ('flex_demo_key', '=like', 'matching-20261024-%'), ('flex_demo_key', '=like', 'refresh-%-flexible')])
    if any(p.user_id.login not in APPROVED or not p.user_id.active for p in profiles):
        raise ValidationError('Hồ sơ không thuộc tài khoản cá nhân đã được chỉ định.')
    protected = env['res.company'].sudo().search([]).mapped('partner_id') | sites.mapped('user_id.partner_id')
    legacy = users.search([('login', '=like', 'demo-flex-%@example.invalid')]).filtered(
        lambda u: re.fullmatch(r'demo-flex-(?:0\d|1[0-5])@example\.invalid', u.login or ''))
    if any(legacy.mapped('active')):
        raise ValidationError('Không lưu trữ liên hệ khi tài khoản cũ còn hoạt động.')
    qa = env['res.partner'].sudo().search([('active', '=', True), ('name', '=like', 'QA %')]).filtered(
        lambda p: not users.search_count([('partner_id', '=', p.id)]) and p not in protected)
    contacts = (legacy.mapped('partner_id') | qa).filtered('active')
    if any(users.search_count([('partner_id', '=', p.id), ('active', '=', True)]) or p in protected for p in contacts):
        raise ValidationError('Liên hệ đang có tài khoản hoạt động hoặc được hệ thống sử dụng.')
    plan = dict(profiles=profiles.ids, offers=profiles.capability_ids.ids, archive_contacts=contacts.ids)
    if not apply:
        return plan
    for profile in profiles:
        display = re.sub(r'\bdemo\b\s*', '', profile.user_id.name, flags=re.I).strip()
        if display != profile.name:
            profile.write({'name': display})
        matching = (profile.flex_demo_key or '').startswith('matching-20261024-')
        if matching:
            title = re.sub(r'^\[Demo matching\]\s*', '', profile.profile_title or '')
            # Different price/service scopes remain different ordinary records;
            # no algorithm outcome is put into a title or a biography.
            if profile.flex_demo_key.endswith('-conflict') and not title.endswith(' · Thỏa thuận riêng'):
                title += ' · Thỏa thuận riêng'
            description = profile.capability_ids[:1].description or ''
            description = re.sub(r'^DỮ LIỆU DEMO HƯ CẤU\.\s*', '', description)
            description = re.sub(r' Mẫu đối chứng:.*$', '', description)
            values = dict(profile_title=title, headline=title,
                bio=description, goal='Trao đổi rõ phạm vi, lịch và tiền công trước khi nhận làm.')
            changed = {name: value for name, value in values.items() if profile[name] != value}
            if changed:
                profile.write(changed)
        elif (profile.bio or '').startswith('HỒ SƠ MẪU HƯ CẤU.'):
            profile.write({'bio': profile.bio.replace('HỒ SƠ MẪU HƯ CẤU. ', '', 1)})
        for offer in profile.capability_ids:
            values = {}
            for name in ('title', 'description', 'flex_schedule_note', 'flex_cost_note', 'flex_experience'):
                value = offer[name] or ''
                clean = re.sub(r'^\[Mẫu thử\]\s*|^DỮ LIỆU DEMO HƯ CẤU\.\s*|^HỒ SƠ MẪU HƯ CẤU\.\s*', '', value)
                clean = re.sub(r' Mẫu đối chứng:.*$', '', clean)
                clean = clean.replace('Giá giả lập.', '').replace('giá mẫu phục vụ demo', 'tiền công cần chốt theo phạm vi thực tế').strip()
                clean = re.sub(r'Hồ sơ và giấy tờ là dữ liệu[^.]*\.',
                    'Giấy tờ, phương tiện và điều kiện thực hiện cần được kiểm tra trước khi nhận việc.', clean)
                clean = clean.replace('Chỉ là ví dụ khảo sát biểu mẫu chuyến đi; thời gian và giá phải trao đổi lại.',
                    'Lịch và giá cần được trao đổi theo từng hành trình.')
                clean = clean.replace('trong demo.', 'trên hệ thống.')
                if matching and name == 'flex_schedule_note':
                    clean = 'Cần xác nhận lại ngày và khung giờ trống trước khi nhận việc.'
                if matching and name == 'flex_cost_note':
                    clean = 'Vật tư, di chuyển và phát sinh thống nhất riêng trước khi thực hiện.'
                if name == 'flex_experience':
                    clean = 'Trao đổi kinh nghiệm liên quan và yêu cầu thực hiện trước khi thống nhất nhận việc.'
                if clean != value:
                    values[name] = clean
            if values:
                offer.write(values)
    if contacts:
        # The legacy lookup includes archived users. Restore native active-user
        # filtering before archiving their contacts; do not bypass Odoo's guard.
        contacts.with_context(active_test=True).write({'active': False})
    firms = env['care.org.member'].sudo().search([
        ('state', '=', 'active'), ('user_id.active', '=', True),
        ('user_id.login', '=like', '%.demo@khovieclam.vn')]).mapped('organization_id')
    for firm in firms:
        if firm.name.endswith(' · Demo'):
            firm.write({'name': firm.name.removesuffix(' · Demo')})
    env['care.audit.event'].sudo().create(dict(company_id=env.company.id, actor_user_id=env.user.id,
        action='local.account_bound_records.normalized', target_model='tacare.profile',
        target_res_id=profiles[:1].id or 0, changes=plan,
        reason='Chủ dự án yêu cầu dùng hồ sơ thông thường của tài khoản hiện có; lưu trữ liên hệ thừa, giữ nguyên quyền.'))
    return plan
