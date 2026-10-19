"""Meaningful local ORM checks for field semantics. All data is rolled back."""
from odoo import fields
from odoo.exceptions import ValidationError


def check(env):
    position = env.ref('tacare_website.position_it_frontend')
    other = env.ref('tacare_website.position_it_backend')
    candidate = env['res.users'].sudo().with_context(no_reset_password=True).create({
        'name': 'QA v2 candidate', 'login': 'qa-v2-rollback@example.invalid',
        'tacare_account_role': 'candidate'})
    profile = env['tacare.profile'].sudo().create({'user_id': candidate.id, 'name': 'QA v2',
        'desired_position_id': position.id, 'sector': 'it', 'mode': 'remote'})
    job = env['hr.job'].sudo().create({'name': 'QA v2 frontend', 'care_position_id': position.id,
        'care_position': position.name, 'care_sector_id': position.sector_id.id,
        'tacare_type': 'employment', 'care_work_fraction': 'full', 'tacare_mode': 'hybrid',
        'tacare_required_skills': 'JavaScript, TypeScript', 'care_skills_any': True,
        'care_experience_min': 1, 'care_salary_display': 'range', 'care_salary_basis': 'base',
        'care_salary_tax': 'gross', 'care_income_period': 'month',
        'care_salary_min': 10000000, 'care_salary_max': 20000000,
        # Application deadline before the start date is normal.
        'tacare_deadline': fields.Date.add(fields.Date.today(), months=1),
        'tacare_start': fields.Date.add(fields.Date.today(), months=2)})
    result = job._care_compare_profile(profile, allow_profile=True, allow_skills=True)
    find = lambda result, prefix: next(x for x in result['comparisons'] if x['name'].startswith(prefix))
    assert find(result, 'Kinh nghiệm')['result'] == 'unknown'
    assert find(result, 'Hình thức')['result'] == 'unmet', 'Hybrid must not automatically match remote'
    assert find(result, 'Một trong')['result'] == 'unknown', 'Missing skills are not failure'
    profile.write({'experience_known': True, 'relevant_months': 0})
    assert find(job._care_compare_profile(profile, True, True), 'Kinh nghiệm')['result'] == 'unmet'
    profile.write({'relevant_months': 24, 'salary_min': 15000000, 'salary_currency_id': job.care_currency_id.id,
                   'salary_period': 'month', 'salary_tax': 'gross'})
    env['tacare.profile.skill'].sudo().create({'profile_id': profile.id, 'name': 'JavaScript'})
    result = job._care_compare_profile(profile, True, True)
    assert find(result, 'Kinh nghiệm')['result'] == 'met'
    assert find(result, 'Một trong')['result'] == 'met', 'OR group only needs one declared skill'
    assert find(result, 'Lương')['result'] == 'met'
    profile.write({'desired_position_id': other.id})
    assert find(job._care_compare_profile(profile, True, True), 'Kinh nghiệm')['result'] == 'unknown'
    job.write({'care_salary_basis': 'total', 'care_license_note': 'Giấy phép hành nghề'})
    result = job._care_compare_profile(profile, True, True)
    assert find(result, 'Lương')['result'] == 'unknown', 'Total income is not base salary'
    assert find(result, 'Giấy phép')['result'] == 'unknown'
    hidden = job._care_compare_profile(profile, False, False)
    assert not hidden['matched'] and not hidden['preferred_found']
    assert all(row['result'] == 'unknown' for row in hidden['comparisons'])
    for vals in [{'salary_min': float('nan')}, {'relevant_months': -1}]:
        try:
            with env.cr.savepoint():
                profile.write(vals)
        except ValidationError:
            pass
        else:
            raise AssertionError('Invalid profile value accepted')
    print('PASS v2: unknown vs zero, occupation-specific experience, hybrid, OR skills, salary basis, consent scopes, finite values, deadline before start')


try:
    check(env)
finally:
    env.cr.rollback()
