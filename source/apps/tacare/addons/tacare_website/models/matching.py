"""Private matching snapshot schema; live comparisons do not persist snapshots."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CareMatchConfig(models.Model):
    _name = 'care.match.config'
    _description = 'TA.CARE Matching Configuration'

    version = fields.Char(required=True, index=True)
    algorithm = fields.Char(required=True)
    model_version = fields.Char()
    weights = fields.Json(default=dict)
    rules = fields.Json(default=dict)
    taxonomy_version = fields.Char()
    taxonomy_snapshot = fields.Json(default=dict)
    state = fields.Selection([('draft', 'Bản nháp'), ('active', 'Đang dùng'),
                              ('retired', 'Ngừng dùng')], default='draft', required=True)
    _unique_version = models.Constraint('unique(version)', 'Phiên bản cấu hình matching phải duy nhất.')


class CareMatchSession(models.Model):
    _name = 'care.match.session'
    _description = 'TA.CARE Matching Session'
    _order = 'create_date desc, id desc'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    config_id = fields.Many2one('care.match.config', required=True, ondelete='restrict')
    requested_by = fields.Many2one('res.users', required=True, ondelete='restrict')
    job_id = fields.Many2one('hr.job', ondelete='restrict')
    profile_id = fields.Many2one('tacare.profile', ondelete='restrict')
    state = fields.Selection([('queued', 'Chờ xử lý'), ('running', 'Đang xử lý'),
                              ('completed', 'Hoàn thành'), ('failed', 'Lỗi')],
                             default='queued', required=True)
    started_at = fields.Datetime()
    finished_at = fields.Datetime()
    idempotency_key = fields.Char(index=True)
    error_code = fields.Char()
    input_ids = fields.One2many('care.match.input', 'session_id')
    result_ids = fields.One2many('care.match.result', 'session_id')
    _unique_idempotency = models.Constraint('unique(idempotency_key)', 'Khóa idempotency matching đã được sử dụng.')

    @api.constrains('job_id', 'profile_id')
    def _check_subject(self):
        for session in self:
            if bool(session.job_id) == bool(session.profile_id):
                raise ValidationError('Một phiên matching phải bắt đầu từ tin hoặc hồ sơ, không phải cả hai.')


class CareMatchInput(models.Model):
    _name = 'care.match.input'
    _description = 'TA.CARE Matching Input Snapshot'

    company_id = fields.Many2one('res.company', related='session_id.company_id', store=True, index=True)
    session_id = fields.Many2one('care.match.session', required=True, ondelete='cascade', index=True)
    job_id = fields.Many2one('hr.job', ondelete='restrict')
    profile_id = fields.Many2one('tacare.profile', ondelete='restrict')
    consent_id = fields.Many2one('care.consent', ondelete='restrict')
    source_version = fields.Integer(required=True)
    payload = fields.Json(default=dict, required=True)
    payload_hash = fields.Char(required=True)
    state = fields.Selection([('valid', 'Hợp lệ'), ('stale', 'Đã cũ'),
                              ('withdrawn', 'Đã thu hồi')], default='valid', required=True)

    @api.constrains('job_id', 'profile_id', 'consent_id')
    def _check_input(self):
        for item in self:
            if bool(item.job_id) == bool(item.profile_id):
                raise ValidationError('Đầu vào matching phải là tin hoặc hồ sơ.')
            if item.profile_id and (not item.consent_id or
                                    item.consent_id.profile_id != item.profile_id or
                                    not item.consent_id.is_current('matching')):
                raise ValidationError('Đầu vào hồ sơ cần consent matching đúng chủ sở hữu.')


class CareMatchResult(models.Model):
    _name = 'care.match.result'
    _description = 'TA.CARE Matching Result Snapshot'

    company_id = fields.Many2one('res.company', related='session_id.company_id', store=True, index=True)
    session_id = fields.Many2one('care.match.session', required=True, ondelete='cascade', index=True)
    job_input_id = fields.Many2one('care.match.input', required=True, ondelete='restrict')
    profile_input_id = fields.Many2one('care.match.input', required=True, ondelete='restrict')
    disclosure_consent_id = fields.Many2one('care.consent', ondelete='restrict')
    total_score = fields.Float()
    component_scores = fields.Json(default=dict)
    explanation = fields.Json(default=dict)
    eligibility = fields.Selection([('eligible', 'Đủ điều kiện'), ('missing', 'Thiếu yêu cầu'),
                                    ('unknown', 'Chưa đủ dữ liệu')], default='unknown', required=True)
    state = fields.Selection([('draft', 'Bản nháp'), ('ready', 'Sẵn sàng'),
                              ('withdrawn', 'Đã thu hồi')], default='draft', required=True)

    @api.constrains('session_id', 'job_input_id', 'profile_input_id', 'total_score', 'disclosure_consent_id')
    def _check_result(self):
        for result in self:
            if result.job_input_id.session_id != result.session_id or result.profile_input_id.session_id != result.session_id:
                raise ValidationError('Hai đầu vào kết quả phải cùng phiên matching.')
            if not result.job_input_id.job_id or not result.profile_input_id.profile_id:
                raise ValidationError('Kết quả cần một đầu vào tin và một đầu vào hồ sơ.')
            if not 0 <= result.total_score <= 100:
                raise ValidationError('Điểm matching phải từ 0 đến 100.')
            if result.disclosure_consent_id and (result.disclosure_consent_id.profile_id != result.profile_input_id.profile_id or
                                                 not result.disclosure_consent_id.is_current('discovery')):
                raise ValidationError('Consent hiển thị kết quả không khớp hồ sơ.')
