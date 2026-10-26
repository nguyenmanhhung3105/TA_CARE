"""Rollback-only lifecycle, review publication, privacy and capacity checks."""
from datetime import timedelta
from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.addons.tacare_website.tools.matching_demo import prepare_matching_demo
from odoo.addons.tacare_website.tools.map_test_profiles import account

assert env.cr.dbname == 'tacare_local'

def denied(operation, kind=ValidationError):
    try:
        with env.cr.savepoint():
            operation()
    except kind:
        return
    raise AssertionError('Forbidden operation succeeded')

try:
    originals = env['tacare.profile'].sudo().search([('flex_demo_key', 'not like', 'matching-20261024-')])
    original_state = [(p.id, p.visible, p.scope, p.user_id.id, p.version) for p in originals]
    cases = prepare_matching_demo(env, apply=True)
    assert len(cases) >= 9
    for job_id, profile_id, variant in cases:
        job = env['hr.job'].sudo().browse(job_id)
        profile = env['tacare.profile'].sudo().browse(profile_id)
        result = job._care_compare_profile(profile, allow_profile=True, allow_skills=True)
        assert result['eligible'] == (variant == 'fit'), (job_id, profile_id, variant)
        if variant == 'fit':
            assert result['capability_id'] in profile.capability_ids.ids
        assert not env['care.consent'].sudo().search_count([('profile_id', '=', profile.id), ('purpose', '=', 'contact')])
        consents = env['care.consent'].sudo().search([('profile_id', '=', profile.id)])
        assert len(consents) == 2 and all(c.recipient_partner_id == job.tacare_owner_partner_id and c.valid_until for c in consents)
    assert original_state == [(p.id, p.visible, p.scope, p.user_id.id, p.version) for p in originals]
    assert prepare_matching_demo(env, apply=True) == cases  # no duplication or reset
    source = env['hr.job'].sudo().browse(cases[0][0])
    buyer = source.tacare_owner_user_id
    providers = env['res.users'].sudo().browse([account(env, key).id for key in
        ('provider_home', 'provider_green', 'provider_manual')]).sorted('id')
    job = source.copy({'name': 'QA work review - rollback', 'no_of_recruitment': 1, 'flex_demo_key': False,
        'tacare_status': 'published', 'is_published': True,
        'tacare_owner_user_id': buyer.id, 'tacare_owner_partner_id': source.tacare_owner_partner_id.id})
    order = env['care.work.order'].sudo().create({'job_id': job.id})
    entries = []
    for user in providers[:2]:
        p = env['tacare.profile'].sudo().create({'user_id': user.id, 'name': 'QA rollback participant'})
        cap = env['care.profile.capability'].sudo().create(dict(profile_id=p.id, title='QA dịch vụ',
            description='QA mô phỏng', flex_category_id=job.flex_category_id.id, flex_state='available'))
        c = env['tacare.connection'].sudo().create(dict(type='application', job_id=job.id,
            profile_id=p.id, sender_id=user.id, receiver_id=buyer.id, status='accepted'))
        participation = env['care.work.participation'].sudo().create(dict(work_order_id=order.id,
            connection_id=c.id, profile_id=p.id, capability_id=cap.id, buyer_partner_id=c.organization_id.id,
            provider_user_id=user.id, terms='QA thỏa thuận cụ thể để kiểm thử; rollback toàn bộ.'))
        entries.append(participation)
    one, two = entries
    denied(lambda: one._review(buyer, 5, 'Chưa hoàn thành'))
    denied(lambda: one._act(providers[2], 'confirm'), AccessError)
    one._act(one.provider_user_id, 'confirm')
    assert one.state == 'proposed' and job.care_remaining_slots == 1
    one._act(buyer, 'confirm')
    assert one.state == 'confirmed' and job.care_remaining_slots == 0
    two._act(two.provider_user_id, 'confirm')
    denied(lambda: two._act(buyer, 'confirm'))
    assert two.state == 'proposed'
    denied(lambda: one._review(buyer, 5, 'Chưa hoàn thành'))
    one._act(buyer, 'start')
    one._act(one.provider_user_id, 'complete')
    assert one.state == 'completion_pending'
    denied(lambda: one._review(buyer, 5, 'Chưa đủ xác nhận'))
    denied(lambda: one._act(one.provider_user_id, 'complete'))
    one._act(buyer, 'complete')
    assert one.state == 'completed' and one.completed_at and job.care_remaining_slots == 0
    denied(lambda: one._review(buyer, 0, 'Không hợp lệ'))
    denied(lambda: one._review(buyer, 6, 'Không hợp lệ'))
    denied(lambda: one._review(buyer, 5, 'a'))
    denied(lambda: one._review(providers[2], 5, 'Người ngoài'), AccessError)
    first = one._review(buyer, 4, 'Hoàn thành đúng phạm vi đã trao đổi.')
    assert not first.published
    assert not env['care.feedback']._summary(profile=one.profile_id)['count']
    denied(lambda: one._review(buyer, 5, 'Đánh giá lặp'))
    second = one._review(one.provider_user_id, 5, 'Yêu cầu rõ ràng, phối hợp đúng lịch.')
    first.invalidate_recordset()
    assert first.published and second.published
    provider_summary = env['care.feedback']._summary(profile=one.profile_id)
    buyer_summary = env['care.feedback']._summary(buyer=one.buyer_partner_id)
    assert provider_summary['average'] == 4 and buyer_summary['average'] == 5
    limited_admin = env['res.users'].sudo().with_context(no_reset_password=True).create({
        'name': 'QA limited review administrator', 'login': 'qa-review-limited@example.invalid',
        'company_id': one.profile_id.company_id.id, 'company_ids': [(6, 0, one.profile_id.company_id.ids)],
        'group_ids': [(6, 0, [env.ref('base.group_user').id, env.ref('base.group_system').id])]})
    for model, record in [('care.work.order', order), ('care.work.participation', one), ('care.feedback', first)]:
        scoped = env[model].with_user(limited_admin).with_context(allowed_company_ids=limited_admin.company_ids.ids)
        assert not scoped.search([('id', '=', record.id)])
    denied(lambda: one._act(limited_admin, 'complete'), AccessError)
    denied(lambda: first.write({'rating': 5}))
    denied(lambda: first.unlink())
    first.write({'moderation': 'hidden', 'moderation_reason': 'QA kiểm duyệt rollback'})
    assert not first.published and not env['care.feedback']._summary(profile=one.profile_id)['count']
    for user in providers:
        for model in ('care.work.order', 'care.work.participation', 'care.feedback'):
            denied(lambda: env[model].with_user(user).search([]), AccessError)
        denied(lambda: one.with_user(user).write({'state': 'completed'}), AccessError)
    # Deadline publication, without requiring a second review.
    another_job = source.copy({'name': 'QA expiry - rollback', 'flex_demo_key': False,
        'tacare_status': 'published', 'is_published': True,
        'tacare_owner_user_id': buyer.id, 'tacare_owner_partner_id': source.tacare_owner_partner_id.id})
    another_order = env['care.work.order'].sudo().create({'job_id': another_job.id})
    c = one.connection_id.copy({'job_id': another_job.id})
    late = one.copy({'work_order_id': another_order.id, 'connection_id': c.id,
        'state': 'completed', 'buyer_completed': True, 'provider_completed': True,
        'completed_at': fields.Datetime.now() - timedelta(days=15)})
    late_review = late._review(buyer, 3, 'Phản hồi sau thời hạn thử nghiệm.')
    assert late_review.published
    two._act(two.provider_user_id, 'cancel')
    assert two.state == 'cancelled'
    print('PASS: demo matrix, original privacy, exact offer, participant roles, last slot, both confirmations, '
          'early/outsider/duplicate denial, blind publication, 14-day expiry, immutable reviews, moderation, '
          'profile/buyer aggregates and portal ACL. All changes rolled back.')
finally:
    env.cr.rollback()
