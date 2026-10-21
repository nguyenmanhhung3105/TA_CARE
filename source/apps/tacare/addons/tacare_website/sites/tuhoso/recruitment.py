"""Explicitly authorized structured recruitment timeline editing."""
import re
from odoo import fields, http
from odoo.http import request
from odoo.exceptions import ValidationError
from werkzeug.exceptions import BadRequest, Forbidden


class RecruitmentControllers(http.Controller):
    def _profile_content_audit(self, action, profile):
        request.env['care.audit.event'].sudo().create({'company_id': profile.company_id.id,
            'actor_user_id': self._user().id, 'action': action, 'target_model': profile._name,
            'target_res_id': profile.id, 'changes': {'admin_edit': self._user() != profile.user_id}})

    def _timeline_values(self, record, kind):
        keys = ('organization','position','employment_type','location','responsibilities','achievements','tools') if kind == 'experience' else ('school','major','description')
        values = {k: record[k] or '' if record else '' for k in keys}
        values.update(start_date=record.start_date.strftime('%Y-%m') if record and record.start_date else '',
            end_date=record.end_date.strftime('%Y-%m') if record and record.end_date else '',
            is_current='on' if record and record.is_current else '',
            qualification_id=str(record.qualification_id.id or '') if record and kind == 'education' else '')
        return values

    def _history_error(self, profile, kind, row_id, submitted, message):
        return self._child_form_error(profile, submitted, kind + ('_edit' if row_id else '_add'), message, row_id)

    @http.route('/tuhoso/history/<string:kind>/save', auth='user', website=True, methods=['POST'])
    def history_save(self, kind, **kw):
        if kind not in ('experience', 'education'):
            raise BadRequest('Loại mục không hợp lệ.')
        profile = self._editable_profile(kw.get('profile_id'), lock=True)
        if not profile.care_recruitment_enabled:
            raise BadRequest('Chọn hồ sơ tuyển dụng để thêm quá trình làm việc hoặc học tập.')
        try:
            row_id = int(kw.get('id') or 0)
        except ValueError:
            raise BadRequest('Mục không hợp lệ.')
        model = request.env['tacare.profile.' + kind].sudo()
        row = model.search([('id', '=', row_id), ('profile_id', '=', profile.id)], limit=1) if row_id else model
        if row_id and not row:
            raise Forbidden('Mục này không thuộc hồ sơ đang chỉnh sửa.')
        texts = ('organization','position','employment_type','location','responsibilities','achievements','tools') if kind == 'experience' else ('school','major','description')
        if set(kw) - set(texts + ('csrf_token','profile_id','id','start_date','end_date','is_current','qualification_id')):
            raise BadRequest('Biểu mẫu có trường không được phép sửa.')
        try:
            vals = {}
            for key in texts:
                value = (kw.get(key) or '').strip()
                if len(value) > (getattr(model._fields[key], 'size', None) or 10000):
                    raise ValidationError('Nội dung quá dài; vui lòng rút gọn.')
                vals[key] = value or False
            for key in ('organization','position') if kind == 'experience' else ('school',):
                if not 2 <= len(vals[key] or '') <= 180:
                    raise ValidationError('Tên đơn vị, vị trí hoặc trường cần từ 2 đến 180 ký tự.')
            if kind == 'experience':
                if vals['employment_type'] and vals['employment_type'] not in dict(model._fields['employment_type'].selection):
                    raise ValidationError('Chọn loại kinh nghiệm hợp lệ.')
            else:
                degree_id = int(kw.get('qualification_id') or 0)
                degree = request.env['hr.recruitment.degree'].sudo().browse(degree_id).exists()
                if degree_id and not degree:
                    raise ValidationError('Trình độ học vấn không hợp lệ.')
                vals['qualification_id'] = degree.id
            for key in ('start_date','end_date'):
                value = kw.get(key) or ''
                if value and not re.fullmatch(r'\d{4}-\d{2}', value):
                    raise ValidationError('Thời gian phải có dạng tháng/năm hợp lệ.')
                vals[key] = fields.Date.to_date(value + '-01') if value else False
            vals['is_current'] = kw.get('is_current') == 'on'
            if vals['is_current']:
                vals['end_date'] = False
            with request.env.cr.savepoint():
                if row:
                    row.write(vals)
                else:
                    if model.search_count([('profile_id','=',profile.id)]) >= 100:
                        raise ValidationError('Mỗi hồ sơ có tối đa 100 mục trong nhóm này.')
                    model.create({**vals, 'profile_id': profile.id})
                self._profile_content_audit('profile.%s.saved' % kind, profile)
        except (ValidationError, ValueError, TypeError, OverflowError) as exc:
            return self._history_error(profile, kind, row_id, kw, str(exc) if isinstance(exc, ValidationError) else 'Kiểm tra tháng bắt đầu/kết thúc và các lựa chọn.')
        return request.redirect('/tuhoso/profile/%s/edit?notice=history#profile-%s-records' % (profile.id, kind))

    @http.route('/tuhoso/history/<string:kind>/<int:record_id>/delete', auth='user', website=True, methods=['POST'])
    def history_delete(self, kind, record_id, **kw):
        if kind not in ('experience','education') or set(kw) - {'csrf_token','profile_id','confirm'} or kw.get('confirm') != 'delete':
            raise BadRequest('Xác nhận mục cần xóa.')
        row = self._my_child('tacare.profile.' + kind, record_id)
        profile = row.profile_id
        row.unlink()
        self._profile_content_audit('profile.%s.deleted' % kind, profile)
        return request.redirect('/tuhoso/profile/%s/edit#profile-%s-records' % (profile.id, kind))
