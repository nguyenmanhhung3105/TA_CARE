"""Run with Odoo shell on a DEV DB. All QA records are rolled back."""

from odoo.exceptions import AccessError


def check(env):
    partner = env['res.partner'].sudo()
    users = env['res.users'].sudo()
    jobs = env['hr.job'].sudo()
    profiles = env['tacare.profile'].sudo()
    site = env['website'].sudo().search([('domain', 'ilike', 'khovieclam.localhost')], limit=1)
    assert site, 'Local Kho Việc Làm website is missing'

    organizations = [partner.create({'name': f'QA Org {i}', 'is_company': True}) for i in (1, 2)]
    businesses = []
    candidates = []
    for i, organization in enumerate(organizations, 1):
        person = partner.create({'name': f'QA Business {i}', 'parent_id': organization.id})
        businesses.append(users.create({
            'name': f'QA Business {i}', 'login': f'qa-business-{i}@example.invalid',
            'partner_id': person.id, 'tacare_account_role': 'business',
        }))
        candidates.append(users.create({
            'name': f'QA Candidate {i}', 'login': f'qa-candidate-{i}@example.invalid',
            'tacare_account_role': 'candidate',
        }))
    assert all(u.has_group('tacare_account_access.group_tacare_business') for u in businesses)
    assert all(u.has_group('tacare_account_access.group_tacare_candidate') for u in candidates)

    membership = env['care.org.member'].sudo().create({
        'company_id': env.company.id, 'organization_id': organizations[0].id,
        'user_id': businesses[0].id, 'role': 'viewer', 'state': 'active',
    })
    assert businesses[0].care_organization_ids == organizations[0]
    membership.write({'state': 'suspended'})
    assert not businesses[0].care_organization_ids, 'Suspended membership fell back to partner ownership'
    membership.write({'state': 'active', 'role': 'owner'})

    job_records = [jobs.create({
        'name': f'QA Job {i}', 'company_id': env.company.id, 'website_id': site.id,
        'tacare_owner_partner_id': organization.id,
        'tacare_owner_user_id': business.id,
    }) for i, (organization, business) in enumerate(zip(organizations, businesses), 1)]
    profile_records = [profiles.create({'name': f'QA Candidate {i}', 'user_id': candidate.id})
                       for i, candidate in enumerate(candidates, 1)]

    for index, business in enumerate(businesses):
        visible = jobs.with_user(business).search([('id', 'in', [item.id for item in job_records])])
        assert visible == job_records[index], 'Business saw a foreign job'
    for index, candidate in enumerate(candidates):
        visible = profiles.with_user(candidate).search([('id', 'in', [item.id for item in profile_records])])
        assert visible == profile_records[index], 'Candidate saw a foreign profile'

    try:
        with env.cr.savepoint():
            profiles.with_user(candidates[0]).browse(profile_records[1].id).write({'name': 'ILLEGAL'})
    except AccessError:
        pass
    else:
        raise AssertionError('Candidate portal write unexpectedly allowed')

    consent = env['care.consent'].sudo().create({
        'profile_id': profile_records[0].id, 'purpose': 'contact',
        'recipient_kind': 'organization', 'recipient_partner_id': organizations[0].id,
        'field_scope': ['email'], 'state': 'granted', 'granted_by': candidates[0].id,
    })
    assert consent.is_current('contact', organizations[0], 'email')
    assert not consent.is_current('contact', organizations[1], 'email')
    consent.write({'state': 'revoked'})
    assert not consent.is_current('contact', organizations[0], 'email')
    print('PASS: two organizations, two candidates, isolated records, blocked portal write, scoped contact consent and revocation')


try:
    check(env)
finally:
    env.cr.rollback()
