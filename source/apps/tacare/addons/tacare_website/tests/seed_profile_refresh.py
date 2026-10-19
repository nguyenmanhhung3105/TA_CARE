"""LOCAL only. Account input is private runtime JSON, never a committed password fixture."""
import hashlib
import json
from pathlib import Path


def seed(env):
    assert env.cr.dbname == 'tacare_local'
    assert env['website'].sudo().search_count([('domain', 'ilike', 'tuhoso.localhost')])
    path = Path('/var/lib/odoo/profile_refresh_accounts.json')
    data = json.loads(path.read_text())
    logins = [a['login'] for a in data['accounts']]
    assert set(logins) == {'ungvien1@tacare.vn', 'ungvien2@tacare.vn'}
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users WHERE login != ALL(%s) ORDER BY id', [logins])
    before = hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
    users = env['res.users'].sudo().with_context(no_reset_password=True, mail_create_nosubscribe=True, tracking_disable=True)
    profiles = env['tacare.profile'].sudo()
    capabilities = env['care.profile.capability'].sudo()
    vnd = env.ref('base.VND')
    hcm = env['res.country.state'].sudo().search([('country_id.code','=','VN'),('name','ilike','Hồ Chí Minh')],limit=1)
    for number, account in enumerate(data['accounts'],1):
        user = users.with_context(active_test=False).search([('login','=',account['login'])],limit=1)
        vals = {'name':account['name'],'login':account['login'],'password':account['password'],
                'tacare_account_role':'candidate','active':True}
        if user:
            assert not user._is_internal(), 'Do not change an internal account'
            user.write(vals)
        else:
            user = users.create({**vals,'email':account['login'], 'company_id':env.company.id,
                                 'company_ids':[(6,0,[env.company.id])]})
        position = env.ref('tacare_website.position_' + ('it_frontend' if number == 1 else 'marketing_content'))
        title = 'Frontend Junior' if number == 1 else 'Content Marketing'
        for kind in ('recruitment','flexible'):
            key = 'refresh-uv%s-%s' % (number,kind)
            profile = profiles.search([('flex_demo_key','=',key)],limit=1)
            profile_vals = {'user_id':user.id,'name':account['name'],'flex_demo_key':key,
                'profile_title': ('Ứng tuyển ' + title) if kind == 'recruitment' else (
                    'Nhận chăm cây cuối tuần' if number == 1 else 'Dọn nhà theo giờ'),
                'care_recruitment_enabled':kind == 'recruitment', 'scope':'private','visible':False}
            if kind == 'recruitment':
                profile_vals.update(headline=title,sector=position.sector_id.code,desired_position_id=position.id,
                    region_id=hcm.id,location='TP. Hồ Chí Minh', mode='hybrid' if number == 1 else 'office',
                    desired_type='employment',work_fraction='full', salary_min=9000000 if number == 1 else 10000000,
                    salary_currency_id=vnd.id,salary_period='month',bio=(
                        'Tôi muốn ứng tuyển vị trí Frontend Junior, tập trung giao diện web và kiểm thử trên điện thoại.' if number == 1 else
                        'Tôi muốn làm nội dung cho website và mạng xã hội, có khả năng lên kế hoạch và biên tập bài viết.'),
                    work_history='Dự án thực hành cá nhân và phối hợp nhóm. Nội dung hư cấu phục vụ demo.',
                    education_details='Thông tin mẫu cho hồ sơ thử nghiệm.')
            else:
                profile_vals['bio'] = 'Tôi nhận chăm cây nhỏ và thay chậu vào cuối tuần.' if number == 1 else 'Tôi nhận dọn căn hộ theo giờ trong khu vực đã khai.'
            profile.write(profile_vals) if profile else None
            profile = profile or profiles.create(profile_vals)
            if kind == 'recruitment':
                for name in (['HTML / CSS','JavaScript'] if number == 1 else ['Viết nội dung','Biên tập']):
                    if not profile.skill_ids.filtered(lambda s:s.name == name):
                        env['tacare.profile.skill'].sudo().create({'profile_id':profile.id,'name':name,'level':'good',
                            'use':'Đã sử dụng trong dự án thực hành; nội dung demo.'})
            else:
                codes = ['gardening','repot'] if number == 1 else ['floor','kitchen','bathroom']
                values = {'profile_id':profile.id,'title':profile_vals['profile_title'],'description':profile_vals['bio'],
                    'flex_demo_key':key,'flex_category_id':env.ref('tacare_website.flex_category_' + ('garden' if number == 1 else 'cleaning')).id,
                    'flex_skill_ids':[(6,0,[env.ref('tacare_website.flex_skill_'+code).id for code in codes])],
                    'flex_mode':'onsite','flex_region_id':hcm.id,
                    'flex_location':'Khu vực Thủ Đức, TP.HCM' if number == 1 else 'Khu vực Bình Thạnh, TP.HCM',
                    'flex_schedule':'recurring' if number == 1 else 'flexible','flex_weekdays':'5,6' if number == 1 else False,
                    'flex_time_from':'08:00' if number == 1 else False,'flex_time_to':'11:00' if number == 1 else False,
                    'flex_schedule_note':'Hẹn trước một ngày, giá tùy phạm vi công việc.',
                    'flex_duration':3,'flex_rate_min':80000 if number == 1 else 65000,
                    'flex_rate_max':100000 if number == 1 else 80000,'flex_pay_unit':'hour','flex_pay_basis':'person',
                    'currency_id':vnd.id,'flex_min_hours':2,'flex_tools':'client','flex_negotiable':True,
                    'flex_cost_note':'Khách chuẩn bị vật tư và dụng cụ; giá mẫu phục vụ demo.','flex_state':'available'}
                cap = capabilities.search([('flex_demo_key','=',key)],limit=1)
                cap.write(values) if cap else capabilities.create(values)
        account['user_id'] = user.id
        account['profile_ids'] = profiles.search([('user_id','=',user.id)],order='id').ids
        assert len(account['profile_ids']) == 2
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users WHERE login != ALL(%s) ORDER BY id', [logins])
    assert before == hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
    data['unchanged_other_accounts_fingerprint'] = before
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2));path.chmod(0o600)
    env.cr.commit()
    print('PASS: two requested local candidate accounts, two profiles per candidate, two service offers; all other account credentials/roles preserved.')


seed(env)
