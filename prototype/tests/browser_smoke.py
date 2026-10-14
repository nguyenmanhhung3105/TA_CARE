"""Optional end-to-end smoke test; run with Python 3.12 and Playwright + local Chrome."""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:4173'
OUT = Path(__file__).resolve().parents[2] / 'docs' / 'screenshots'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))

    for site in ['khovieclam', 'tuhoso', 'tacare']:
        page.goto(f'{BASE}/{site}')
        page.locator('h1').wait_for()
        assert page.locator('img.logo').evaluate('(img) => img.complete && img.naturalWidth > 0')
        page.screenshot(path=str(OUT / f'{site}-desktop.png'), full_page=True)
        print(site, page.locator('h1').inner_text())

    page.set_viewport_size({'width': 375, 'height': 812})
    for site in ['khovieclam', 'tuhoso', 'tacare']:
        page.goto(f'{BASE}/{site}')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'{site} horizontal overflow'
    page.screenshot(path=str(OUT / 'tacare-mobile.png'), full_page=True)
    page.set_viewport_size({'width': 1440, 'height': 900})

    page.goto(f'{BASE}/khovieclam/job/new')
    page.locator('#demo-user').select_option('u-sen')
    page.goto(f'{BASE}/khovieclam/job/new')
    page.get_by_role('button', name='Đăng tin').click()
    assert page.locator('#title-error').inner_text()
    page.locator('#title').fill('Thực tập phân tích dữ liệu')
    page.locator('#sector').select_option('Công nghệ thông tin')
    page.locator('#type').select_option('Thực tập')
    page.locator('#mode').select_option('Kết hợp')
    page.locator('#location').fill('Hà Nội')
    page.locator('#experience').select_option('Không yêu cầu')
    page.locator('#deadline').fill('2026-12-30')
    page.locator('#description').fill('Hỗ trợ nhóm phân tích dữ liệu mẫu.')
    page.locator('#required').select_option('SQL')
    page.get_by_role('button', name='Xem trước').click()
    assert page.get_by_text('Xem trước tin').count() > 0
    page.get_by_role('button', name='Đăng tin').click()
    assert 'Tin đã được đăng' in page.locator('.alert.success').inner_text()
    new_job = page.url.rsplit('/', 1)[-1]
    print('new job', new_job)

    page.locator('#demo-user').select_option('u-nam')
    page.goto(f'{BASE}/khovieclam/job/{new_job}/edit')
    assert page.get_by_text('Tin thuộc tổ chức khác.').count() > 0

    page.locator('#demo-user').select_option('u-an')
    page.goto(f'{BASE}/tuhoso/skills')
    page.locator('#name').select_option('SQL')
    page.get_by_role('button', name='Thêm kỹ năng').click()
    assert page.get_by_text('Đã lưu kỹ năng').count() > 0
    page.get_by_role('button', name='Sửa').first.click()
    page.locator('#level').select_option('Thành thạo')
    page.get_by_role('button', name='Lưu kỹ năng').click()
    assert 'Thành thạo' in page.locator('.skill-list').inner_text()
    page.goto(f'{BASE}/tuhoso/evidence')
    page.locator('#title').fill('Dự án thử nghiệm')
    page.locator('#role').fill('Thành viên')
    page.get_by_role('button', name='Lưu minh chứng').click()
    assert page.get_by_text('Dự án thử nghiệm').count() > 0
    page.locator('#cv-file').set_input_files({'name':'cv-mau.pdf','mimeType':'application/pdf','buffer':b'%PDF-1.4 demo'})
    assert page.get_by_text('cv-mau.pdf').count() > 0
    assert page.get_by_role('link', name='Xem tệp vừa chọn').count() > 0
    assert '%PDF-1.4 demo' not in page.evaluate('JSON.stringify(localStorage)')
    page.goto(f'{BASE}/tuhoso/apply/{new_job}')
    page.get_by_role('button', name='Gửi đề nghị ứng tuyển').click()
    request_id = page.url.rsplit('/', 1)[-1]
    assert page.get_by_text('Chờ phản hồi').count() > 0
    print('new request', request_id)

    page.locator('#demo-user').select_option('u-sen')
    page.goto(f'{BASE}/tacare/connection/{request_id}')
    page.get_by_role('button', name='Đồng ý trao đổi').click()
    assert page.get_by_text('Đồng ý trao đổi').count() > 0
    assert 'an@example.com' not in page.locator('main').inner_text()
    page.locator('#result').select_option('Đã trao đổi')
    page.get_by_role('button', name='Lưu kết quả trao đổi').click()
    assert 'Đã trao đổi' in page.locator('main').inner_text()

    page.goto(f'{BASE}/tacare/invite/j-01/p-binh')
    page.get_by_role('button', name='Gửi lời mời').click()
    invite_id = page.url.rsplit('/', 1)[-1]
    page.locator('#demo-user').select_option('u-binh')
    page.goto(f'{BASE}/tacare/connection/{invite_id}')
    page.get_by_role('button', name='Đồng ý trao đổi').click()
    assert 'Đồng ý trao đổi' in page.locator('main').inner_text()
    page.goto(f'{BASE}/tuhoso/sharing')
    page.locator('input[name="shareContact"]').check()
    page.get_by_role('button', name='Lưu lựa chọn').click()
    page.locator('#demo-user').select_option('u-sen')
    page.goto(f'{BASE}/tacare/connection/{invite_id}')
    assert 'binh@example.com' in page.locator('main').inner_text()
    page.locator('#demo-user').select_option('u-binh')
    page.goto(f'{BASE}/tuhoso/sharing')
    page.locator('input[name="shareContact"]').uncheck()
    page.locator('#scope').select_option('private')
    page.locator('input[name="visible"]').uncheck()
    page.get_by_role('button', name='Lưu lựa chọn').click()
    page.locator('#demo-user').select_option('u-sen')
    page.goto(f'{BASE}/tacare/connection/{invite_id}')
    assert 'binh@example.com' not in page.locator('main').inner_text()
    page.goto(f'{BASE}/khovieclam/candidates')
    assert page.get_by_role('link', name='Mạnh Hùng').count() == 0

    page.goto(f'{BASE}/khovieclam/opportunities')
    page.locator('#q').fill('không có tin này')
    page.get_by_role('button', name='Áp dụng bộ lọc').click()
    assert page.get_by_text('Chưa có cơ hội phù hợp').count() > 0
    page.get_by_role('button', name='Xóa bộ lọc').first.click()
    assert page.locator('.job-card').count() >= 12

    page.goto(f'{BASE}/tacare/matching')
    assert 'Điểm phù hợp' in page.locator('main').inner_text()
    page.goto(f'{BASE}/tacare/notifications')
    assert page.locator('.notification').count() > 0
    page.reload()
    assert page.locator('#demo-user').input_value() == 'u-sen'
    page.set_viewport_size({'width': 375, 'height': 812})
    for route in ['/khovieclam/job/new', '/tacare/connections']:
        page.goto(BASE + route)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), route
    page.locator('#demo-user').select_option('u-an')
    page.goto(BASE + '/tuhoso/profile/edit')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.set_viewport_size({'width': 1440, 'height': 900})
    assert not errors, errors
    print('browser smoke PASS')
    browser.close()
