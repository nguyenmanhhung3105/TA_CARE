"""Reviewable revisions for changes to a published opportunity."""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CareJobRevision(models.Model):
    _name = 'care.job.revision'
    _description = 'TA.CARE Job Revision'
    _order = 'job_id, version desc'

    company_id = fields.Many2one('res.company', related='job_id.company_id', store=True, index=True)
    job_id = fields.Many2one('hr.job', required=True, ondelete='cascade', index=True)
    version = fields.Integer(required=True)
    payload = fields.Json(default=dict, required=True)
    state = fields.Selection([('draft', 'Bản nháp'), ('submitted', 'Chờ duyệt'),
                              ('approved', 'Đã duyệt'), ('rejected', 'Từ chối'),
                              ('published', 'Đã áp dụng')], default='draft', required=True)
    submitted_by = fields.Many2one('res.users', ondelete='set null')
    reviewed_by = fields.Many2one('res.users', ondelete='set null')
    reviewed_at = fields.Datetime()
    review_note = fields.Text()

    _unique_version = models.Constraint('unique(job_id, version)', 'Phiên bản của tin phải duy nhất.')

    @api.constrains('version', 'payload')
    def _check_revision(self):
        for revision in self:
            if revision.version < 1 or not isinstance(revision.payload, dict):
                raise ValidationError('Phiên bản hoặc nội dung sửa tin không hợp lệ.')

    def write(self, vals):
        if any(item.state == 'published' for item in self):
            raise ValidationError('Phiên bản đã công bố là bất biến.')
        return super().write(vals)

    def unlink(self):
        if any(item.state == 'published' for item in self):
            raise ValidationError('Phiên bản đã công bố không được xóa.')
        return super().unlink()

    def action_publish(self, reviewer, note=None):
        """Apply only reviewed, allowlisted job fields in one ORM transaction."""
        allowed = {
            'name', 'tacare_sector', 'tacare_type', 'tacare_mode', 'tacare_location',
            'tacare_required_skills', 'tacare_preferred_skills', 'tacare_schedule',
            'tacare_pay', 'tacare_outcome', 'tacare_description_text', 'description',
            'website_description', 'no_of_recruitment', 'tacare_start', 'tacare_deadline',
            'care_experience_min', 'care_salary_min', 'care_salary_max', 'care_currency_id',
            'care_matching_enabled',
            'care_sector_id', 'care_position', 'care_level', 'care_work_fraction',
            'care_days_per_week', 'care_duration_months', 'care_shift_note',
            'care_income_type', 'care_income_period', 'care_requires_travel',
            'care_requires_license', 'care_requires_portfolio', 'care_requires_clinical',
            '_requirements',
        }
        for revision in self:
            if revision.state != 'submitted' or not reviewer.has_group('base.group_system'):
                raise ValidationError('Chỉ quản trị được duyệt phiên bản đang chờ.')
            if not set(revision.payload).issubset(allowed):
                raise ValidationError('Phiên bản chứa trường không được phép cập nhật.')
            payload = dict(revision.payload)
            requirements = payload.pop('_requirements', None)
            revision.job_id.write({**payload, 'care_revision': revision.version})
            if requirements is not None:
                revision.job_id.care_requirement_ids.unlink()
                for index, row in enumerate(requirements):
                    self.env['care.job.requirement'].sudo().create({
                        'job_id': revision.job_id.id, 'sequence': (index + 1) * 10, **row})
                revision.job_id._care_sync_requirement_skills()
            if revision.job_id._care_publish_errors():
                raise ValidationError('Bản sửa không đủ điều kiện đăng: ' + ', '.join(revision.job_id._care_publish_errors()))
            revision.job_id._care_sync_job_skills()
            revision.write({'state': 'published', 'reviewed_by': reviewer.id,
                            'reviewed_at': fields.Datetime.now(), 'review_note': note or False})
