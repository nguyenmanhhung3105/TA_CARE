"""Fictional UI scenarios; no personal data, consent or connection is fabricated."""
from odoo import http
from odoo.http import request
from werkzeug.exceptions import Forbidden, BadRequest
from ...controllers.profiles import TacareProfiles


class TacareExamples(TacareProfiles):
    def _example_cards(self):
        scenarios = [
            ('Dọn căn hộ sáng thứ Bảy', 'Người nhận dọn nhà theo giờ', 'Có căn cứ để trao đổi', [
                ('Đầu việc', 'met', 'Cả hai cùng khai lau sàn, bếp và nhà tắm.'),
                ('Khu vực', 'met', 'Cùng TP.HCM; địa chỉ và quãng đường cần xác nhận.'),
                ('Lịch', 'met', 'Bên thuê cần 08:00–11:00 thứ Bảy; bên nhận khai 08:00–12:00.'),
                ('Tiền công', 'met', 'Ngân sách 80.000đ/giờ, mức nhận từ 65.000đ/giờ, cùng cách tính mỗi người.'),
                ('Dụng cụ', 'unknown', 'Cần chốt danh sách hóa chất và dụng cụ trước khi làm.')]),
            ('Frontend cho sản phẩm giáo dục', 'Hồ sơ Frontend Junior', 'Cần bổ sung thông tin', [
                ('JavaScript và CSS', 'met', 'Có trong kỹ năng tự khai của hồ sơ mẫu.'),
                ('Cách làm', 'met', 'Cả hai chọn kết hợp.'),
                ('Kinh nghiệm', 'unknown', 'Hồ sơ chưa nêu số tháng cho đúng nhóm nghề.'),
                ('Thu nhập', 'unknown', 'Chưa đủ thông tin gross/net để đối chiếu.')]),
            ('Chăm vườn vào thứ Hai', 'Người nhận chăm cây cuối tuần', 'Không đưa vào gợi ý hiện tại', [
                ('Đầu việc', 'met', 'Cùng nhóm chăm cây và thay chậu.'),
                ('Ngày trong tuần', 'unmet', 'Tin cần thứ Hai; hồ sơ chỉ nhận thứ Bảy và Chủ nhật.'),
                ('Cách xử lý', 'unknown', 'Hai bên cần cập nhật lịch trước khi có thể kết nối.')]),
        ]
        examples = [dict(job=j, profile=p, outcome=o, comparisons=[dict(name=n, result=r,
            basis=b, mandatory=True, category='Ví dụ hư cấu') for n, r, b in rows])
            for j, p, o, rows in scenarios]
        return examples

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
