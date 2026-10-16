from odoo import api, fields, models
from odoo.exceptions import ValidationError


class TacareConnection(models.Model):
    _name = 'tacare.connection'
    _description = 'TA.CARE Connection'
    _order = 'create_date desc, id desc'

    type = fields.Selection([('application', 'Đề nghị ứng tuyển'),
                             ('invitation', 'Lời mời trao đổi')], required=True)
    job_id = fields.Many2one('hr.job', required=True, ondelete='restrict', index=True)
    company_id = fields.Many2one('res.company', related='job_id.company_id', store=True, index=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='restrict', index=True)
    result_id = fields.Many2one('care.match.result', ondelete='set null', string='Kết quả ghép cặp')
    organization_id = fields.Many2one('res.partner', related='job_id.tacare_owner_partner_id', store=True)
    sender_id = fields.Many2one('res.users', required=True, index=True)
    initiator_user_id = fields.Many2one('res.users', related='sender_id', store=True, string='Người khởi tạo kết nối')
    receiver_id = fields.Many2one('res.users', required=True, index=True)
    recipient_partner_id = fields.Many2one('res.partner', related='receiver_id.partner_id', store=True)
    message = fields.Text()
    status = fields.Selection([('pending', 'Chờ phản hồi'),
                               ('accepted', 'Đồng ý trao đổi'),
                               ('declined', 'Từ chối'),
                               ('cancelled', 'Đã hủy')], default='pending', required=True)
    state = fields.Selection(related='status', readonly=False, string='Trạng thái kết nối TA.CARE')
    requested_at = fields.Datetime(default=fields.Datetime.now, required=True)
    decided_at = fields.Datetime()
    expires_at = fields.Datetime()
    contact_consent_id = fields.Many2one('care.consent', ondelete='set null')
    snapshot_name = fields.Char()
    snapshot_headline = fields.Char()
    snapshot_skills = fields.Char()
    share_contact = fields.Boolean()
    result = fields.Selection([('discussed', 'Đã trao đổi'),
                               ('reviewing', 'Đang xem xét'),
                               ('joined', 'Tham gia cơ hội'),
                               ('stopped', 'Không tiếp tục')])
    result_note = fields.Text()
    result_user_id = fields.Many2one('res.users')
    applicant_id = fields.Many2one('hr.applicant', ondelete='set null')

    @api.constrains('job_id', 'profile_id', 'sender_id', 'receiver_id', 'contact_consent_id')
    def _check_connection(self):
        for item in self:
            if item.sender_id == item.receiver_id:
                raise ValidationError('Không thể tự gửi đề nghị cho chính mình.')
            if item.contact_consent_id and (item.contact_consent_id.profile_id != item.profile_id or
                                            item.contact_consent_id.purpose != 'contact' or
                                            item.contact_consent_id.recipient_partner_id != item.organization_id):
                raise ValidationError('Consent liên hệ không đúng hồ sơ hoặc tổ chức.')

    @api.constrains('job_id', 'profile_id', 'type', 'status')
    def _check_active_duplicate(self):
        for item in self.filtered(lambda record: record.status == 'pending'):
            duplicates = self.search([('id', '!=', item.id), ('job_id', '=', item.job_id.id),
                                      ('profile_id', '=', item.profile_id.id), ('type', '=', item.type),
                                      ('status', '=', 'pending')], limit=1)
            if duplicates:
                raise ValidationError('Đã có đề nghị hoặc lời mời cùng loại đang chờ cho tin và hồ sơ này.')


class TacareNotification(models.Model):
    _name = 'tacare.notification'
    _description = 'TA.CARE Notification'
    _order = 'create_date desc, id desc'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade', index=True)
    connection_id = fields.Many2one('tacare.connection', ondelete='cascade')
    message = fields.Char(required=True)
    is_read = fields.Boolean(default=False)
