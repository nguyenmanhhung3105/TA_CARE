"""Run in an Odoo shell on DEV. QA rows are rolled back."""

from odoo import fields
from odoo.exceptions import ValidationError


def check(env):
    site = env['website'].sudo().search([('domain', 'ilike', 'khovieclam.localhost')], limit=1)
    assert site, 'Missing local Kho việc làm website'
    organization = env['res.partner'].sudo().create({'name': 'QA KVL temporary organization',
                                                      'is_company': True})
    sectors = env['care.job.sector'].sudo().search([
        ('code', 'in', ['ecommerce', 'sales', 'marketing', 'health'])])
    assert len(sectors) == 4, 'Four example sectors must be configurable catalog records'
    cases = {
        'ecommerce': ('tool', 'Excel', 'office'),
        'sales': ('certificate', 'Giấy phép lái xe A1', 'office'),
        'marketing': ('evidence', 'Portfolio bài viết', 'hybrid'),
        'health': ('major', 'Điều dưỡng', 'office'),
    }
    for sector in sectors:
        category, criterion, mode = cases[sector.code]
        job = env['hr.job'].sudo().create({
            'name': 'QA ' + sector.name, 'care_position': 'Thực tập sinh',
            'care_sector_id': sector.id, 'tacare_type': 'internship',
            'tacare_mode': mode, 'tacare_location': 'Hà Nội',
            'tacare_description_text': 'Hỗ trợ công việc theo hướng dẫn.',
            'description': '<p>Hỗ trợ công việc theo hướng dẫn.</p>',
            'tacare_deadline': fields.Date.add(fields.Date.today(), months=6),
            'tacare_status': 'draft', 'company_id': env.company.id,
            'website_id': site.id, 'tacare_owner_partner_id': organization.id,
            'care_requirement_ids': [(0, 0, {'category': category,
                                              'name': criterion, 'mandatory': True})],
        })
        assert not job._care_publish_errors(), (sector.code, job._care_publish_errors())
        assert job.care_requirement_ids.category == category
        assert job.tacare_status == 'draft'
    incomplete = env['hr.job'].sudo().create({
        'name': 'QA incomplete draft', 'company_id': env.company.id,
        'website_id': site.id, 'tacare_owner_partner_id': organization.id,
    })
    assert incomplete._care_publish_errors(), 'Incomplete draft was incorrectly publishable'
    try:
        with env.cr.savepoint():
            incomplete.write({'care_days_per_week': 8})
    except ValidationError:
        pass
    else:
        raise AssertionError('Invalid weekly schedule was accepted')
    print('PASS: four sectors, structured mandatory requirements, incomplete draft and schedule constraint')


try:
    check(env)
finally:
    env.cr.rollback()
