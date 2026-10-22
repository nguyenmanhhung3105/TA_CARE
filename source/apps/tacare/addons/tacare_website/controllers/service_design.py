"""Public design metadata, shared across Kho and Tủ; no account/profile discovery."""
from urllib.parse import urlencode

ASSET = '/tacare_website/static/src/'
CATEGORY_DESIGN = [
    ('cleaning', 'Dọn dẹp nhà', 'broom', 'mint', 'Lau dọn, vệ sinh theo giờ'),
    ('repair', 'Sửa chữa & lắp ráp', 'hammer', 'peach', 'Sửa đồ, lắp kệ, hoàn thiện góc nhà'),
    ('garden', 'Chăm cây & làm vườn', 'plant', 'lime', 'Tưới cây, thay chậu, chăm vườn'),
    ('cooking', 'Nấu ăn & phụ bếp', 'cooking-pot', 'butter', 'Bữa cơm nhà, một buổi phụ bếp'),
    ('loading', 'Kho & chuyển đồ', 'package', 'sky', 'Đóng gói, sắp xếp, thêm người theo ca'),
    ('digital', 'Thiết kế & việc số', 'paint-brush', 'lilac', 'Ấn phẩm, hình ảnh, nội dung từ xa'),
    ('tutoring', 'Dạy kèm & kỹ năng', 'book-open', 'rose', 'Chia sẻ kiến thức theo buổi'),
    ('pets', 'Chăm thú cưng', 'paw-print', 'peach', 'Cho ăn, đi dạo, chăm khi chủ vắng'),
    ('farm', 'Nông nghiệp', 'carrot', 'mint', 'Chăm luống rau, hỗ trợ mùa vụ'),
]


def service_design_context(categories, jobs):
    by_code = {category.code: category for category in categories}
    catalog = []
    for code, label, icon, tone, description in CATEGORY_DESIGN:
        category = by_code.get(code)
        if not category:
            continue
        catalog.append(dict(code=code, label=label, icon=icon, tone=tone,
            description=description, id=category.id,
            photo=ASSET + 'img/services/' + code + '.webp',
            count=len(jobs.filtered(lambda job: job.flex_category_id == category)),
            profile_query=urlencode({'kind':'flexible', 'profile_title':'Nhận ' + label.lower()})))
    meta = {item['code']: item for item in catalog}
    scenarios = [
        dict(title='Nhà thêm gọn. Ngày thêm vui.', label='Cho tổ ấm của bạn', icon='house', tone='mint',
             text='Một góc nhà cần sửa, một khu vườn cần chăm. Bắt đầu từ đúng việc bạn đang cần.',
             photo='repair', codes=['cleaning', 'repair', 'garden', 'pets']),
        dict(title='Thêm đôi tay cho tiệm nhỏ.', label='Cho việc kinh doanh', icon='storefront', tone='butter',
             text='Một ca phụ bếp, một buổi sắp hàng. Tìm người cùng hoàn thành phần việc cụ thể.',
             photo='cleaning', codes=['cooking', 'loading', 'farm']),
        dict(title='Ở đâu cũng tạo được giá trị.', label='Cho những việc từ xa', icon='laptop', tone='lilac',
             text='Một mẫu thiết kế, một buổi chia sẻ kỹ năng. Kết nối theo đầu ra và lịch hai bên.',
             photo='digital', codes=['digital', 'tutoring']),
    ]
    featured = jobs.browse()
    used = set()
    for job in jobs:
        code = job.flex_category_id.code
        if code in meta and code not in used:
            featured |= job
            used.add(code)
        if len(featured) == 4:
            break
    return dict(service_catalog=catalog, service_by_code=meta, service_scenarios=scenarios,
        service_featured_jobs=featured,
        provider_stories=[('cooking', 'cooking', 'Một bữa ăn ngon, một khả năng đáng chia sẻ.'),
                          ('garden', 'garden', 'Khéo chăm một chậu cây, hay cả khu vườn.'),
                          ('pets', 'pets', 'Một chút quan tâm, thêm một người bạn nhỏ.')])
