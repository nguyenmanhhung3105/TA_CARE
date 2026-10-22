"""Fictional UI scenarios; no personal data, consent or connection is fabricated."""
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden, BadRequest
from ...controllers.profiles import TacareProfiles


class TacareExamples(TacareProfiles):
    @http.route('/how-it-works', auth='public', website=True, methods=['GET'])
    def seasonal_journey(self, **kw):
        return self._render('seasonal_journey', site='tacare')

    def _example_cards(self):
        scenarios = [
            ('Dọn căn hộ sáng thứ Bảy', 'Người nhận dọn nhà theo giờ', 'Có căn cứ để trao đổi', [
                ('Đầu việc', 'met', 'Cả hai cùng khai lau sàn, bếp và nhà tắm.'),
                ('Khu vực', 'met', 'Cùng TP.HCM; địa chỉ và quãng đường cần xác nhận.'),
                ('Lịch', 'met', 'Bên thuê cần 08:00–11:00 thứ Bảy; bên nhận khai 08:00–12:00.'),
                ('Tiền công', 'met', 'Ngân sách 80.000đ/giờ, mức nhận từ 65.000đ/giờ, cùng cách tính mỗi người.'),
                ('Dụng cụ', 'unknown', 'Cần chốt danh sách hóa chất và dụng cụ trước khi làm.')]),
            ('Thiết kế ấn phẩm cho quán cà phê', 'Người nhận thiết kế theo sản phẩm', 'Cần bổ sung thông tin', [
                ('Đầu ra', 'met', 'Cùng mô tả một poster và các kích thước bàn giao.'),
                ('Cách làm', 'met', 'Cả hai nhận trao đổi từ xa.'),
                ('Lịch', 'unknown', 'Cần xác nhận hạn gửi bản nháp và số vòng chỉnh sửa.'),
                ('Chi phí', 'unknown', 'Chưa chốt phí tài nguyên có bản quyền và phần phát sinh.')]),
            ('Chăm vườn vào thứ Hai', 'Người nhận chăm cây cuối tuần', 'Không đưa vào gợi ý hiện tại', [
                ('Đầu việc', 'met', 'Cùng nhóm chăm cây và thay chậu.'),
                ('Ngày trong tuần', 'unmet', 'Tin cần thứ Hai; hồ sơ chỉ nhận thứ Bảy và Chủ nhật.'),
                ('Cách xử lý', 'unknown', 'Hai bên cần cập nhật lịch trước khi có thể kết nối.')]),
        ]
        examples = [dict(job=j, profile=p, outcome=o, comparisons=[dict(name=n, result=r,
            basis=b, mandatory=True, category='Ví dụ hư cấu') for n, r, b in rows])
            for j, p, o, rows in scenarios]
        visual = [
            ('cleaning', 'cleaning', 'Dọn nhà theo giờ', '80.000đ / giờ / người', 'Sáng thứ Bảy · TP.HCM', 'Có thể trao đổi', 'met'),
            ('digital', 'digital', 'Thiết kế theo đầu việc', 'Cần thống nhất chi phí', 'Làm từ xa · Theo sản phẩm', 'Cần làm rõ', 'unknown'),
            ('garden', 'garden', 'Chăm cây theo buổi', 'Chưa chốt tiền công', 'Tin cần thứ Hai · Hồ sơ rảnh cuối tuần', 'Lịch chưa phù hợp', 'unmet'),
        ]
        for example, (key, photo, category, price, schedule, badge, state) in zip(examples, visual):
            example.update(key=key, photo=photo, category=category, price=price, schedule=schedule,
                           badge=badge, state=state)
        amounts = [('80.000đ / giờ / người', 'Từ 65.000đ / giờ / người', 'Thứ Bảy, 08:00–11:00', 'Thứ Bảy, 08:00–12:00'),
                   ('Cần thống nhất chi phí', 'Chưa báo giá đầy đủ', 'Làm từ xa, cần chốt hạn bàn giao', 'Nhận thiết kế theo sản phẩm'),
                   ('Chưa chốt tiền công', 'Chưa chốt tiền công', 'Cần làm vào thứ Hai', 'Chỉ nhận thứ Bảy và Chủ nhật')]
        for example, (need_price, offer_price, need_schedule, offer_schedule) in zip(examples, amounts):
            example.update(need_price=need_price, offer_price=offer_price, need_schedule=need_schedule, offer_schedule=offer_schedule)
        return examples

    def _home_suggestions(self):
        self._flex_user()
        jobs, selected, hire = self._hire_matching_data()
        data = {'jobs': jobs, 'selected': selected, 'hire': hire[:3], 'profile': False, 'receive': [],
                'can_receive': self._role() != 'business'}
        if data['can_receive']:
            profile = self._my_profile()
            data.update(profile=profile, receive=self._receive_matching_data(profile)[:3] if profile else [])
        return data

    @http.route('/tacare/examples', auth='user', website=True, methods=['GET'])
    def examples(self, **kw):
        self._flex_user()
        return self._render('matching_examples', examples=self._example_cards())

    def _home_admin_matches(self, **kw):
        if self._role() != 'admin':
            raise Forbidden('Chỉ quản trị được xem tổng quan đối chiếu.')
        jobs = request.env['hr.job'].sudo().search(self._job_domain() + [
            ('company_id', 'in', self._user().company_ids.ids), ('care_matching_enabled', '=', True)],
            order='write_date desc, id desc', limit=100)
        selected_id = str(kw.get('home_job') or '')
        if selected_id and not selected_id.isdigit():
            raise BadRequest('Tin đối chiếu không hợp lệ.')
        selected = jobs.filtered(lambda j: j.id == int(selected_id)) if selected_id else jobs[:6]
        if selected_id and not selected:
            raise BadRequest('Tin không còn sẵn sàng hoặc nằm ngoài phạm vi quản lý.')
        pairs = []
        for job in selected:
            profiles = self._visible_profiles(job.tacare_owner_partner_id).filtered(lambda p:
                self._current_consent(p, 'matching', job.tacare_owner_partner_id, 'profile') and
                self._current_consent(p, 'matching', job.tacare_owner_partner_id, 'skills'))
            for profile in profiles:
                reason = self._match(job, profile)
                if reason.get('eligible', True) and reason['rank']:
                    pairs.append({'job': job, 'profile': profile, 'reason': reason})
        pairs.sort(key=lambda p: p['reason']['rank'], reverse=True)
        return {'jobs': jobs, 'selected_id': selected_id, 'pairs': pairs[:3], 'checked_job_count': len(selected),
                'examples': self._example_cards()}
