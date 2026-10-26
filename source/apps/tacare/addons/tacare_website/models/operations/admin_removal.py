"""Admin removal policy. Shared by the Kho and Tủ controllers; no schema changes."""
from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import SQL

KINDS = {'job': ('hr.job', 'tin việc làm', '/kvl/manage'),
         'profile': ('tacare.profile', 'hồ sơ', '/tuhoso/profiles?scope=all'),
         'service': ('care.profile.capability', 'công việc nhận làm', '/tuhoso/profiles?scope=all')}


def check_admin(actor, record=None):
    if not actor.active or not actor.has_group('base.group_system'):
        raise AccessError('Chỉ quản trị hệ thống được xóa bản ghi.')
    if record and record.company_id not in actor.company_ids:
        raise AccessError('Bản ghi nằm ngoài các công ty bạn được phép quản lý.')


def plan_removal(record, actor):
    record.ensure_one()
    check_admin(actor, record)
    kind = next((k for k, v in KINDS.items() if v[0] == record._name), None)
    if not kind:
        raise ValidationError('Loại bản ghi không hỗ trợ thao tác này.')
    dependencies = []
    env = record.env
    references = []
    if kind == 'service':
        references.append(('care.work.participation', 'capability_id', 'lượt thực hiện công việc'))
    if kind in ('job', 'profile'):
        field = 'job_id' if kind == 'job' else 'profile_id'
        references += [('tacare.connection', field, 'kết nối'),
                       ('care.match.session', field, 'phiên đối chiếu'),
                       ('care.match.input', field, 'đầu vào đối chiếu')]
        references += ([('hr.applicant', 'job_id', 'hồ sơ ứng tuyển'), ('hr.employee', 'job_id', 'nhân sự'),
                        ('care.job.revision', 'job_id', 'phiên bản tin')] if kind == 'job' else
                       [('care.document', 'profile_id', 'tài liệu'), ('care.ocr.job', 'profile_id', 'bản ghi xử lý tài liệu')])
    for model, field, label in references:
        count = env[model].sudo().with_context(active_test=False).search_count([(field, '=', record.id)])
        if count:
            dependencies.append('%s %s' % (count, label))
    return {'kind': kind, 'label': KINDS[kind][1], 'archive': bool(dependencies),
            'dependencies': dependencies,
            'title': record.profile_title or record.name if kind == 'profile' else record.title if kind == 'service' else record.name}


def remove_record(record, actor):
    """Permanently delete unlinked content; retain linked history out of the library."""
    check_admin(actor, record)
    record.env.cr.execute(SQL('SELECT id FROM %s WHERE id = %s FOR UPDATE', SQL.identifier(record._table), record.id))
    record.invalidate_recordset()
    plan = plan_removal(record, actor)
    kind = plan['kind']
    if kind == 'profile' and record.status == 'archived' or kind in ('job', 'service') and not record.active:
        raise ValidationError('Bản ghi đã được gỡ. Vui lòng tải lại danh sách.')
    record.env['care.audit.event'].sudo().create({'company_id': record.company_id.id,
        'actor_user_id': actor.id, 'action': 'admin.%s.%s' % (kind, 'removed' if plan['archive'] else 'deleted'),
        'target_model': record._name, 'target_res_id': record.id,
        'changes': {'retained_history': plan['archive'], 'dependencies': plan['dependencies']}})
    if plan['archive']:
        if kind == 'job':
            record.write({'tacare_status': 'closed', 'is_published': False, 'care_matching_enabled': False, 'active': False})
        elif kind == 'service':
            record.write({'active': False, 'flex_state': 'paused'})
        else:
            record.write({'status': 'archived', 'visible': False, 'scope': 'private', 'share_contact': False})
            record.capability_ids.write({'active': False, 'flex_state': 'paused'})
            record.env['care.consent'].sudo().search([('profile_id', '=', record.id), ('state', '=', 'granted')]).write({
                'state': 'revoked', 'revoked_at': fields.Datetime.now(), 'revoke_reason': 'Hồ sơ được quản trị gỡ khỏi hệ thống.'})
        if kind != 'service':
            field = 'job_id' if kind == 'job' else 'profile_id'
            record.env['tacare.connection'].sudo().search([(field, '=', record.id), ('status', '=', 'pending')]).write({
                'status': 'cancelled', 'decided_at': fields.Datetime.now()})
    else:
        record.unlink()
    return 'removed' if plan['archive'] else 'deleted'
