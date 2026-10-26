"""Owner-authorized, manual local account rename and multi-profile map trial.

No install hook. Existing users, owners, needs, profiles and consents are kept.
Passwords are generated at runtime and written only to an ignored private file.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.addons.tacare_website.geo_utils import approximate, distance_km

PREFIX = 'map-owner-20261027-'
# Groups reflect the public professions already owned by these exact accounts.
ACCOUNTS = (
    ('home', 'nhaviet.demo@khovieclam.vn', 'nhacua-thucung@khovieclam.vn',
     'Cần người · Dọn dẹp / Nấu ăn / Thú cưng', 'business'),
    ('green', 'vuonxanh.demo@khovieclam.vn', 'vuon-nongtrai@khovieclam.vn',
     'Cần người · Làm vườn / Nông trại', 'business'),
    ('manual', 'tienich.demo@khovieclam.vn', 'suachua-bocxep@khovieclam.vn',
     'Cần người · Sửa chữa / Bốc xếp', 'business'),
    ('digital', 'sangtao.demo@khovieclam.vn', 'noidungso@khovieclam.vn',
     'Cần người · Nội dung số', 'business'),
    ('learning', 'hoctot.demo@khovieclam.vn', 'giasu@khovieclam.vn',
     'Cần người · Gia sư', 'business'),
    ('provider_home', 'ungvien1@tuhoso.com', 'dondep-vuon-giasu@tuhoso.com',
     'Nhận việc · Dọn dẹp / Làm vườn / Gia sư', 'candidate'),
    ('provider_green', 'ungvien2@tuhoso.com', 'nauan-nongtrai-noidungso@tuhoso.com',
     'Nhận việc · Nấu ăn / Nông trại / Nội dung số', 'candidate'),
    ('provider_manual', 'student.test@tuhoso.com', 'bocxep-suachua-thucung@tuhoso.com',
     'Nhận việc · Bốc xếp / Sửa chữa / Thú cưng', 'candidate'),
)
PROVIDERS = {'cleaning':'provider_home', 'garden':'provider_home', 'tutoring':'provider_home',
             'cooking':'provider_green', 'farm':'provider_green', 'digital':'provider_green',
             'loading':'provider_manual', 'repair':'provider_manual', 'pets':'provider_manual'}
# Independently authored service scope/prices; no skill, date or pay claims are
# copied from a source job. Each profile has one explicit, owner-linked offer.
SERVICES = {
    'cleaning': ('hour', 'person', 0, (45000,50000,55000), (
        ('Nhận dọn căn hộ và vệ sinh bếp', 'Lau sàn, làm sạch mặt bếp và dọn khu vệ sinh. Thống nhất diện tích, chất tẩy và phần cần tránh trước khi làm.'),
        ('Nhận lau kính thấp và dọn ban công', 'Lau cửa kính trong tầm với, quét ban công và gom rác gọn. Không nhận làm ở vị trí trên cao hoặc cần thiết bị bảo hộ chuyên dụng.'),
        ('Nhận dọn phòng sau khi chuyển đồ', 'Quét bụi, lau tủ trống và sàn sau khi đồ đạc đã được chuyển ra. Trao đổi riêng khi có phế thải hoặc vết bẩn cần xử lý chuyên dụng.'))),
    'cooking': ('month', 'person', 0, (4250000,4500000,4750000), (
        ('Nhận nấu cơm gia đình theo tuần', 'Chuẩn bị bữa cơm gia đình và dọn gọn khu nấu. Thực đơn, số người ăn và nguyên liệu được chốt trước mỗi tuần.'),
        ('Nhận sơ chế và chuẩn bị bữa trưa', 'Rửa, chia phần nguyên liệu và nấu bữa trưa theo thực đơn đã thống nhất. Gia đình chuẩn bị bếp và dụng cụ phù hợp.'),
        ('Nhận nấu món chay gia đình', 'Chuẩn bị món chay đơn giản và chia phần cho gia đình. Cần trao đổi thành phần không dùng, khẩu vị và chi phí nguyên liệu trước.'))),
    'garden': ('task', 'package', 0, (240000,260000,280000), (
        ('Nhận chăm cây ban công', 'Kiểm tra đất, tưới cây và tỉa lá khô trong ban công nhỏ. Chậu nặng, thay đất nhiều hoặc xử lý sâu bệnh cần trao đổi riêng.'),
        ('Nhận thay đất và sắp xếp chậu cây', 'Trộn đất đã chuẩn bị, thay đất chậu nhỏ và sắp xếp cây gọn theo khu vực. Chủ nhà thống nhất số chậu và chuẩn bị vật tư.'),
        ('Nhận làm cỏ và dọn vườn nhỏ', 'Nhổ cỏ nhẹ, gom lá và dọn lối đi vườn. Không nhận cắt cây lớn hoặc sử dụng hóa chất khi chưa thống nhất.'))),
    'farm': ('day', 'person', 8, (220000,240000,260000), (
        ('Nhận thu hoạch và phân loại nông sản', 'Hỗ trợ thu hái trong tầm với, phân loại và xếp vào giỏ theo hướng dẫn. Cần trao đổi loại cây, sản lượng và điều kiện làm việc.'),
        ('Nhận đóng gói nông sản tại vườn', 'Nhặt, cân và đóng gói nông sản theo quy cách đã thống nhất. Chủ vườn chuẩn bị khu thao tác và bao bì.'),
        ('Nhận chăm luống và dọn khu trồng', 'Làm cỏ nhẹ, dọn luống và tưới theo hướng dẫn tại vườn. Không tự sử dụng máy hoặc thuốc bảo vệ thực vật.'))),
    'loading': ('shift', 'person', 3, (120000,130000,140000), (
        ('Nhận xếp hàng nhẹ trong kho', 'Phân loại thùng nhẹ và xếp đúng vị trí được chỉ dẫn. Cần chốt trọng lượng, số lượng và chiều cao xếp trước ca.'),
        ('Nhận hỗ trợ chuyển đồ trong nhà', 'Bọc đồ nhỏ, chuyển giữa các phòng và sắp xếp theo hướng dẫn. Đồ dễ vỡ, cầu thang hoặc đồ nặng cần khảo sát trước.'),
        ('Nhận đóng thùng và kiểm đếm hàng', 'Đóng thùng, dán nhãn và kiểm đếm theo danh sách bàn giao. Bên cần người chuẩn bị vật tư và hướng dẫn quy cách.'))),
    'repair': ('task', 'package', 0, (280000,300000,320000), (
        ('Nhận kiểm tra vòi nước và rò rỉ nhỏ', 'Kiểm tra điểm rò, thay gioăng hoặc phụ kiện đơn giản sau khi thống nhất. Linh kiện tính riêng; không tự tháo hệ thống âm tường.'),
        ('Nhận lắp kệ và phụ kiện gia đình', 'Lắp kệ nhỏ, bắt vít và căn chỉnh phụ kiện trong phạm vi đã trao đổi. Cần kiểm tra loại tường, tải trọng và vị trí đường điện nước.'),
        ('Nhận chỉnh cửa và đồ gỗ nhỏ', 'Kiểm tra bản lề, tay nắm và căn chỉnh cánh cửa hoặc tủ nhỏ. Hạng mục thay thế lớn cần báo lại trước khi thực hiện.'))),
    'tutoring': ('session', 'person', 1.5, (150000,160000,170000), (
        ('Nhận hỗ trợ học Toán theo buổi', 'Cùng ôn kiến thức cơ bản và hướng dẫn cách giải bài tập. Trao đổi lớp học, phần cần củng cố và mục tiêu trước buổi đầu.'),
        ('Nhận kèm bài tập và rèn nếp tự học', 'Hỗ trợ đọc đề, lập kế hoạch làm bài và kiểm tra lại kết quả. Không làm bài thay; cần thống nhất nội dung với gia đình.'),
        ('Nhận ôn chuyên đề Toán cơ bản', 'Ôn từng chuyên đề nhỏ, chuẩn bị bài luyện tập vừa sức và ghi lại nội dung cần ôn thêm. Lịch học được hẹn riêng.'))),
    'digital': ('task', 'package', 0, (650000,750000,850000), (
        ('Nhận viết nội dung giới thiệu sản phẩm', 'Soạn nội dung ngắn từ thông tin sản phẩm được cung cấp. Thống nhất số bài, độ dài và số lần chỉnh sửa trước khi bắt đầu.'),
        ('Nhận sắp xếp nội dung trang bán hàng', 'Biên tập tiêu đề, mô tả và mục hỏi đáp từ dữ liệu được duyệt. Không tự đưa cam kết sản phẩm khi chưa có thông tin xác nhận.'),
        ('Nhận chuẩn bị bài đăng mạng xã hội', 'Lên dàn ý và viết một nhóm bài đăng theo chủ đề thống nhất. Hình ảnh do bên đặt việc cung cấp hoặc chốt quyền sử dụng riêng.'))),
    'pets': ('day', 'person', 1, (90000,100000,110000), (
        ('Nhận ghé chăm mèo tại nhà', 'Thay nước, chia thức ăn theo hướng dẫn và dọn khay vệ sinh. Cần trao đổi thói quen, cách vào nhà và đầu mối liên hệ khi có việc phát sinh.'),
        ('Nhận cho thú cưng ăn và dọn khu ở', 'Ghé cho ăn đúng khẩu phần và dọn khu vực sinh hoạt đã thống nhất. Không tự dùng thuốc hoặc đổi loại thức ăn.'),
        ('Nhận kiểm tra thú cưng khi chủ đi vắng', 'Ghé kiểm tra nước, thức ăn và ghi lại tình trạng theo yêu cầu. Cần xác nhận phạm vi theo dõi, số lượt ghé và tình huống cần báo chủ.'))),
}


def account(env, key):
    row = next(r for r in ACCOUNTS if r[0] == key)
    found = env['res.users'].sudo().search([('login','in',row[1:3])])
    if len(found) != 1 or not found.active or found.tacare_account_role != row[4] or found.has_group('base.group_system'):
        raise ValidationError('Tài khoản thử không đúng danh sách/role: ' + key)
    return found


def _fingerprint(records, names):
    # Compare stored relational IDs, not display names changed by account renaming.
    return hashlib.sha256(json.dumps(records.read(names, load=None), sort_keys=True, default=str).encode()).hexdigest()


def _new_secret(login):
    return 'TC!' + login.split('@')[0].split('-')[0].capitalize() + secrets.token_urlsafe(6)


def prepare(env, apply=False, credential_dir=None):
    if env.cr.dbname != 'tacare_local':
        raise ValidationError('Chỉ được thực hiện trên tacare_local.')
    sites = env['website'].sudo().search([('care_site_kind','in',['tacare','khovieclam','tuhoso'])])
    if len(sites) != 3 or any('.localhost' not in (w.domain or '') for w in sites):
        raise ValidationError('Chỉ dùng bộ ba website localhost.')
    users = {r[0]:account(env,r[0]) for r in ACCOUNTS}
    jobs = env['hr.job'].sudo().search([('tacare_owner_user_id','in',[u.id for u in users.values()]),
        ('care_opportunity_kind','=','flexible'),('tacare_status','=','published'),('is_published','=',True),
        ('care_matching_enabled','=',True),('care_remaining_slots','>',0)], order='id')
    bases = {code:jobs.filtered(lambda j:j.flex_category_id.code == code)[:1] for code in SERVICES}
    if any(not j for j in bases.values()):
        raise ValidationError('Thiếu tin nguồn đang mở cho một nhóm nghề.')
    if any(not j.geo_set for c,j in bases.items() if c != 'digital'):
        raise ValidationError('Tin nguồn bản đồ chưa có điểm.')
    existing = env['tacare.profile'].sudo().search([('flex_demo_key','=like',PREFIX+'%')])
    plan = dict(accounts=len(users), additional_profiles=27-len(existing), map_profiles=24, remote_profiles=3)
    if not apply:
        return plan
    directory = Path(credential_dir or '')
    if not directory.is_absolute() or not str(directory).startswith('/var/lib/odoo/'):
        raise ValidationError('Thông tin đăng nhập phải lưu trong runtime local riêng tư.')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = directory/'map_test_accounts_20261027.json'
    if path.exists() or existing:
        raise ValidationError('Đợt dữ liệu này đã có; không tự xoay mật khẩu hoặc tạo lặp.')
    if any(users[r[0]].login != r[1] for r in ACCOUNTS):
        raise ValidationError('Tài khoản đã được đổi ở nơi khác; cần kiểm tra trước khi chạy.')
    selected = [u.id for u in users.values()]
    env.cr.execute('SELECT id,login,password,active FROM res_users WHERE NOT (id = ANY(%s)) ORDER BY id',[selected])
    untouched_accounts = env.cr.fetchall()
    originals = env['tacare.profile'].sudo().search([])
    offers = env['care.profile.capability'].sudo().with_context(active_test=False).search([])
    grants = env['care.consent'].sudo().search([])
    old_profile_fields = ['user_id','name','profile_title','scope','visible','version','write_date']
    old_offer_fields = ['profile_id','title','description','geo_lat','geo_lon','geo_share','geo_sample','write_date']
    old_grant_fields = ['profile_id','purpose','recipient_kind','recipient_partner_id','field_scope','state','valid_until','write_date']
    before = (_fingerprint(originals,old_profile_fields), _fingerprint(offers,old_offer_fields), _fingerprint(grants,old_grant_fields))
    partner_count = env['res.partner'].sudo().with_context(active_test=False).search_count([])
    mail_count = env['mail.mail'].sudo().search_count([])
    account_shape = {k:(u.id,u.partner_id.id,u.tacare_account_role,u.company_ids.ids,u.group_ids.ids) for k,u in users.items()}
    created=[]
    now=fields.Datetime.now()
    for code, (unit,basis,duration,prices,variants) in SERVICES.items():
        owner=users[PROVIDERS[code]]; job=bases[code]; cells=set()
        for i,(title,description) in enumerate(variants):
            profile=env['tacare.profile'].with_user(owner).sudo().create(dict(user_id=owner.id,
                name=owner.name, profile_title=title, headline=title, bio=description,
                goal='Trao đổi rõ phạm vi, lịch và tiền công trước khi nhận việc.',
                scope='members', visible=True, care_recruitment_enabled=False,
                source_job_id=job.id, flex_demo_key=PREFIX+code+'-'+str(i+1)))
            values=dict(profile_id=profile.id, flex_category_id=job.flex_category_id.id,
                title=title, description=description, flex_state='available',
                flex_mode='remote' if code=='digital' else 'onsite',
                flex_region_id=False if code=='digital' else job.flex_region_id.id,
                flex_schedule='flexible', flex_schedule_note='Nhận theo lịch hẹn; cần xác nhận lại ngày và giờ trước khi làm.',
                flex_rate_min=prices[i], flex_pay_unit=unit, flex_pay_basis=basis, flex_duration=duration,
                flex_tools=['client','shared','discuss'][i], flex_negotiable=True,
                flex_cost_note=['Vật tư và di chuyển thỏa thuận riêng.','Cần chốt chi phí phát sinh trước khi làm.','Chỉ gồm phần tiền công đã mô tả.'][i],
                currency_id=env.ref('base.VND').id)
            if code!='digital':
                radius=[1.4,4.1,8.2][i]
                for step in range(72):
                    angle=math.radians(i*117+step*5+job.id)
                    lat=round(job.geo_lat+radius*math.cos(angle)/111.195,6)
                    lon=round(job.geo_lon+radius*math.sin(angle)/(111.195*math.cos(math.radians(job.geo_lat))),6)
                    cell=tuple(approximate(lat,lon))
                    if cell not in cells:
                        cells.add(cell); break
                else:
                    raise ValidationError('Không tìm được các ô bản đồ khác nhau.')
                assert distance_km(job.geo_lat,job.geo_lon,lat,lon)<10
                address='Điểm thử %s · %s · Việt Nam' % (i+1,job.flex_region_id.name)
                values.update(geo_set=True,geo_lat=lat,geo_lon=lon,geo_sample=True,geo_share=True,
                              geo_address=address,flex_location=address)
            offer=env['care.profile.capability'].with_user(owner).sudo().create(values)
            for purpose in ('discovery','matching'):
                env['care.consent'].with_user(owner).sudo().create(dict(profile_id=profile.id,purpose=purpose,
                    recipient_kind='organization',recipient_partner_id=job.tacare_owner_partner_id.id,
                    field_scope=['profile','skills'],state='granted',granted_by=owner.id,
                    valid_from=now,valid_until=now+timedelta(days=14)))
            assert not offer._flex_ready_errors(), offer._flex_ready_errors()
            result=job._care_compare_profile(profile,allow_profile=True,allow_skills=True)
            assert result['eligible'] and result['capability_id']==offer.id
            created.append(dict(code=code,user_id=owner.id,job_id=job.id,profile_id=profile.id,offer_id=offer.id))
    credentials=[]
    # Native ORM password hashing/session invalidation; suppress local QA alert
    # emails so no notification is sent to any address during the test setup.
    with patch.object(type(env['res.users']), '_notify_security_setting_update', return_value=False):
        for key,old,new,name,role in ACCOUNTS:
            user=users[key]
            password=_new_secret(new)
            user.with_context(no_reset_password=True,mail_notrack=True).write(dict(login=new,name=name,password=password))
            env['care.auth.session'].sudo().search([('user_id','=',user.id),('revoked_at','=',False)])._revoke()
            credentials.append(dict(key=key,user_id=user.id,old_login=old,login=new,name=name,password=password,
                role='provider' if role=='candidate' else 'business'))
    # New profiles display the same account owner; never fabricate extra people.
    new_profiles=env['tacare.profile'].sudo().browse([r['profile_id'] for r in created])
    for p in new_profiles:
        p.write({'name':p.user_id.name})
    after=(_fingerprint(originals,old_profile_fields), _fingerprint(offers,old_offer_fields), _fingerprint(grants,old_grant_fields))
    assert before==after, [label for label,a,b in zip(('profiles','offers','consents'),before,after) if a!=b]
    env.cr.execute('SELECT id,login,password,active FROM res_users WHERE NOT (id = ANY(%s)) ORDER BY id',[selected])
    assert env.cr.fetchall()==untouched_accounts, 'An unrelated account changed'
    assert partner_count==env['res.partner'].sudo().with_context(active_test=False).search_count([])
    assert mail_count==env['mail.mail'].sudo().search_count([])
    assert account_shape=={k:(u.id,u.partner_id.id,u.tacare_account_role,u.company_ids.ids,u.group_ids.ids) for k,u in users.items()}
    receipt=dict(created=created,account_ids=selected,consent_until=str(now+timedelta(days=14)),
        preserved_originals=True,counts={m:env[m].sudo().search_count([]) for m in ['hr.job','tacare.profile','care.profile.capability']})
    def private_write(filename,body):
        fd=os.open(directory/filename,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f: f.write(body)
    private_write(path.name,json.dumps(credentials,ensure_ascii=False,indent=2))
    private_write('map_test_receipt_20261027.json',json.dumps(receipt,ensure_ascii=False,indent=2))
    table=['# Tài khoản kiểm thử local — 27/10/2026','',
        'Chỉ dùng cho ba website localhost. Tài khoản quản trị không thay đổi. Các tài khoản cũ dưới đây đã đổi tên đăng nhập và mật khẩu; cần đăng nhập lại.', '',
        '| Nhóm tài khoản | Đăng nhập mới | Mật khẩu |', '| --- | --- | --- |']
    table += ['| %s | `%s` | `%s` |' % (r['name'],r['login'],r['password']) for r in credentials]
    table += ['', 'Đã thêm 27 hồ sơ: mỗi nghề 3 hồ sơ khác nội dung, tiền công và phạm vi. 24 hồ sơ có điểm thử trên bản đồ; 3 hồ sơ nội dung số làm từ xa.',
        'Cùng một tài khoản có nhiều hồ sơ; các hồ sơ này không đại diện cho nhiều người khác nhau.',
        'Hồ sơ cũ, chủ sở hữu và quyền chia sẻ cũ giữ nguyên. Quyền tìm kiếm/đối chiếu mới chỉ áp dụng cho đúng tổ chức liên quan, hết hạn sau 14 ngày; không cấp quyền liên hệ.', '',
        'Kho: http://khovieclam.localhost:8069/ · Tủ: http://tuhoso.localhost:8069/ · TA.CARE: http://tacare.localhost:8069/#nearby-connections']
    private_write('TAI_KHOAN_TEST_20261027.md','\n'.join(table)+'\n')
    env['care.audit.event'].sudo().create(dict(company_id=env.company.id,actor_user_id=env.user.id,
        action='local.map_test_accounts.prepared',target_model='tacare.profile',target_res_id=new_profiles[0].id,
        changes=dict(account_ids=selected,profile_ids=new_profiles.ids),
        reason='Chủ dự án yêu cầu đổi tên/mật khẩu tài khoản thử và thêm nhiều hồ sơ cùng nghề để thử bản đồ.'))
    return receipt
