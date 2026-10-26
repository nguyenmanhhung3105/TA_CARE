"""Two-party work confirmation and immutable, transaction-scoped reviews.

One initial occurrence per need. Acceptance of a connection never confirms work.
All website mutations use private methods after controller authorization; portal
users receive no direct model ACL, even for reading unpublished reviews.
"""
from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError


class ProfileSource(models.Model):
    _inherit = 'tacare.profile'
    source_job_id = fields.Many2one('hr.job', ondelete='set null', copy=False,
                                  string='Tin tham khảo khi tạo hồ sơ')


class WorkOrder(models.Model):
    _name = 'care.work.order'
    _description = 'Đầu việc đã thống nhất'
    job_id = fields.Many2one('hr.job', required=True, ondelete='restrict', index=True)
    company_id = fields.Many2one(related='job_id.company_id', store=True)
    participation_ids = fields.One2many('care.work.participation', 'work_order_id')
    _one_occurrence = models.Constraint('unique(job_id)', 'Tin đã có lượt thực hiện đầu tiên.')


class WorkParticipation(models.Model):
    _name = 'care.work.participation'
    _description = 'Lượt thực hiện công việc'
    _order = 'id desc'
    work_order_id = fields.Many2one('care.work.order', required=True, ondelete='restrict')
    connection_id = fields.Many2one('tacare.connection', required=True, ondelete='restrict', index=True)
    company_id = fields.Many2one(related='work_order_id.company_id', store=True)
    job_id = fields.Many2one(related='work_order_id.job_id', store=True)
    profile_id = fields.Many2one('tacare.profile', required=True, ondelete='restrict')
    capability_id = fields.Many2one('care.profile.capability', required=True, ondelete='restrict')
    buyer_partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict')
    provider_user_id = fields.Many2one('res.users', required=True, ondelete='restrict')
    terms = fields.Text(required=True, string='Phạm vi, lịch và tiền công đã thống nhất')
    buyer_confirmed = fields.Boolean()
    provider_confirmed = fields.Boolean()
    buyer_completed = fields.Boolean()
    provider_completed = fields.Boolean()
    state = fields.Selection([
        ('proposed', 'Chờ hai bên xác nhận nhận việc'), ('confirmed', 'Đã chốt người làm'),
        ('in_progress', 'Đang thực hiện'), ('completion_pending', 'Chờ xác nhận hoàn thành'),
        ('completed', 'Hai bên đã xác nhận hoàn thành'), ('disputed', 'Có bất đồng'),
        ('cancelled', 'Đã hủy')], default='proposed', required=True)
    completed_at = fields.Datetime()
    issue_note = fields.Text()
    feedback_ids = fields.One2many('care.feedback', 'participation_id')
    _unique_connection = models.Constraint('unique(connection_id)', 'Kết nối đã có lượt thực hiện.')
    _unique_provider = models.Constraint('unique(work_order_id, provider_user_id)', 'Người này đã có lượt thực hiện cho đầu việc.')

    @api.constrains('connection_id', 'work_order_id', 'profile_id', 'capability_id', 'buyer_partner_id', 'provider_user_id')
    def _check_parties(self):
        for p in self:
            c = p.connection_id
            if c.status != 'accepted' or c.job_id.care_opportunity_kind != 'flexible' or c.job_id != p.job_id or c.profile_id != p.profile_id or \
                    p.capability_id.profile_id != p.profile_id or p.provider_user_id != p.profile_id.user_id or \
                    p.capability_id.category_id != p.job_id.flex_category_id or \
                    p.buyer_partner_id != c.organization_id or p.provider_user_id == c.job_id.tacare_owner_user_id or \
                    p.provider_user_id.partner_id.commercial_partner_id == p.buyer_partner_id.commercial_partner_id:
                raise ValidationError('Hai bên, hồ sơ và việc nhận làm không đúng kết nối đã trao đổi.')

    def _side(self, actor):
        self.ensure_one()
        if not actor.active or self.company_id not in actor.company_ids:
            raise AccessError('Lượt thực hiện ngoài phạm vi tài khoản.')
        if actor == self.provider_user_id and (actor.tacare_account_role == 'candidate' or actor.has_group('base.group_system')):
            return 'provider'
        if actor.tacare_account_role == 'business':
            members = self.env['care.org.member'].sudo().search([('user_id', '=', actor.id)])
            valid = members.filtered(lambda m: m.company_id == self.company_id and
                m.organization_id == self.buyer_partner_id and m.state == 'active' and
                (m.role in ('owner', 'recruiter') or m.can_handle_candidates))
            if valid or not members and actor.partner_id.commercial_partner_id == self.buyer_partner_id:
                return 'buyer'
        elif actor == self.job_id.tacare_owner_user_id:
            return 'buyer'
        raise AccessError('Chỉ hai bên tham gia được xác nhận hoặc đánh giá.')

    def _lock(self):
        self.ensure_one()
        # Same lock order for every transition: need, then participant.
        self.env.cr.execute('SELECT id FROM hr_job WHERE id=%s FOR UPDATE', [self.job_id.id])
        self.env.cr.execute('SELECT id FROM care_work_participation WHERE id=%s FOR UPDATE', [self.id])
        self.job_id.invalidate_recordset()
        self.invalidate_recordset()

    def _act(self, actor, action, note=''):
        self._lock()
        side = self._side(actor)
        vals = {}
        if action == 'confirm' and self.state == 'proposed':
            if self[side + '_confirmed']:
                raise ValidationError('Bạn đã xác nhận nhận việc.')
            vals[side + '_confirmed'] = True
            if self.buyer_confirmed or side == 'buyer':
                if self.provider_confirmed or side == 'provider':
                    if self.job_id.tacare_status != 'published' or not self.job_id.is_published or \
                            self.job_id.tacare_deadline and self.job_id.tacare_deadline < fields.Date.today():
                        raise ValidationError('Tin không còn mở để chốt người làm.')
                    occupied = self.sudo().search_count([('job_id', '=', self.job_id.id),
                        ('id', '!=', self.id), ('state', 'not in', ['proposed', 'cancelled'])])
                    if occupied >= self.job_id.no_of_recruitment:
                        raise ValidationError('Đầu việc đã đủ người nhận làm.')
                    vals['state'] = 'confirmed'
        elif action == 'start' and self.state == 'confirmed':
            vals['state'] = 'in_progress'
        elif action == 'complete' and self.state in ('in_progress', 'completion_pending'):
            if self[side + '_completed']:
                raise ValidationError('Bạn đã xác nhận hoàn thành; đang chờ bên còn lại.')
            vals[side + '_completed'] = True
            vals['state'] = 'completion_pending'
            if (self.buyer_completed or side == 'buyer') and (self.provider_completed or side == 'provider'):
                vals.update(state='completed', completed_at=fields.Datetime.now())
        elif action == 'dispute' and self.state in ('confirmed', 'in_progress', 'completion_pending'):
            if not 10 <= len(note.strip()) <= 2000:
                raise ValidationError('Nêu bất đồng từ 10 đến 2.000 ký tự.')
            vals.update(state='disputed', issue_note=note.strip())
        elif action == 'cancel' and self.state in ('proposed', 'confirmed'):
            vals.update(state='cancelled')
        else:
            raise ValidationError('Thao tác không phù hợp trạng thái hiện tại. Hãy tải lại trang.')
        self.write(vals)
        self.env['care.audit.event'].sudo().create(dict(company_id=self.company_id.id,
            actor_user_id=actor.id, action='work.' + action, target_model=self._name,
            target_res_id=self.id, changes={'state': self.state, 'side': side}))

    def _review(self, actor, rating, comment):
        self._lock()
        side = self._side(actor)
        if self.state != 'completed' or not self.buyer_completed or not self.provider_completed:
            raise ValidationError('Chỉ đánh giá sau khi hai bên xác nhận hoàn thành.')
        if type(rating) is not int or not 1 <= rating <= 5 or not 5 <= len(comment.strip()) <= 2000:
            raise ValidationError('Chọn 1–5 sao và viết nhận xét từ 5 đến 2.000 ký tự.')
        if self.feedback_ids.filtered(lambda f: f.author_side == side):
            raise ValidationError('Mỗi bên chỉ đánh giá một lần cho lượt thực hiện.')
        review = self.env['care.feedback'].sudo().create(dict(company_id=self.company_id.id,
            author_user_id=actor.id, connection_id=self.connection_id.id, participation_id=self.id,
            author_side=side, rating=rating, reason=comment.strip()))
        self.env['care.audit.event'].sudo().create(dict(company_id=self.company_id.id,
            actor_user_id=actor.id, action='work.review.submitted', target_model='care.feedback',
            target_res_id=review.id, changes={'participation_id': self.id, 'side': side}))
        return review


class TransactionFeedback(models.Model):
    _inherit = 'care.feedback'
    participation_id = fields.Many2one('care.work.participation', ondelete='restrict', index=True)
    author_side = fields.Selection([('buyer', 'Bên cần người đánh giá'), ('provider', 'Người nhận việc đánh giá')])
    moderation = fields.Selection([('visible', 'Được công bố'), ('hidden', 'Đã ẩn')], default='visible', required=True)
    moderation_reason = fields.Char()
    published = fields.Boolean(compute='_compute_published')
    _one_review_side = models.Constraint('unique(participation_id, author_side)', 'Mỗi phía chỉ đánh giá một lần.')

    @api.depends('moderation', 'participation_id.state', 'participation_id.completed_at', 'participation_id.feedback_ids')
    def _compute_published(self):
        now = fields.Datetime.now()
        for r in self:
            p = r.participation_id
            r.published = bool(p and p.state == 'completed' and r.moderation == 'visible' and
                (len(p.feedback_ids) == 2 or p.completed_at and now >= p.completed_at + timedelta(days=14)))

    @api.constrains('participation_id', 'author_user_id', 'author_side', 'connection_id', 'result_id', 'reason')
    def _check_transaction_review(self):
        for r in self.filtered('participation_id'):
            p = r.participation_id
            if p.state != 'completed' or not p.buyer_completed or not p.provider_completed or \
                    r.connection_id != p.connection_id or r.result_id or r.company_id != p.company_id or \
                    r.author_side != p._side(r.author_user_id) or not 5 <= len((r.reason or '').strip()) <= 2000:
                raise ValidationError('Đánh giá không đúng lượt hoàn thành hoặc bên tham gia.')

    def write(self, vals):
        if self.filtered('participation_id'):
            if set(vals) - {'moderation', 'moderation_reason'}:
                raise ValidationError('Đánh giá đã gửi không thể sửa nội dung hoặc tác giả.')
            if not self.env.user.has_group('base.group_system'):
                raise AccessError('Chỉ quản trị được kiểm duyệt đánh giá.')
            if not (vals.get('moderation_reason') or '').strip():
                raise ValidationError('Cần lý do kiểm duyệt.')
            for r in self:
                self.env['care.audit.event'].sudo().create(dict(company_id=r.company_id.id,
                    actor_user_id=self.env.user.id, action='work.review.moderated',
                    target_model=self._name, target_res_id=r.id, reason=vals['moderation_reason']))
        return super().write(vals)

    def unlink(self):
        if self.filtered('participation_id'):
            raise ValidationError('Giữ đánh giá để đối soát; quản trị có thể ẩn kèm lý do.')
        return super().unlink()

    @api.model
    def _summary(self, profile=None, buyer=None):
        domain = [('participation_id.state', '=', 'completed')]
        if profile:
            domain += [('author_side', '=', 'buyer'), ('participation_id.profile_id', '=', profile.id)]
        elif buyer:
            domain += [('author_side', '=', 'provider'), ('participation_id.buyer_partner_id', '=', buyer.id)]
        else:
            return {'count': 0, 'average': False, 'items': []}
        reviews = self.sudo().search(domain, order='create_date desc,id desc').filtered('published')
        return {'count': len(reviews), 'average': sum(reviews.mapped('rating')) / len(reviews) if reviews else False,
                'items': reviews[:10]}


class JobCapacity(models.Model):
    _inherit = 'hr.job'
    care_participation_ids = fields.One2many('care.work.participation', 'job_id')
    care_remaining_slots = fields.Integer(compute='_compute_care_slots', store=True)

    @api.depends('no_of_recruitment', 'care_participation_ids.state')
    def _compute_care_slots(self):
        for job in self:
            used = len(job.care_participation_ids.filtered(lambda p: p.state not in ('proposed', 'cancelled')))
            job.care_remaining_slots = max(0, int(job.no_of_recruitment) - used)
