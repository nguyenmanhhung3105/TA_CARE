"""Manual LOCAL data refresh approved 21 October. Never an installation hook.

Run only after a backup. Real accounts/credentials/admin profiles/consents remain
unchanged. Rehomes sample offers, removes only old profile-01..15 demo shells.
"""
import hashlib
from datetime import timedelta
from odoo import fields
from markupsafe import escape


def refresh(env):
    assert env.cr.dbname == 'tacare_local'
    assert env['website'].sudo().search_count([('domain', 'ilike', '.localhost')]) == 3
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users ORDER BY id')
    before = hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
    users = env['res.users'].sudo()
    profiles = env['tacare.profile'].sudo()
    caps = env['care.profile.capability'].sudo()
    today = fields.Date.today()
    hcm = env['res.country.state'].search([('country_id.code', '=', 'VN'), ('name', 'ilike', 'Hồ Chí Minh')], limit=1)
    owner_users = []
    flex_profiles = []
    for prefix, key, title in [('ungvien1', 'refresh-uv1-flexible', 'Nhận chăm cây cuối tuần'),
                              ('ungvien2', 'refresh-uv2-flexible', 'Dọn nhà theo giờ'),
                              ('student.test', 'refresh-student-flexible', 'Việc làm thêm và dịch vụ số')]:
        user = users.search(['|', ('login', '=', prefix), ('login', '=like', prefix + '@%')], limit=1)
        assert user and user.active and user.tacare_account_role == 'candidate'
        owner_users.append(user)
        profile = profiles.search([('user_id', '=', user.id), ('flex_demo_key', '=', key)], limit=1)
        if not profile:
            profile = profiles.create({'user_id': user.id, 'name': user.name,
                'profile_title': title, 'flex_demo_key': key, 'care_recruitment_enabled': False,
                'scope': 'private', 'visible': False})
        flex_profiles.append(profile)
    # Preserve useful offers, explicitly attach them to an actual account profile.
    mapping = {'garden': 0, 'farm': 0, 'repair': 0, 'cleaning': 1, 'cooking': 1, 'loading': 1,
               'pets': 1, 'digital': 2, 'tutoring': 2, 'driving': 0}
    for cap in caps.search([('flex_demo_key', '=like', 'flex-service-%')]):
        cap.write({'profile_id': flex_profiles[mapping[cap.category_id.code]].id})
    old = profiles.search([('flex_demo_key', 'in', ['profile-%02d' % n for n in range(1, 16)])])
    assert all(p.user_id.login.startswith('demo-flex-') for p in old)
    assert not env['tacare.connection'].sudo().search_count([('profile_id', 'in', old.ids)])
    assert not env['care.match.input'].sudo().search_count([('profile_id', 'in', old.ids)])
    removed = len(old)
    old.unlink()
    # Add a recruitment profile for the existing student account, without changing it.
    student = owner_users[2]
    key = 'refresh-student-recruitment'
    student_profile = profiles.search([('user_id', '=', student.id), ('flex_demo_key', '=', key)], limit=1)
    if not student_profile:
        student_profile = profiles.create({'user_id': student.id, 'name': student.name,
            'profile_title': 'Thực tập Frontend và thiết kế giao diện', 'headline': 'Thực tập Frontend',
            'care_recruitment_enabled': True, 'flex_demo_key': key, 'scope': 'private', 'visible': False})
    for p in profiles.search([('user_id', 'in', [u.id for u in owner_users]), ('flex_demo_key', '=like', 'refresh-%')]):
        data = {'bio': 'HỒ SƠ MẪU HƯ CẤU. ' + (p.bio or p.profile_title or '') if not (p.bio or '').startswith('HỒ SƠ MẪU') else p.bio,
            'work_history': 'Mẫu thực hành 2025–2026: làm theo yêu cầu, ghi lại phạm vi và thời gian; kiểm tra đầu ra với người hướng dẫn. Các kinh nghiệm này là dữ liệu minh họa, chưa xác minh.',
            'education_details': 'Dữ liệu minh họa: chương trình học và tự học theo định hướng công việc; chưa xác minh văn bằng.',
            'languages': 'Tiếng Việt; tiếng Anh đọc hướng dẫn cơ bản (tự khai trong mẫu).',
            'licenses': 'Chưa cung cấp chứng chỉ hoặc giấy phép đã xác minh.',
            'goal': 'Thống nhất đầu việc, lịch, thu nhập và tiêu chí nghiệm thu trước khi bắt đầu.',
            'availability': 'Có thể trao đổi lịch trước 24 giờ; không nhận công việc ngoài phạm vi đã thống nhất.',
            'location': 'TP. Hồ Chí Minh', 'region_id': hcm.id}
        if p.care_recruitment_enabled:
            frontend = p.user_id != owner_users[1]
            position = env.ref('tacare_website.position_' + ('it_frontend' if frontend else 'marketing_content'))
            data.update(desired_position_id=position.id, sector=position.sector_id.code,
                mode='hybrid', desired_type='internship' if p == student_profile else 'employment', work_fraction='full',
                experience_known=True, relevant_months=6 if p == student_profile else 12,
                salary_min=4000000 if p == student_profile else 10000000,
                salary_currency_id=env.ref('base.VND').id, salary_period='month', salary_tax='gross',
                start_date=today + timedelta(days=7), travel='no')
            skill_names = ['JavaScript', 'CSS', 'HTML / CSS', 'Figma'] if frontend else ['Viết nội dung', 'Biên tập', 'Lập kế hoạch nội dung']
            for name in skill_names:
                if not p.skill_ids.filtered(lambda s: s.name == name):
                    env['tacare.profile.skill'].sudo().create({'profile_id': p.id, 'name': name, 'level': 'good',
                        'use': 'Dùng trong bài thực hành; kỹ năng tự khai, chưa xác minh.', 'years_experience': 0.5})
        p.write(data)
    publisher = users.search(['|', ('login', '=', 'hr.hozota'), ('login', '=like', 'hr.hozota@%')], limit=1)
    assert publisher and publisher.tacare_account_role == 'business'
    jobs = env['hr.job'].sudo().search([('flex_demo_key', '!=', False)])
    extra = {
        'cleaning': ('Kiểm tra hiện trạng trước khi làm, lau từ khu khô đến khu ướt, phân loại rác theo thùng chủ nhà chuẩn bị.', 'Sàn, mặt bếp và thiết bị vệ sinh sạch; không lau mặt ngoài cửa sổ cao hoặc di chuyển đồ nặng.', 'Khăn, chổi, cây lau, găng tay; chủ nhà cung cấp hóa chất phù hợp bề mặt.'),
        'cooking': ('Thống nhất thực đơn và dị ứng trước mỗi tuần; sơ chế, nấu ba món, chia phần và vệ sinh khu nấu.', 'Bữa ăn bàn giao đúng giờ, nguyên liệu còn lại được bảo quản theo hướng dẫn của chủ.', 'Nồi, bếp, hộp đựng và nguyên liệu của chủ; không tự mua thêm khi chưa thống nhất.'),
        'loading': ('Kiểm đếm 40 thùng trước và sau khi chuyển; dùng xe đẩy, đặt hàng theo sơ đồ kho, báo ngay thùng rách.', 'Đủ 40 thùng tại vị trí quy định; không gồm vận chuyển bằng xe hoặc nâng kiện quá 15kg/người.', 'Xe đẩy và lối đi thông thoáng do chủ kho chuẩn bị; người làm mang giày kín.'),
        'garden': ('Kiểm tra từng chậu và cây; thay chậu hoặc cắt cỏ theo danh sách; gom lá và đất thừa về vị trí thống nhất.', 'Cây/chậu đặt ổn định, khu làm việc được dọn; không cắt cây lớn, leo cao hoặc dùng thuốc khi chưa thống nhất.', 'Găng tay, kéo, xẻng nhỏ; chậu/đất hoặc máy cắt cần chốt riêng theo tin.'),
        'farm': ('Nhận hướng dẫn tại khu làm việc; chia lô và thực hiện đúng từng bước; ghi khối lượng cuối ca và báo bất thường.', 'Bàn giao khối lượng đã làm mỗi ngày; không vận hành máy lớn, dùng hóa chất hay thực hiện điều trị thú y.', 'Dụng cụ tại chỗ, nước uống và khu nghỉ do bên thuê chuẩn bị; mang đồ bảo hộ phù hợp.'),
        'repair': ('Kiểm kê phụ kiện, kiểm tra kích thước và hiện trạng; lắp đặt theo hướng dẫn; thử độ chắc hoặc thử nước trước bàn giao.', 'Thiết bị hoạt động trong phạm vi sửa/lắp; không sửa điện, thay đường ống âm tường hay phát sinh vật tư ngoài báo giá.', 'Dụng cụ cầm tay do người làm mang; chủ có sẵn bộ phụ kiện hoặc thiết bị thay mới.'),
        'tutoring': ('Buổi đầu trao đổi mục tiêu và kiểm tra nền tảng; mỗi buổi gồm ôn bài, thực hành và ghi việc cần tự luyện.', 'Gửi nội dung đã học và bài tập sau buổi; không cam kết điểm số hoặc thi hộ.', 'Tài liệu phù hợp trình độ; lớp online cần mạng, tai nghe và thiết bị của mỗi bên.'),
        'digital': ('Chốt brief và tư liệu đầu vào; gửi bản nháp, tiếp nhận phản hồi theo số vòng trong mô tả; bàn giao bản xuất và hướng dẫn.', 'Sản phẩm đúng kích thước, nội dung và số lượng đã duyệt; phí tên miền, nền tảng và tài nguyên có bản quyền tính riêng.', 'Máy tính và phần mềm hợp pháp của người làm; bên thuê cấp logo, nội dung, tư liệu được phép sử dụng.'),
        'pets': ('Chủ bàn giao hướng dẫn cho ăn, vị trí đồ dùng và cách vào nhà; mỗi lượt thay nước, cho ăn, dọn khay và ghi nhật ký.', 'Hai lượt ghé/ngày theo lịch đã chốt, gửi cập nhật sau lượt; không ở lại hoặc thực hiện điều trị thú y.', 'Chủ chuẩn bị thức ăn, cát, túi rác và đầu mối liên lạc khi có tình huống bất thường.'),
        'driving': ('Chỉ là ví dụ khảo sát biểu mẫu chuyến đi; thời gian và giá phải trao đổi lại.', 'Không mở nhận chuyến, điều phối hoặc vận hành vận tải hành khách trong demo.', 'Thông tin xe và giấy tờ đều chưa xác minh.'),
    }
    for job in jobs:
        vals = {'tacare_owner_user_id': publisher.id, 'tacare_owner_partner_id': publisher.partner_id.commercial_partner_id.id,
                'care_matching_enabled': job.flex_category_id.code != 'driving', 'tacare_deadline': today + timedelta(days=45)}
        if job.care_opportunity_kind == 'flexible':
            steps, output, tools = extra[job.flex_category_id.code]
            base = (job.tacare_description_text or '').split('\n\nQuy trình thực hiện:')[0]
            vals.update(tacare_description_text=base + '\n\nQuy trình thực hiện:\n' + steps + '\n\nBàn giao và giới hạn:\n' + output + '\n\nTrao đổi trước khi làm: xác nhận lịch, địa chỉ cụ thể, phạm vi, phụ phí và cách nghiệm thu. Mọi thông tin là giả lập.',
                flex_tools_note=tools, flex_experience='Có thể giải thích cách làm, từng bước kiểm tra chất lượng và giới hạn an toàn. Kinh nghiệm là tự khai; không yêu cầu xuất trình giấy tờ cá nhân công khai.',
                flex_cost_note='Giá mẫu chỉ gồm phạm vi mô tả; vật tư và phát sinh phải được hai bên thống nhất trước. Không thu phí qua hệ thống.')
        else:
            tasks = {'it': 'Xây dựng component bằng JavaScript/CSS; kết nối API theo tài liệu; kiểm thử bàn phím và điện thoại; sửa lỗi qua code review.',
                'ecommerce': 'Kiểm tra gian hàng đầu ngày; cập nhật danh mục; theo dõi đơn và tồn; phối hợp xử lý hoàn/đổi; lập báo cáo Excel mỗi tuần.',
                'marketing': 'Nghiên cứu người đọc; lên lịch bốn tuần; viết và biên tập bài; phối hợp thiết kế; theo dõi phản hồi để cải thiện nội dung.',
                'logistics': 'Kiểm nhận hàng theo phiếu; theo dõi xuất nhập tồn; sắp xếp vị trí; kiểm kê định kỳ; ghi nhận sai lệch với người phụ trách.',
                'design': 'Đọc brief; xây dựng phương án bố cục; thiết kế ấn phẩm số bằng Figma; kiểm tra font và quyền tài nguyên; bàn giao file đúng chuẩn.'}[job.tacare_sector]
            vals.update(tacare_description_text='TIN TUYỂN DỤNG MẪU HƯ CẤU.\n\nCông việc hằng ngày:\n' + tasks + '\n\nPhối hợp: báo cáo đầu tuần, rà soát kết quả cuối tuần và thống nhất ưu tiên với người phụ trách. Tháng đầu làm quen quy trình, tháng hai tự xử lý đầu việc có phản hồi.',
                care_candidate_requirements='Trình bày được một bài thực hành liên quan; giải thích vai trò và kết quả của bản thân; giao tiếp rõ, đúng hẹn và tiếp nhận phản hồi. Minh chứng có thể được bổ sung khi trao đổi; thiếu dữ liệu chưa được xem là không đạt.',
                care_benefits='Lương cố định theo khoảng công bố, trước thuế; trả theo tháng. Mẫu mô tả: có hướng dẫn ban đầu, thiết bị phù hợp, phản hồi định kỳ và lịch nghỉ được trao đổi trong thư mời. Không coi đây là cam kết của doanh nghiệp thực tế.',
                tacare_schedule='Thứ Hai–thứ Sáu, 08:30–17:30, nghỉ trưa 12:00–13:00; lịch từ xa theo thỏa thuận với quản lý.',
                tacare_outcome='Hoàn thành đầu việc theo brief, đúng lịch đã chốt; có bản bàn giao và danh sách các điểm cần tiếp tục.',
                care_salary_tax='gross', care_salary_basis='base')
        vals['description'] = vals['website_description'] = '<p>%s</p>' % escape(vals['tacare_description_text'])
        job.write(vals)
    for cap in caps.search([('profile_id', 'in', [p.id for p in flex_profiles])]):
        steps, output, tools = extra[cap.category_id.code]
        base = (cap.description or '').split('\n\nCách nhận việc:')[0]
        cap.write({'description': base + '\n\nCách nhận việc:\n' + steps + '\n\nBàn giao và giới hạn:\n' + output,
                   'flex_tools_note': tools, 'flex_experience': 'Mẫu tự khai: có thể mô tả quy trình và báo phát sinh trước khi làm; chưa xác minh tay nghề.',
                   'flex_state': 'paused' if cap.category_id.code == 'driving' else cap.flex_state})
    assert len(jobs) == 20 and all(not j._care_publish_errors() for j in jobs)
    assert all(p.user_id.active and not p.user_id.login.startswith('demo-flex-') for p in profiles.search([]))
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users ORDER BY id')
    assert before == hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest(), 'Account state changed'
    env.cr.commit()
    print('PASS local refresh: removed %s old demo profiles; 20 detailed jobs; %s account-owned profiles; accounts and consents unchanged.' % (removed, profiles.search_count([])))


refresh(env)
