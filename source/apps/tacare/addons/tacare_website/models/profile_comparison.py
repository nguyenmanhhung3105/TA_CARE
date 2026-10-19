"""Explainable comparisons. Absent data stays unknown; no inferred eligibility."""
from odoo import models


class HrJobComparison(models.Model):
    _inherit = 'hr.job'

    def _care_compare_profile(self, profile, allow_profile=False, allow_skills=False):
        self.ensure_one()
        profile.ensure_one()
        rows = []

        def add(name, result, basis, mandatory=False, category='Điều kiện làm việc'):
            rows.append(dict(name=name, result=result, basis=basis, mandatory=mandatory, category=category))

        def compare(name, expected, actual, category='Điều kiện làm việc'):
            if expected:
                add(name, 'unknown' if not actual else 'met' if expected == actual else 'unmet',
                    'Hai bên chọn cùng giá trị.' if actual and expected == actual else
                    'Hai bên đang chọn khác giá trị; cần trao đổi lại.' if actual else
                    'Chưa có thông tin được chia sẻ để đối chiếu.', category=category)

        split = lambda text: [x.strip() for x in (text or '').split(',') if x.strip()]
        names = {name.casefold() for name in profile.skill_ids.mapped('name')} if allow_skills else set()
        required, preferred = split(self.tacare_required_skills), split(self.tacare_preferred_skills)
        matched = [x for x in required if x.casefold() in names]
        missing = [x for x in required if x.casefold() not in names]
        preferred_found = [x for x in preferred if x.casefold() in names]
        if self.care_skills_any and required:
            add('Một trong: ' + ', '.join(required), 'met' if matched else 'unknown',
                'Kỹ năng tự khai trùng: ' + ', '.join(matched) if matched else
                'Chưa có dữ liệu kỹ năng trùng; không kết luận ứng viên không có kỹ năng.', True, 'Kỹ năng')
        else:
            for name in required:
                add(name, 'met' if name.casefold() in names else 'unknown',
                    'Có trong kỹ năng ứng viên tự khai.' if name.casefold() in names else
                    'Kỹ năng chưa được khai hoặc chưa được chia sẻ.', True, 'Kỹ năng')
        for name in preferred:
            add(name, 'met' if name.casefold() in names else 'unknown',
                'Có trong kỹ năng ứng viên tự khai.' if name.casefold() in names else
                'Chưa có dữ liệu cho kỹ năng này.', False, 'Kỹ năng')
        if self.care_position_id:
            compare('Nhóm nghề', self.care_position_id.id,
                    profile.desired_position_id.id if allow_profile else False, 'Định hướng')
        if self.care_experience_min:
            known = allow_profile and profile.experience_known and self.care_position_id and \
                self.care_position_id == profile.desired_position_id
            add('Kinh nghiệm liên quan tối thiểu: %g năm' % self.care_experience_min,
                'unknown' if not known else 'met' if profile.relevant_months >= self.care_experience_min * 12 else 'unmet',
                '%s tháng ứng viên tự khai cho cùng nhóm nghề.' % profile.relevant_months if known else
                'Cần số tháng kinh nghiệm đã xác nhận cho đúng nhóm nghề.', True, 'Kinh nghiệm')
        compare('Hình thức làm việc', self.tacare_mode, profile.mode if allow_profile else False)
        # Keep legacy values readable, but normalize the opportunity/fraction axes.
        job_type = 'employment' if self.tacare_type in ('full_time', 'part_time') else self.tacare_type
        compare('Loại cơ hội', job_type, profile.desired_type if allow_profile else False)
        compare('Thời lượng làm việc', self.care_work_fraction, profile.work_fraction if allow_profile else False)
        if self.tacare_mode != 'remote' and self.care_region_id:
            compare('Tỉnh / thành làm việc', self.care_region_id.id, profile.region_id.id if allow_profile else False)
        if self.care_salary_display != 'negotiable' and (self.care_salary_min or self.care_salary_max):
            comparable = allow_profile and profile.salary_min > 0 and self.care_salary_basis == 'base' and \
                self.care_currency_id == profile.salary_currency_id and \
                self.care_income_period == profile.salary_period and \
                self.care_salary_tax in ('gross', 'net') and self.care_salary_tax == profile.salary_tax
            state, basis = 'unknown', 'Cần cùng tiền tệ, kỳ trả, gross/net và lương cố định để so sánh.'
            if comparable:
                if self.care_salary_max:
                    state = 'met' if self.care_salary_max >= profile.salary_min else 'unmet'
                    basis = 'Đối chiếu mức mong muốn tối thiểu với trần lương công bố; mức cụ thể cần thỏa thuận.'
                elif self.care_salary_min >= profile.salary_min:
                    state, basis = 'met', 'Mức sàn lương công bố đáp ứng mong muốn tối thiểu.'
                else:
                    basis = 'Tin chỉ công bố mức sàn, chưa có trần lương để kết luận.'
            add('Lương cố định mong muốn', state, basis, category='Thu nhập')
        if self.care_requires_travel:
            actual = profile.travel if allow_profile else False
            add('Có thể đi công tác / di chuyển', 'unknown' if not actual else 'met' if actual == 'yes' else 'unmet',
                'Theo lựa chọn ứng viên tự khai.' if actual else 'Ứng viên chưa nêu khả năng di chuyển.', True)
        if self.tacare_start and not self.care_start_flexible:
            actual = profile.start_date if allow_profile else False
            add('Ngày có thể bắt đầu', 'unknown' if not actual else 'met' if actual <= self.tacare_start else 'unmet',
                'So sánh ngày sẵn sàng với ngày bắt đầu bắt buộc.' if actual else 'Chưa nêu ngày sẵn sàng.', True)
        for title, requirement, actual in [
                ('Học vấn', self.care_education_note, profile.education_details if allow_profile else ''),
                ('Ngoại ngữ', self.care_language_note, profile.languages if allow_profile else ''),
                ('Giấy phép / chứng chỉ', self.care_license_note, profile.licenses if allow_profile else ''),
                ('Lịch bắt buộc', self.tacare_schedule if self.care_schedule_required else '',
                 profile.availability if allow_profile else '')]:
            if requirement:
                add(title + ': ' + requirement, 'unknown',
                    'Cần nhà tuyển dụng kiểm tra nội dung tự khai: ' + actual if actual else
                    'Chưa có dữ liệu trực tiếp; cần bổ sung và kiểm tra.', True, 'Điều kiện bổ sung')
        for row in self.care_requirement_ids:
            add(row.name, 'unknown', 'Tiêu chí cũ cần nhà tuyển dụng kiểm tra trực tiếp.', row.mandatory, 'Tiêu chí bổ sung')
        return dict(matched=matched, missing=missing, preferred_found=preferred_found,
                    same_mode=allow_profile and bool(profile.mode) and profile.mode == self.tacare_mode,
                    same_location=allow_profile and bool(profile.region_id) and
                        (self.tacare_mode == 'remote' or profile.region_id == self.care_region_id),
                    comparisons=rows, rank=sum(row['result'] == 'met' for row in rows))
