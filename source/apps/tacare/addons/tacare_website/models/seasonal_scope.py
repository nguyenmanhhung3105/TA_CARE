"""Seasonal-only writes, without renaming the existing storage models."""
import re
from werkzeug.exceptions import NotFound
from odoo import api, models
from odoo.http import request
from odoo.exceptions import ValidationError


class SeasonalJobScope(models.Model):
    _inherit = 'hr.job'

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get('care_opportunity_kind', 'flexible') != 'flexible' for vals in vals_list):
            raise ValidationError('TA.CARE chỉ hỗ trợ nhu cầu việc thời vụ.')
        return super().create([{**vals, 'care_opportunity_kind': 'flexible'} for vals in vals_list])

    def write(self, vals):
        if 'care_opportunity_kind' in vals and vals['care_opportunity_kind'] != 'flexible':
            raise ValidationError('TA.CARE chỉ hỗ trợ nhu cầu việc thời vụ.')
        return super().write(vals)


class SeasonalProfileScope(models.Model):
    _inherit = 'tacare.profile'

    @api.model_create_multi
    def create(self, vals_list):
        if any(vals.get('care_recruitment_enabled') for vals in vals_list):
            raise ValidationError('Chỉ tạo hồ sơ nhận việc thời vụ.')
        return super().create([{**vals, 'care_recruitment_enabled': False} for vals in vals_list])

    def write(self, vals):
        if vals.get('care_recruitment_enabled'):
            raise ValidationError('Không chuyển hồ sơ thành hồ sơ tuyển dụng.')
        return super().write(vals)


class SeasonalRoutePolicy(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _pre_dispatch(cls, rule, arguments):
        path=request.httprequest.path.rstrip('/') or '/'
        retired=(path=='/jobs' or path.startswith('/jobs/') or path=='/kvl/candidates' or
            path in ('/kvl/job/new','/kvl/job/save','/website/form/hr.applicant') or path.startswith('/website_hr_recruitment/') or
            re.fullmatch(r'/kvl/revision/\d+/review',path) or
            re.fullmatch(r'/kvl/job/\d+/(?:edit|preview|history|status|delete|candidate/\d+)',path) or
            re.fullmatch(r'/tacare/job/\d+/profile/\d+',path) or
            path.startswith('/tuhoso/history/'))
        if retired:
            raise NotFound()
        return super()._pre_dispatch(rule,arguments)
