"""Explainable comparisons. Absent data stays unknown; no inferred eligibility."""
from odoo import models


class HrJobComparison(models.Model):
    _inherit = 'hr.job'

    def _care_compare_profile(self, profile, allow_profile=False, allow_skills=False):
        self.ensure_one()
        profile.ensure_one()
        if self.care_opportunity_kind == 'flexible':
            return self._care_compare_flexible(profile, allow_profile, allow_skills)
        if not profile.care_recruitment_enabled:
            return dict(matched=[], missing=[], preferred_found=[], comparisons=[], rank=0, eligible=False)
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

    def _care_compare_flexible(self, profile, allow_profile=False, allow_skills=False):
        """Static, conservative suggestions; explicit conflicts exclude an offer.

        Unknown details stay visible for review. No distance, booking or verified
        competence is inferred from self-declared skills, prices or photographs.
        """
        self.ensure_one()
        profile.ensure_one()
        empty = dict(matched=[], missing=[], preferred_found=[], comparisons=[], rank=0, eligible=False)
        if not allow_profile or not allow_skills or self.flex_pay_unit == 'trip':
            return empty
        offers = profile.capability_ids.filtered(lambda s: s.active and s.flex_state == 'available' and
            s.category_id == self.flex_category_id and s.flex_pay_unit != 'trip')
        candidates = []
        for offer in offers:
            rows = []
            def add(name, result, basis, need_value='', offer_value=''):
                rows.append(dict(name=name, result=result, basis=basis, mandatory=True,
                    category='Việc linh hoạt', need_value=need_value or 'Chưa khai',
                    offer_value=offer_value or 'Chưa khai'))
            def dates(record):
                return '%s → %s' % (record.flex_date_from or 'Chưa khai ngày bắt đầu',
                                    record.flex_date_to or 'Chưa khai ngày kết thúc')
            days = dict(enumerate(['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ nhật']))
            def day_names(values):
                return ', '.join(days[int(x)] for x in sorted(values) if x.isdigit() and int(x) in days)
            add('Nghề / đầu việc', 'met', offer.title + ' · Cùng nhóm công việc tự khai.',
                self.flex_category_id.name + ' · ' + self.name, offer.category_id.name + ' · ' + offer.title)
            for title, expected, actual in [('Cách thực hiện', self.flex_mode, offer.flex_mode),
                    ('Tỉnh / thành', self.flex_region_id.id if self.flex_mode != 'remote' else False,
                     offer.flex_region_id.id)]:
                if expected:
                    add(title, 'unknown' if not actual else 'met' if expected == actual else 'unmet',
                        'Hai bên cùng lựa chọn.' if actual == expected else
                        'Hai bên khai khác nhau.' if actual else 'Chưa đủ thông tin.',
                        self._flex_label('flex_mode') if title == 'Cách thực hiện' else self.flex_region_id.name,
                        offer._flex_label('flex_mode') if title == 'Cách thực hiện' else offer.flex_region_id.name)
            if self.flex_date_to and offer.flex_date_from and offer.flex_date_from > self.flex_date_to or \
                    self.flex_date_from and offer.flex_date_to and offer.flex_date_to < self.flex_date_from:
                add('Khoảng ngày', 'unmet', 'Khoảng nhận việc và ngày cần người không giao nhau.', dates(self), dates(offer))
            else:
                add('Khoảng ngày', 'unknown', 'Cần xác nhận lịch trống thực tế trước khi nhận việc.', dates(self), dates(offer))
            job_days, offer_days = set((self.flex_weekdays or '').split(',')) - {''}, set((offer.flex_weekdays or '').split(',')) - {''}
            if job_days and offer_days:
                add('Ngày trong tuần', 'met' if job_days <= offer_days else 'unmet',
                    'Đối chiếu các ngày cần người với ngày nhận việc đã khai.', day_names(job_days), day_names(offer_days))
            if self.flex_time_from and offer.flex_time_from:
                fits = offer.flex_time_from <= self.flex_time_from and offer.flex_time_to >= self.flex_time_to
                add('Khung giờ', 'met' if fits else 'unmet', 'Giờ nhận việc phải bao phủ khung giờ cần người.',
                    self.flex_time_from + '–' + self.flex_time_to, offer.flex_time_from + '–' + offer.flex_time_to)
            if self.flex_rate_min and offer.flex_rate_min and self.flex_pay_unit == offer.flex_pay_unit and \
                    self.flex_pay_basis == offer.flex_pay_basis and offer.currency_id.name == 'VND':
                maximum = self.flex_rate_max or self.flex_rate_min
                add('Tiền công', 'met' if maximum >= offer.flex_rate_min else 'unmet',
                    'Ngân sách và mức nhận cùng đơn vị; chi phí ngoài tiền công cần thống nhất riêng.',
                    self._flex_price_label(), offer._flex_price_label())
            else:
                add('Tiền công', 'unknown', 'Cần cùng đơn vị tiền, cách tính và phạm vi giá để đối chiếu.',
                    self._flex_price_label(), offer._flex_price_label())
            skills = set(offer.flex_skill_ids.ids)
            matched = [s.name for s in self.flex_skill_ids if s.id in skills]
            missing = [s.name for s in self.flex_skill_ids if s.id not in skills]
            for skill in self.flex_skill_ids:
                add(skill.name, 'met' if skill.id in skills else 'unknown',
                    'Có trong đầu việc tự khai.' if skill.id in skills else 'Chưa khai; cần trao đổi, không kết luận thiếu kỹ năng.',
                    skill.name, skill.name if skill.id in skills else 'Chưa khai kỹ năng này')
            add('Khu vực cụ thể và phạm vi công việc', 'unknown',
                'Bên cần: %s. Bên nhận: %s. Cần xác nhận địa chỉ, di chuyển, dụng cụ và đầu ra.' %
                (self.flex_location or 'Từ xa', offer.flex_location or 'Từ xa'),
                self.flex_location or ('Từ xa' if self.flex_mode == 'remote' else 'Chưa khai'),
                offer.flex_location or ('Từ xa' if offer.flex_mode == 'remote' else 'Chưa khai'))
            candidates.append(dict(capability_id=offer.id, matched=matched, missing=missing, preferred_found=[], comparisons=rows,
                rank=sum(r['result'] == 'met' for r in rows), eligible=not any(r['result'] == 'unmet' for r in rows)))
        eligible = [r for r in candidates if r['eligible']]
        return max(eligible, key=lambda r: r['rank']) if eligible else empty
