"""Manual LOCAL-only seed. Run in Odoo shell; no demo accounts/data load on install.

Creates 20 jobs (5 recruitment, 15 flexible), 15 profiles and 10 work capabilities.
Generated login secrets are written only to the ignored local runtime directory.
"""
import hashlib
import json
import os
import secrets
from datetime import timedelta
from pathlib import Path

from odoo import fields


def seed(env):
    assert env.cr.dbname == 'tacare_local', 'Local demo database only'
    site = env['website'].sudo().search([('domain', 'ilike', 'khovieclam.localhost')], limit=1)
    assert site, 'Local website required'
    users = env['res.users'].sudo().with_context(no_reset_password=True, mail_create_nosubscribe=True,
                                              tracking_disable=True)
    jobs = env['hr.job'].sudo()
    profiles = env['tacare.profile'].sudo()
    capabilities = env['care.profile.capability'].sudo()
    secret_path = Path('/var/lib/odoo/flexible_demo_accounts.json')
    credentials = json.loads(secret_path.read_text()) if secret_path.exists() else {'accounts': []}
    by_login = {x['login']: x for x in credentials['accounts']}
    env.cr.execute("SELECT id, login, password, active, tacare_account_role FROM res_users WHERE login NOT LIKE 'demo-flex-%' AND login NOT IN ('ungvien1@tacare.vn', 'ungvien2@tacare.vn') ORDER BY id")
    before = hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()

    def user(number, name, role='candidate'):
        login = 'demo-flex-%02d@example.invalid' % number
        record = users.with_context(active_test=False).search([('login', '=', login)], limit=1)
        if not record:
            password = secrets.token_urlsafe(24)
            record = users.create({'name': name, 'login': login, 'password': password,
                'email': login, 'tacare_account_role': role,
                'company_id': env.company.id, 'company_ids': [(6, 0, [env.company.id])]})
            by_login[login] = {'login': login, 'password': password, 'user_id': record.id, 'name': name}
        else:
            record.write({'name': name})
            if login in by_login:
                by_login[login].update(name=name, user_id=record.id)
        return record

    publisher = user(0, 'Đơn vị tuyển dụng Demo TA.CARE', 'business')
    publisher.partner_id.write({'is_company': True})
    vnd = env.ref('base.VND')
    today = fields.Date.today()
    states = env['res.country.state'].sudo().search([('country_id.code', '=', 'VN')])

    def region(text):
        found = states.filtered(lambda s: text.casefold() in s.name.casefold())
        assert found, 'Region missing: ' + text
        return found[0]

    hcm, hanoi, lamdong = region('Hồ Chí Minh'), region('Hà Nội'), region('Lâm Đồng')
    recruitment = [
        ('Lập trình Frontend · Sản phẩm giáo dục', 'it_frontend', 'it', 18000000, 25000000,
         'Phát triển giao diện web, phối hợp thiết kế và kiểm thử tính năng.', 'JavaScript, CSS', 'hybrid'),
        ('Nhân viên vận hành sàn thương mại điện tử', 'ecommerce_operation', 'ecommerce', 9000000, 12000000,
         'Theo dõi gian hàng, xử lý đơn, cập nhật nội dung sản phẩm và báo cáo tuần.', 'Excel, Vận hành gian hàng', 'office'),
        ('Content Marketing · Nội dung có chiều sâu', 'marketing_content', 'marketing', 10000000, 15000000,
         'Lập kế hoạch và viết nội dung cho website, phối hợp chiến dịch truyền thông.', 'Viết nội dung, Biên tập', 'hybrid'),
        ('Chuyên viên vận hành kho · Ca hành chính', 'logistics_warehouse', 'logistics', 8500000, 11000000,
         'Theo dõi xuất nhập tồn, sắp xếp kho và phối hợp giao nhận hàng hóa.', 'Quản lý kho, Excel', 'office'),
        ('Thiết kế đồ họa · Nhận ứng viên mới', 'design_graphic', 'design', 10000000, 14000000,
         'Thiết kế ấn phẩm số, chuẩn hóa hình ảnh và phối hợp các nhóm dự án.', 'Figma, Thiết kế đồ họa', 'remote'),
    ]
    demo_users = []
    for i, (title, position, sector, low, high, description, skills, mode) in enumerate(recruitment, 1):
        p = env.ref('tacare_website.position_' + position)
        vals = dict(name=title, company_id=env.company.id, website_id=site.id,
            tacare_owner_partner_id=publisher.partner_id.id, tacare_owner_user_id=publisher.id,
            care_opportunity_kind='recruitment', flex_demo_key='recruitment-%02d' % i,
            tacare_status='published', is_published=True, care_position=p.name,
            care_position_id=p.id, care_sector_id=p.sector_id.id, tacare_sector=sector,
            tacare_type='employment', tacare_mode=mode, care_work_fraction='full',
            care_region_id=hcm.id, tacare_location='TP. Hồ Chí Minh' if mode != 'remote' else 'Từ xa',
            tacare_description_text=description + '\nTin giả lập phục vụ trải nghiệm demo.',
            care_candidate_requirements='Có khả năng thực hiện công việc nêu trên; trao đổi rõ kinh nghiệm liên quan.',
            care_benefits='Có hướng dẫn ban đầu; môi trường phối hợp và phản hồi rõ ràng. Nội dung demo.',
            care_training_provided=True, tacare_required_skills=skills,
            tacare_schedule='Thứ Hai–thứ Sáu, 08:30–17:30', no_of_recruitment=1,
            care_salary_display='range', care_salary_basis='base', care_salary_tax='unknown',
            care_salary_min=low, care_salary_max=high, care_currency_id=vnd.id,
            care_income_period='month', tacare_deadline=today + timedelta(days=90),
            care_matching_enabled=False)
        record = jobs.search([('flex_demo_key', '=', vals['flex_demo_key'])], limit=1)
        record.write(vals) if record else jobs.create(vals)
        u = user(i, 'Hồ sơ demo %02d · %s' % (i, p.name))
        demo_users.append(u)
        profile = profiles.search([('user_id', '=', u.id), ('flex_demo_key', '=', 'profile-%02d' % i)], limit=1)
        values = dict(user_id=u.id, name=u.name, headline=p.name, bio='Hồ sơ hư cấu dùng thử nhánh tuyển dụng.',
            sector=sector, desired_position_id=p.id, region_id=hcm.id, location='TP. Hồ Chí Minh',
            mode=mode, desired_type='employment', work_fraction='full',
            salary_min=low, salary_currency_id=vnd.id, salary_period='month',
            care_recruitment_enabled=True, flex_demo_key='profile-%02d' % i,
            scope='private', visible=False)
        profile.write(values) if profile else profiles.create(values)

    # title, category, rate, unit, description, skill codes, mode, schedule, location
    work = [
        ('Dọn căn hộ 60m² sáng thứ Bảy', 'cleaning', 60000, 'hour',
         'Lau sàn, vệ sinh bếp và một nhà tắm trong căn hộ 60m². Không nấu ăn. Chủ có dụng cụ và hóa chất.', ['floor','kitchen','bathroom'], 'onsite', 'once', 'Khu vực Thủ Đức, TP.HCM'),
        ('Nấu bữa tối cho gia đình bốn người', 'cooking', 5000000, 'month',
         'Ba món mỗi bữa, thứ Hai–thứ Sáu 16–19 giờ; dọn bếp sau nấu. Chủ mua nguyên liệu, không gồm việc nhà khác.', ['cooking','dishes'], 'onsite', 'recurring', 'Khu vực Gò Vấp, TP.HCM'),
        ('Hai người bốc 40 thùng hàng vào kho', 'loading', 150000, 'shift',
         'Thùng 10–15kg, đưa từ xe vào kho tầng trệt. Chủ có xe đẩy. Chỉ thuê nhân công, không thuê xe chở.', ['loading'], 'onsite', 'once', 'Khu vực Bình Tân, TP.HCM'),
        ('Thay chậu cho 12 cây ban công', 'garden', 300000, 'task',
         'Thay chậu cây nhỏ, gom đất thừa vào bao tại nhà. Chủ có chậu, đất và sỏi; không gồm chở phế thải.', ['repot','gardening'], 'onsite', 'once', 'Khu vực Phú Nhuận, TP.HCM'),
        ('Cắt cỏ và dọn vườn cuối tuần', 'garden', 450000, 'task',
         'Vườn khoảng 80m², cắt cỏ và gom lá vào bao. Người làm mang máy cắt, không xử lý cây lớn.', ['mowing','gardening'], 'onsite', 'once', 'Khu vực Củ Chi, TP.HCM'),
        ('Phụ thu hoạch rau theo đợt ba ngày', 'farm', 280000, 'day',
         'Thu hoạch và phân loại rau theo hướng dẫn, mỗi ngày sáu giờ. Có dụng cụ và nơi nghỉ trưa. Dữ liệu nghề nông giả lập.', ['harvest'], 'onsite', 'once', 'Khu vực Đức Trọng, Lâm Đồng'),
        ('Chăm đàn bò trong một tuần', 'farm', 2000000, 'task',
         'Cho ăn, tiếp nước và vệ sinh khu vực theo hướng dẫn trong bảy ngày. Không thực hiện điều trị thú y; cần trao đổi lịch và kinh nghiệm.', ['feeding'], 'onsite', 'recurring', 'Khu vực Lâm Đồng'),
        ('Lắp hai kệ sách tại căn hộ', 'repair', 350000, 'task',
         'Lắp hai kệ theo hướng dẫn có sẵn; chủ có đủ bộ phụ kiện. Người làm mang dụng cụ, không khoan tường.', ['assembly'], 'onsite', 'once', 'Khu vực Tân Bình, TP.HCM'),
        ('Thay vòi nước bếp, chủ đã có vòi mới', 'repair', 250000, 'task',
         'Tháo vòi cũ, lắp vòi mới do chủ có và kiểm tra rò. Phụ kiện ngoài phạm vi cần thống nhất trước.', ['plumbing'], 'onsite', 'once', 'Khu vực Thanh Xuân, Hà Nội'),
        ('Gia sư Toán lớp 6 hai buổi mỗi tuần', 'tutoring', 180000, 'session',
         'Ôn nền tảng Toán lớp 6, một học viên, mỗi buổi 90 phút. Thứ Ba và thứ Năm 18:30–20:00.', ['math'], 'onsite', 'recurring', 'Khu vực Cầu Giấy, Hà Nội'),
        ('Luyện giao tiếp tiếng Anh trực tuyến', 'tutoring', 150000, 'session',
         'Người học mức cơ bản, tập hội thoại công việc; buổi 60 phút qua video, hai buổi mỗi tuần cần hẹn trước.', ['english'], 'remote', 'flexible', ''),
        ('Một landing page giới thiệu dịch vụ', 'digital', 2000000, 'task',
         'Một trang LadiPage năm phần, form gửi email, hai lượt chỉnh sửa. Khách cấp nội dung/logo; chưa gồm phí nền tảng và tên miền.', ['ladipage','design'], 'remote', 'deadline', ''),
        ('Dựng ba video ngắn cho cửa hàng', 'digital', 900000, 'task',
         'Ba video dọc 30–45 giây từ tư liệu khách cấp, thêm phụ đề, một lượt sửa. Không gồm quay phim.', ['video'], 'remote', 'deadline', ''),
        ('Xe kèm tài xế: TP.HCM đi Đà Lạt', 'driving', 1600000, 'trip',
         'Một chiều, bốn hành khách và bốn vali nhỏ; xe 7 chỗ kèm tài xế. Giá, giấy tờ và hành trình cần xác nhận; không phải chuyến đang điều phối.', ['driving'], 'onsite', 'once', 'Khu vực Thủ Đức, TP.HCM'),
        ('Ghé chăm hai mèo khi gia đình đi vắng', 'pets', 120000, 'day',
         'Hai lượt ghé mỗi ngày trong ba ngày: thay nước, cho ăn, dọn khay. Chủ chuẩn bị thức ăn và đồ dùng; không yêu cầu ở lại.', ['petcare'], 'onsite', 'recurring', 'Khu vực Bình Thạnh, TP.HCM'),
    ]
    service_jobs = [1, 2, 3, 4, 6, 8, 10, 12, 14, 15]
    service_titles = ['Dọn căn hộ theo giờ', 'Nấu cơm gia đình định kỳ', 'Bốc xếp hàng theo ca',
        'Chăm cây và thay chậu tại nhà', 'Phụ thu hoạch rau theo đợt', 'Lắp ráp kệ và nội thất nhỏ',
        'Gia sư Toán lớp 6', 'Thiết kế landing page LadiPage', 'Chở gia đình đi tỉnh, xe 7 chỗ',
        'Ghé chăm mèo tại nhà']
    service_descriptions = [
        'Tôi nhận lau sàn, vệ sinh bếp và nhà tắm trong căn hộ. Không nhận vệ sinh sau xây dựng. Khách chuẩn bị dụng cụ và hóa chất.',
        'Tôi nhận nấu ba món cho gia đình bốn người và dọn bếp sau nấu. Khách mua nguyên liệu. Không gồm giặt quần áo hay dọn toàn bộ nhà.',
        'Tôi nhận bốc xếp thùng 10–15kg từ xe vào kho tầng trệt, sử dụng xe đẩy của khách. Giá cho một người; cần thêm người phải hẹn riêng.',
        'Tôi nhận thay chậu, chăm cây nhỏ ở ban công, gom đất thừa tại chỗ. Khách có chậu và vật tư. Không nhận cây lớn hoặc mang phế thải đi.',
        'Tôi nhận thu hoạch và phân loại rau theo hướng dẫn, sáu giờ mỗi ngày, theo đợt. Cần thống nhất dụng cụ và chỗ nghỉ trước khi nhận.',
        'Tôi nhận lắp kệ sách và nội thất nhỏ theo hướng dẫn của bộ sản phẩm, có dụng cụ cầm tay. Khách chuẩn bị đủ phụ kiện; không khoan tường trong gói này.',
        'Tôi nhận ôn Toán lớp 6 cho một học viên, củng cố kiến thức nền và hướng dẫn tự học. Mỗi buổi 90 phút, hai buổi mỗi tuần.',
        'Tôi nhận làm một landing page LadiPage năm phần, có form gửi email và hai lượt chỉnh sửa. Khách cấp nội dung/logo; phí nền tảng và tên miền tính riêng.',
        'Tôi nhận xe 7 chỗ kèm tài xế cho bốn hành khách và bốn vali nhỏ. Một chiều hoặc khứ hồi báo giá riêng, cần chốt hành trình. Hồ sơ và giấy tờ là dữ liệu demo chưa xác minh.',
        'Tôi nhận ghé chăm hai mèo, hai lượt mỗi ngày: thay nước, cho ăn và dọn khay. Khách có thức ăn/đồ dùng. Không ở lại hoặc thực hiện điều trị thú y.',
    ]
    for i in range(6, 16):
        title, category, *_ = work[service_jobs[i - 6] - 1]
        u = user(i, 'Hồ sơ demo %02d · %s' % (i, env.ref('tacare_website.flex_category_' + category).name))
        demo_users.append(u)
        profile = profiles.search([('user_id', '=', u.id), ('flex_demo_key', '=', 'profile-%02d' % i)], limit=1)
        values = dict(user_id=u.id, name=u.name, headline='Nhận việc linh hoạt',
            care_recruitment_enabled=False, flex_demo_key='profile-%02d' % i, scope='private', visible=False)
        if profile:
            profile.write(values)
        else:
            profiles.create(values)

    for i, (title, category, rate, unit, description, skills, mode, schedule, location) in enumerate(work, 1):
        reg = lamdong if category == 'farm' else hanoi if i in (9,10) else hcm
        duration = 4 if unit == 'shift' else 6 if unit == 'day' else 1.5 if i == 10 else 1 if unit == 'session' else 3
        values = dict(flex_category_id=env.ref('tacare_website.flex_category_' + category).id,
            flex_mode=mode, flex_region_id=reg.id if mode != 'remote' else False,
            flex_location=location, flex_schedule=schedule, flex_date_from=today + timedelta(days=5),
            flex_date_to=(today + timedelta(days=7 if i==6 else 15)) if schedule != 'once' or i==6 else False, flex_weekdays='0,1,2,3,4' if schedule=='recurring' else False,
            flex_time_from='08:00', flex_time_to='12:00', flex_duration=duration,
            flex_rate_min=rate, flex_pay_unit=unit, flex_pay_basis='person' if unit in ('hour','shift','session','day','month') else 'package',
            flex_cost_note='Chỉ tiền công; các khoản khác theo mô tả. Giá giả lập.',
            flex_tools='client' if i in (1,2,3,4) else 'discuss',
            flex_skill_ids=[(6, 0, [env.ref('tacare_website.flex_skill_' + code).id for code in skills])],
            flex_experience='Thông tin giả lập, chưa xác minh.', flex_negotiable=True)
        if i in (1, 4, 8):
            values.update(flex_time_to='11:00', flex_duration=3)
        if i == 2:
            values.update(flex_time_from='16:00',flex_time_to='19:00',flex_duration=3,
                          flex_date_to=today + timedelta(days=35))
        if i == 5:
            values['flex_duration'] = 4
        if i == 6:
            values.update(flex_time_to='15:00', flex_schedule_note='Nghỉ trưa một giờ; sáu giờ làm mỗi ngày.')
        if i == 7:
            values.update(flex_date_to=today + timedelta(days=11), flex_weekdays='0,1,2,3,4,5,6',
                          flex_time_to='10:00', flex_duration=2,
                          flex_schedule_note='Mỗi ngày hai giờ trong bảy ngày liên tiếp; lịch cho ăn cần chốt với chủ.')
        if i == 9:
            values.update(flex_time_to='10:00', flex_duration=2)
        if i == 15:
            values.update(flex_date_to=today + timedelta(days=7), flex_weekdays='0,1,2,3,4,5,6',
                          flex_time_from=False, flex_time_to=False, flex_duration=1,
                          flex_schedule_note='Ba ngày liên tiếp, mỗi ngày hai lượt khoảng 30 phút; hẹn giờ với chủ.')
        if i == 10:
            values.update(flex_weekdays='1,3',flex_time_from='18:30',flex_time_to='20:00')
        if mode == 'remote':
            values.update(flex_time_from=False,flex_time_to=False)
            if schedule == 'deadline':
                values['flex_duration'] = 0
        if i == 14:
            values.update(flex_destination='Trung tâm Đà Lạt, Lâm Đồng', flex_trip_service='vehicle',
                flex_trip_direction='oneway', flex_passengers=4, flex_vehicle_note='Xe 7 chỗ; bốn vali nhỏ',
                flex_time_from='07:00',flex_time_to='15:00', flex_duration=8)
        owner = demo_users[(i - 1) % len(demo_users)]
        job_values = dict(values, name=title, company_id=env.company.id, website_id=site.id,
            tacare_owner_user_id=owner.id, tacare_owner_partner_id=owner.partner_id.id,
            care_opportunity_kind='flexible', flex_demo_key='flex-job-%02d' % i,
            tacare_status='published', is_published=True, tacare_type='task',
            tacare_mode='remote' if mode=='remote' else 'office', tacare_location=location,
            tacare_description_text=description, no_of_recruitment=2 if i==3 else 1,
            care_matching_enabled=False)
        job = jobs.search([('flex_demo_key', '=', job_values['flex_demo_key'])], limit=1)
        if job:
            job.write(job_values)
        else:
            job = jobs.create(job_values)
        assert not job._care_publish_errors(), (i, job._care_publish_errors())
        if i in service_jobs:
            profile = profiles.search([('user_id', '=', demo_users[service_jobs.index(i)+5].id), ('flex_demo_key', '=like', 'profile-%')], limit=1)
            service_index = service_jobs.index(i)
            cap_values = dict(values, profile_id=profile.id, title=service_titles[service_index],
                description=service_descriptions[service_index],
                currency_id=vnd.id, flex_state='available', flex_demo_key='flex-service-%02d' % i)
            # An offer is reusable availability, not a copy of the client's dated request.
            cap_values.update(flex_date_from=False, flex_date_to=False, flex_schedule='flexible',
                              flex_weekdays=False, flex_time_from=False, flex_time_to=False,
                              flex_schedule_note='Hẹn lịch cụ thể trước khi nhận việc.')
            if i in (2, 10):
                cap_values.update(flex_schedule='recurring', flex_weekdays=values['flex_weekdays'],
                                  flex_time_from=values['flex_time_from'], flex_time_to=values['flex_time_to'])
            if i == 1:
                cap_values.update(flex_min_hours=2, flex_rate_min=65000, flex_rate_max=80000)
            if i == 14:
                cap_values.update(flex_rate_min=1600000, flex_rate_max=2400000,
                                  flex_destination='TP.HCM đi Lâm Đồng; tuyến cụ thể cần xác nhận')
            cap = capabilities.search([('flex_demo_key', '=', cap_values['flex_demo_key'])], limit=1)
            cap.write(cap_values) if cap else capabilities.create(cap_values)

    demo_admin = user(99, 'Quản trị Demo TA.CARE', 'pending')
    demo_admin.write({'group_ids': [(4, env.ref('base.group_user').id), (4, env.ref('base.group_system').id)]})

    assert jobs.search_count([('flex_demo_key', '!=', False)]) == 20
    assert profiles.search_count([('flex_demo_key', '=like', 'profile-%')]) == 15
    assert capabilities.search_count([('flex_demo_key', '=like', 'flex-service-%')]) == 10
    env.cr.execute("SELECT id, login, password, active, tacare_account_role FROM res_users WHERE login NOT LIKE 'demo-flex-%' AND login NOT IN ('ungvien1@tacare.vn', 'ungvien2@tacare.vn') ORDER BY id")
    assert before == hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest(), 'Original accounts changed'
    credentials['accounts'] = list(by_login.values())
    credentials['original_accounts_fingerprint'] = before
    credentials['recruitment_job_ids'] = jobs.search([('flex_demo_key', '=like', 'recruitment-%')]).ids
    credentials['flex_job_ids'] = jobs.search([('flex_demo_key', '=like', 'flex-job-%')]).ids
    credentials['profile_ids'] = profiles.search([('flex_demo_key', '=like', 'profile-%')]).ids
    secret_path.write_text(json.dumps(credentials, ensure_ascii=False, indent=2))
    os.chmod(secret_path, 0o600)
    env.cr.commit()
    print('PASS local seed: 20 jobs = 5 recruitment + 15 flexible; 15 profiles; 10 work capabilities. Original accounts unchanged.')


seed(env)
