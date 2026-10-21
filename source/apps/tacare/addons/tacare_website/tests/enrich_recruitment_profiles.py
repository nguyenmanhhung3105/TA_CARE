"""Manual LOCAL fictional profile enrichment; no install hook, identity or consent edits."""
import hashlib
from odoo import fields


def enrich(env):
    assert env.cr.dbname == 'tacare_local'
    assert env['website'].sudo().search_count([('domain','ilike','.localhost')]) == 3
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users ORDER BY id')
    account_before = hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
    consents = env['care.consent'].sudo()
    consent_before = consents.search([]).read(['profile_id','purpose','state','field_scope','granted_by','valid_from','valid_until'])
    specs = [
        ('refresh-uv1-recruitment','Frontend Junior', 'junior', 10000000,14000000,
         'Tôi định hướng phát triển giao diện web cho sản phẩm giáo dục và dịch vụ. Điểm mạnh là chia nhỏ giao diện thành component dễ dùng lại, chuyển bản thiết kế thành HTML/CSS và kiểm tra trên điện thoại. Tôi quen làm việc bằng Git, viết ghi chú bàn giao và tiếp nhận phản hồi qua từng vòng review.\n\nTôi mong muốn được phụ trách một nhóm màn hình có phạm vi rõ, phối hợp với thiết kế và backend để hoàn thiện trạng thái tải, lỗi và dữ liệu trống. Các kinh nghiệm dưới đây đều là ví dụ hư cấu, chưa xác minh.',
         'Phát triển Frontend Junior trong 6–12 tháng tới; củng cố JavaScript, kiểm thử giao diện và khả năng diễn đạt quyết định thiết kế. Ưu tiên sản phẩm có người hướng dẫn và code review.',
         'Mẫu · Nhóm sản phẩm học tập An Phát', 'Cộng tác viên Frontend', '2025-10-01','2026-09-01',
         'Phát triển trang danh mục khóa học, màn hình đăng ký và phần theo dõi tiến độ từ bản thiết kế. Phối hợp nhóm 4 người, trao đổi dữ liệu API với backend, bổ sung trạng thái loading/empty/error. Kiểm tra bàn phím và bố cục ở các độ rộng điện thoại phổ biến.',
         'Trong bài thực hành, hoàn thành 8 màn hình responsive và bảng kiểm bàn giao; ghi nhận 12 tình huống lỗi giao diện để sửa theo review. Đây là kết quả mẫu, không phải số liệu đã kiểm chứng.',
         'JavaScript, HTML/CSS, Git, Figma, kiểm thử thủ công',
         'Mẫu · Chương trình Công nghệ phần mềm', 'Công nghệ phần mềm', '2021-09-01','2025-06-01', False,
         'Môn học tiêu biểu: cấu trúc dữ liệu, phát triển web và cơ sở dữ liệu. Đồ án mẫu xây dựng giao diện quản lý khóa học; trực tiếp thực hiện các component và viết tài liệu sử dụng. Văn bằng chưa được xác minh.'),
        ('refresh-uv2-recruitment','Content Marketing', 'junior', 10000000,15000000,
         'Tôi muốn phát triển nội dung giúp người đọc hiểu sản phẩm và ra quyết định có thông tin. Tôi có thể nghiên cứu chủ đề, lập lịch nội dung, viết bản nháp, biên tập theo giọng thương hiệu và phối hợp thiết kế. Tôi thường ghi lại mục tiêu, nhóm người đọc và nguồn tham khảo trước khi viết.\n\nTôi mong muốn làm việc với nhóm có brief rõ, quy trình duyệt và phản hồi định kỳ. Kinh nghiệm, dự án và số lượng bài viết trong hồ sơ là dữ liệu hư cấu để thử giao diện, chưa xác minh.',
         'Phụ trách một nhóm chủ đề cho website và mạng xã hội; cải thiện kỹ năng phỏng vấn người dùng, đo phản hồi và biên tập để nội dung rõ, nhất quán.',
         'Mẫu · Nhóm truyền thông Hướng Mới', 'Cộng tác viên nội dung', '2025-10-01','2026-09-01',
         'Xây dựng lịch nội dung bốn tuần theo ba nhóm người đọc; viết và biên tập nội dung website, bài mạng xã hội và hướng dẫn sử dụng. Phối hợp thiết kế theo brief, kiểm tra nguồn ảnh, ghi lại phản hồi và tổng hợp báo cáo nội dung mỗi tuần.',
         'Bài thực hành gồm 12 bài website, 20 bài mạng xã hội và bộ hướng dẫn giọng điệu ngắn. Trực tiếp viết/biên tập và quản lý checklist duyệt; không tự nhận số liệu tăng trưởng kinh doanh chưa có chứng cứ.',
         'Google Docs, bảng tính, lập lịch nội dung, biên tập, nghiên cứu từ khóa',
         'Mẫu · Chương trình Truyền thông ứng dụng', 'Truyền thông và nội dung số', '2021-09-01','2025-06-01', False,
         'Nội dung học: nghiên cứu người đọc, viết nội dung, truyền thông số và đánh giá nguồn. Đồ án nhóm xây dựng bộ nội dung giới thiệu một dịch vụ hư cấu; phụ trách lịch và biên tập. Chưa xác minh văn bằng.'),
        ('refresh-student-recruitment','Thực tập Frontend', 'intern', 4000000,6000000,
         'Tôi đang học theo hướng phát triển web và tìm cơ hội thực tập Frontend có người hướng dẫn. Tôi đã thực hành bố cục HTML/CSS, JavaScript cơ bản và quản lý mã bằng Git. Trong bài tập nhóm, tôi thường phụ trách giao diện biểu mẫu, kiểm tra lỗi nhập và hỗ trợ trình bày kết quả.\n\nTôi có thể đọc hướng dẫn tiếng Anh cơ bản, ghi lại điều chưa rõ và cập nhật tiến độ đều đặn. Thông tin học tập, nhóm và kết quả trong hồ sơ là hư cấu để thử sản phẩm, không phải kinh nghiệm đã xác minh.',
         'Tìm chương trình thực tập có bài tập rõ, review hằng tuần và cơ hội làm một phần nhỏ của sản phẩm thật. Sau thực tập, tự xử lý được một giao diện đơn giản từ thiết kế đến bàn giao.',
         'Mẫu · Nhóm đồ án Sinh viên Web', 'Thành viên phụ trách giao diện', '2026-02-01','2026-07-01',
         'Thực hiện trang giới thiệu, biểu mẫu đăng ký và danh sách hoạt động cho đồ án nhóm 3 người. Viết HTML/CSS, bổ sung kiểm tra dữ liệu đầu vào bằng JavaScript và thử bố cục trên điện thoại. Nhận phản hồi từ bạn cùng nhóm và ghi nhật ký thay đổi.',
         'Hoàn thành 4 trang trong đồ án, checklist 10 tình huống kiểm thử và hướng dẫn chạy dự án. Không có kinh nghiệm làm việc thương mại được xác minh; số tháng liên quan là tự khai cho bài thực hành.',
         'HTML/CSS, JavaScript cơ bản, Git, Figma cơ bản',
         'Mẫu · Chương trình Kỹ thuật phần mềm đang học', 'Kỹ thuật phần mềm', '2023-09-01',False, True,
         'Đang học lập trình web, cấu trúc dữ liệu và kiểm thử cơ bản. Có thể sắp xếp lịch thực tập theo lịch học và thỏa thuận với người hướng dẫn; không nhận lịch trùng môn học bắt buộc.'),
    ]
    for key,headline,level,low,high,bio,goal,org,position,start,end,tasks,result,tools,school,major,school_start,school_end,current,school_notes in specs:
        profile = env['tacare.profile'].sudo().search([('flex_demo_key','=',key)],limit=1)
        assert profile and profile.care_recruitment_enabled and profile.user_id.active
        assert profile.user_id.login.split('@')[0] in ('ungvien1','ungvien2','student.test')
        profile.write({'headline':headline,'bio':'HỒ SƠ MẪU HƯ CẤU.\n\n'+bio,'goal':goal,
            'career_level':level, 'salary_min':low,'salary_max':high,'salary_currency_id':env.ref('base.VND').id,
            'salary_period':'month','salary_tax':'gross','salary_negotiable':True,'relocation':'discuss',
            'preferred_conditions':'Trao đổi trước về lịch làm, phạm vi nhiệm vụ, người hướng dẫn và cách đánh giá kết quả. Mong muốn phản hồi định kỳ; các điều kiện cụ thể cần hai bên xác nhận.',
            'availability':'Thứ Hai–thứ Sáu theo lịch thống nhất; có thể trao đổi trực tuyến trước khi nhận việc.',
            'work_history':'Tổng quan kinh nghiệm tự khai; chi tiết vai trò, thời gian và kết quả ở từng mục bên dưới. Không cộng trùng thời gian của các dự án song song.',
            'education':'Chương trình đào tạo mẫu, chưa xác minh văn bằng',
            'education_details':school + ' · ' + major + '. Thông tin hoàn toàn hư cấu để thử biểu mẫu.',
            'languages':'Tiếng Việt: sử dụng hằng ngày. Tiếng Anh: đọc hướng dẫn và trao đổi cơ bản (tự khai; chưa có chứng chỉ được xác minh).',
            'licenses':'Chưa cung cấp giấy phép hoặc chứng chỉ đã xác minh. Có thể bổ sung tên, đơn vị cấp và thời hạn khi có tài liệu phù hợp.'})
        work = env['tacare.profile.experience'].sudo().search([('profile_id','=',profile.id),('organization','=',org)],limit=1)
        values={'profile_id':profile.id,'organization':org,'position':position,'start_date':start,'end_date':end,
            'employment_type':'project' if level=='intern' else 'freelance','location':'TP. Hồ Chí Minh / làm việc nhóm trực tuyến',
            'responsibilities':tasks,'achievements':result,'tools':tools}
        work.write(values) if work else env['tacare.profile.experience'].sudo().create(values)
        education = env['tacare.profile.education'].sudo().search([('profile_id','=',profile.id),('school','=',school)],limit=1)
        values={'profile_id':profile.id,'school':school,'major':major,'start_date':school_start,'end_date':school_end,
            'is_current':current,'description':school_notes}
        education.write(values) if education else env['tacare.profile.education'].sudo().create(values)
        if not profile.evidence_ids.filtered(lambda e:e.title == 'Mẫu · Dự án thực hành ' + headline):
            env['tacare.profile.evidence'].sudo().create({'profile_id':profile.id,'title':'Mẫu · Dự án thực hành '+headline,
                'role':position,'description':tasks,'result':'Có bản bàn giao và checklist thực hành. Dữ liệu hư cấu, chưa xác minh.',
                'status':'unverified','visibility':'private'})
        for skill in profile.skill_ids:
            if not skill.use or 'thực hành' in skill.use:
                skill.write({'use':'Đã dùng trong đầu việc mẫu của hồ sơ: ' + tasks[:190]})
    env.cr.execute('SELECT id, login, password, active, tacare_account_role FROM res_users ORDER BY id')
    assert account_before == hashlib.sha256(repr(env.cr.fetchall()).encode()).hexdigest()
    assert consent_before == consents.search([]).read(['profile_id','purpose','state','field_scope','granted_by','valid_from','valid_until'])
    env.cr.commit()
    print('PASS enriched three fictional recruitment profiles with structured experience, education and project evidence; accounts/consents unchanged')


enrich(env)
