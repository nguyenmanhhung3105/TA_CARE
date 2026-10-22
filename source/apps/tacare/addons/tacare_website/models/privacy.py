"""Private document ownership, purpose-scoped consent and OCR metadata."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CareDocument(models.Model):
    _name = 'care.document'
    _description = 'TA.CARE Private Document'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    evidence_id = fields.Many2one('tacare.profile.evidence', ondelete='set null')
    attachment_id = fields.Many2one('ir.attachment', ondelete='restrict', copy=False)
    kind = fields.Selection([('cv', 'CV'), ('evidence', 'Minh chứng'),
                             ('other', 'Tài liệu khác')], required=True, default='other')
    state = fields.Selection([('draft', 'Bản nháp'), ('ready', 'Sẵn sàng'),
                              ('removed', 'Đã gỡ')], required=True, default='draft')
    retention_until = fields.Datetime()

    _unique_attachment = models.Constraint('unique(attachment_id)', 'Tệp chỉ được gắn vào một tài liệu TA.CARE.')

    @api.constrains('profile_id', 'evidence_id', 'attachment_id', 'state')
    def _check_document(self):
        for document in self:
            if document.evidence_id and document.evidence_id.profile_id != document.profile_id:
                raise ValidationError('Minh chứng phải thuộc cùng hồ sơ với tài liệu.')
            if document.state == 'ready' and not document.attachment_id:
                raise ValidationError('Tài liệu sẵn sàng cần có tệp đính kèm.')
            if document.attachment_id and document.attachment_id.public:
                raise ValidationError('Tệp hồ sơ không được đặt công khai.')

    def _bind_attachment(self):
        for document in self.filtered('attachment_id'):
            attachment = document.attachment_id
            if attachment.res_model and (attachment.res_model != 'care.document' or
                                         attachment.res_id not in (0, document.id)):
                raise ValidationError('Tệp đã thuộc đối tượng khác.')
            attachment.sudo().write({'res_model': 'care.document', 'res_id': document.id, 'public': False})

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._bind_attachment()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'attachment_id' in vals:
            self._bind_attachment()
        return result


class CareConsent(models.Model):
    _name = 'care.consent'
    _description = 'TA.CARE Purpose-scoped Consent'
    _order = 'create_date desc, id desc'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    purpose = fields.Selection([('matching', 'Xử lý matching'),
                                ('discovery', 'Hiển thị trong tìm kiếm'),
                                ('contact', 'Chia sẻ liên hệ')], required=True)
    recipient_kind = fields.Selection([('public', 'Mọi người'), ('members', 'Thành viên'),
                                       ('organization', 'Bên thuê cụ thể')], required=True)
    recipient_partner_id = fields.Many2one('res.partner', ondelete='restrict')
    field_scope = fields.Json(default=list, required=True)
    version = fields.Integer(default=1, required=True)
    state = fields.Selection([('draft', 'Bản nháp'), ('granted', 'Đã đồng ý'),
                              ('revoked', 'Đã thu hồi')], required=True, default='draft')
    valid_from = fields.Datetime()
    valid_until = fields.Datetime()
    granted_by = fields.Many2one('res.users', ondelete='set null')
    revoked_at = fields.Datetime()
    revoke_reason = fields.Text()

    @api.constrains('purpose', 'recipient_kind', 'recipient_partner_id', 'field_scope',
                    'valid_from', 'valid_until', 'state', 'granted_by')
    def _check_consent(self):
        for consent in self:
            if consent.recipient_kind == 'organization' and not consent.recipient_partner_id:
                raise ValidationError('Quyền riêng cần chỉ rõ bên nhận.')
            if consent.purpose == 'contact' and consent.recipient_kind != 'organization':
                raise ValidationError('Quyền liên hệ chỉ cấp cho bên thuê cụ thể.')
            if consent.valid_from and consent.valid_until and consent.valid_until <= consent.valid_from:
                raise ValidationError('Thời hạn quyền chia sẻ không hợp lệ.')
            if not isinstance(consent.field_scope, list) or any(not isinstance(x, str) for x in consent.field_scope):
                raise ValidationError('Phạm vi chia sẻ phải là danh sách tên trường.')
            if consent.state == 'granted' and consent.granted_by != consent.profile_id.user_id:
                raise ValidationError('Chỉ chủ hồ sơ được cấp quyền chia sẻ.')

    def is_current(self, purpose, recipient=None, field=None):
        self.ensure_one()
        now = fields.Datetime.now()
        return bool(self.state == 'granted' and self.purpose == purpose and
                    (not self.valid_from or self.valid_from <= now) and
                    (not self.valid_until or now < self.valid_until) and
                    (self.recipient_kind != 'organization' or
                     recipient and self.recipient_partner_id == recipient) and
                    (not field or field in self.field_scope))


class CareOcrJob(models.Model):
    _name = 'care.ocr.job'
    _description = 'TA.CARE OCR Task Metadata'
    _order = 'create_date desc, id desc'

    company_id = fields.Many2one('res.company', related='profile_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='cascade', index=True)
    document_id = fields.Many2one('care.document', required=True, ondelete='restrict')
    requested_by = fields.Many2one('res.users', required=True, ondelete='restrict')
    state = fields.Selection([('queued', 'Chờ xử lý'), ('running', 'Đang xử lý'),
                              ('extracted', 'Đã trích xuất'), ('confirmed', 'Đã xác nhận'),
                              ('failed', 'Lỗi')], default='queued', required=True)
    provider = fields.Char()
    error_code = fields.Char()
    extracted_data = fields.Json()
    base_profile_version = fields.Integer(required=True)
    confirmed_by = fields.Many2one('res.users', ondelete='set null')
    confirmed_at = fields.Datetime()
    retention_until = fields.Datetime()

    @api.constrains('profile_id', 'document_id', 'requested_by', 'confirmed_by', 'state')
    def _check_task(self):
        for task in self:
            if task.document_id.profile_id != task.profile_id:
                raise ValidationError('Tác vụ OCR phải xử lý tài liệu của cùng hồ sơ.')
            if task.requested_by != task.profile_id.user_id:
                raise ValidationError('Chỉ chủ hồ sơ được yêu cầu OCR.')
            if task.state == 'confirmed' and (task.confirmed_by != task.profile_id.user_id or not task.confirmed_at):
                raise ValidationError('Kết quả OCR cần được chủ hồ sơ xác nhận.')
