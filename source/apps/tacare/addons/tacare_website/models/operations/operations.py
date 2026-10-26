"""Feedback, append-only audit and integration outbox metadata."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CareFeedback(models.Model):
    _name = 'care.feedback'
    _description = 'TA.CARE Feedback'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    author_user_id = fields.Many2one('res.users', required=True, ondelete='restrict')
    result_id = fields.Many2one('care.match.result', ondelete='restrict')
    connection_id = fields.Many2one('tacare.connection', ondelete='restrict')
    rating = fields.Integer()
    reason = fields.Text()

    @api.constrains('result_id', 'connection_id', 'rating')
    def _check_feedback(self):
        for item in self:
            if bool(item.result_id) == bool(item.connection_id):
                raise ValidationError('Phản hồi phải gắn với kết quả hoặc kết nối.')
            if not 1 <= item.rating <= 5:
                raise ValidationError('Đánh giá phải từ 1 đến 5.')


class CareAuditEvent(models.Model):
    _name = 'care.audit.event'
    _description = 'TA.CARE Audit Event'
    _order = 'occurred_at desc, id desc'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    actor_user_id = fields.Many2one('res.users', ondelete='set null')
    action = fields.Char(required=True)
    target_model = fields.Char(required=True)
    target_res_id = fields.Integer(required=True)
    occurred_at = fields.Datetime(required=True, default=fields.Datetime.now)
    reason = fields.Char()
    changes = fields.Json(default=dict, string='Dữ liệu thay đổi')
    correlation_id = fields.Char(index=True)

    def write(self, vals):
        raise ValidationError('Nhật ký kiểm toán là bất biến.')

    def unlink(self):
        raise ValidationError('Nhật ký kiểm toán là bất biến.')


class CareIntegrationEvent(models.Model):
    _name = 'care.integration.event'
    _description = 'TA.CARE Integration Event Metadata'
    _order = 'create_date desc, id desc'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    source = fields.Char(required=True)
    event_id = fields.Char(required=True)
    entity_ref = fields.Char()
    source_version = fields.Char()
    state = fields.Selection([('pending', 'Chờ xử lý'), ('processed', 'Đã xử lý'),
                              ('failed', 'Lỗi')], default='pending', required=True)
    retry_count = fields.Integer(default=0)
    next_retry_at = fields.Datetime()
    correlation_id = fields.Char(index=True)
    error_code = fields.Char()
    _unique_source_event = models.Constraint('unique(source, event_id)', 'Sự kiện tích hợp đã được ghi nhận.')
