"""Meaningful security and preservation checks; mutations always roll back."""
from contextlib import ExitStack
from datetime import timedelta
import base64
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from werkzeug.exceptions import BadRequest, Forbidden, NotFound
from odoo.addons.tacare_website.sites.tacare.live_pairs import LivePairs
from odoo.addons.tacare_website.controllers.profiles import TacareProfiles

assert env.cr.dbname in ('tacare_ci', 'tacare_ci_upgrade')
assert env.cr._cnx.info.host == '/ci-socket'
fixture = json.loads((Path('/var/lib/odoo') / (env.cr.dbname + '-fixture.json')).read_text())
users = {kind: env['res.users'].sudo().browse(values['id']) for kind, values in fixture['accounts'].items()}
job = env['hr.job'].sudo().browse(fixture['job_id'])
profile = env['tacare.profile'].sudo().browse(fixture['profile_id'])
private = env['tacare.profile'].sudo().browse(fixture['private_profile_id'])
grants = env['care.consent'].sudo().browse(fixture['consent_ids'])


def denied(operation, errors=(AccessError, Forbidden, NotFound, BadRequest, ValidationError)):
    try:
        with env.cr.savepoint():
            operation()
    except errors:
        return
    raise AssertionError('Unauthorized operation was accepted')


def actor(user, params=None):
    stack = ExitStack()
    request = SimpleNamespace(env=env(user=user.id), params=params or {},
                              httprequest=SimpleNamespace(method='GET'))
    for name in ('controllers.shared.routes', 'controllers.profiles', 'controllers.flexible_work',
                 'sites.khovieclam.routes', 'sites.tuhoso.routes', 'sites.tacare.routes', 'sites.tacare.examples',
                 'sites.tacare.work_reviews', 'sites.tacare.live_pairs'):
        stack.enter_context(patch('odoo.addons.tacare_website.' + name + '.request', request))
    return stack


try:
    env.cr.execute('SELECT id, password FROM res_users WHERE id = ANY(%s) ORDER BY id',
                   [[account.id for account in users.values()]])
    assert hashlib.sha256(json.dumps(env.cr.fetchall()).encode()).hexdigest() == fixture['identity_digest']
    assert all(user.login == fixture['accounts'][kind]['login'] for kind, user in users.items())
    assert hashlib.sha256(base64.b64decode(job.flex_image)).hexdigest() == fixture['image_digest']
    assert job.tacare_owner_user_id == users['business'] and profile.user_id == private.user_id == users['person']
    assert job.care_opportunity_kind == 'flexible' and not profile.care_recruitment_enabled
    assert all(grant.state == 'granted' and grant.recipient_partner_id == job.tacare_owner_partner_id and
               grant.granted_by == users['person'] for grant in grants)
    for kind, user in users.items():
        for site in ('khovieclam', 'tuhoso', 'tacare'):
            assert user._tacare_can_access_host(site + '.localhost') == (kind != 'business' or site != 'tuhoso')
    assert not env['tacare.profile'].with_user(users['other']).search([('id', '=', profile.id)])
    # Published needs are intentionally discoverable; draft ownership stays private.
    draft = job.copy({'name': 'CI Private Draft', 'is_published': False, 'tacare_status': 'draft',
                      'tacare_owner_user_id': users['business'].id,
                      'tacare_owner_partner_id': job.tacare_owner_partner_id.id})
    assert not env['hr.job'].with_user(users['other']).search([('id', '=', draft.id)])
    denied(lambda: profile.with_user(users['person']).write({'name': 'Unauthorized direct write'}))
    denied(lambda: job.with_user(users['business']).write({'name': 'Unauthorized direct write'}))
    denied(lambda: profile.write({'care_recruitment_enabled': True}))
    denied(lambda: job.write({'care_opportunity_kind': 'recruitment'}))
    with actor(users['person']):
        denied(lambda: TacareProfiles()._flex_profile(create=True))
    with actor(users['other'], {'profile_id': profile.id}):
        denied(lambda: TacareProfiles()._flex_profile(create=True))

    controller = LivePairs()
    endpoint = lambda: LivePairs.live_pair_detail.original_endpoint(controller, job.id, profile.id)
    with patch.object(controller, '_render', side_effect=lambda template, **values: values):
        for kind in ('business', 'person'):
            with actor(users[kind]):
                pair = endpoint()['pair']
                assert pair['profile'] == profile
                assert pair['offer'].id == fixture['capability_id']
        for user in (users['other'], env.ref('base.public_user')):
            with actor(user):
                denied(endpoint)
        with actor(users['business']):
            denied(lambda: LivePairs.live_pair_detail.original_endpoint(controller, job.id, private.id))
        matching = grants.filtered(lambda grant: grant.purpose == 'matching')
        matching.state = 'revoked'
        with actor(users['business']):
            denied(endpoint)
        matching.write({'state': 'granted', 'valid_from': fields.Datetime.now() - timedelta(days=2),
                        'valid_until': fields.Datetime.now() - timedelta(days=1)})
        with actor(users['person']):
            denied(endpoint)

    session = env['care.auth.session']._start_for(users['person'])
    assert session._valid_for(users['person'].id) and not session._valid_for(users['other'].id)
    for model in ('care.auth.session', 'care.auth.handoff', 'care.work.participation', 'care.feedback'):
        denied(lambda: env[model].with_user(users['person']).search([]).read())
    session._revoke()
    assert not session._valid_for(users['person'].id)

    # An accepted connection is discussion; work and reviews have separate bilateral states.
    connection = env['tacare.connection'].sudo().create({'job_id': job.id, 'profile_id': profile.id,
        'type': 'application', 'sender_id': users['person'].id, 'receiver_id': users['business'].id,
        'status': 'accepted'})
    order = env['care.work.order'].sudo().create({'job_id': job.id})
    participation = env['care.work.participation'].sudo().create({'work_order_id': order.id,
        'connection_id': connection.id, 'profile_id': profile.id, 'capability_id': fixture['capability_id'],
        'buyer_partner_id': job.tacare_owner_partner_id.id, 'provider_user_id': users['person'].id,
        'terms': 'Synthetic CI agreed work scope, schedule and payment terms.'})
    assert participation.state == 'proposed'
    denied(lambda: participation._act(users['admin'], 'confirm'))
    denied(lambda: participation._review(users['business'], 5, 'CI premature review'))
    participation._act(users['business'], 'confirm')
    assert participation.state == 'proposed'
    participation._act(users['person'], 'confirm')
    assert participation.state == 'confirmed'
    participation._act(users['person'], 'start')
    participation._act(users['business'], 'complete')
    denied(lambda: participation._review(users['person'], 5, 'CI incomplete work'))
    participation._act(users['person'], 'complete')
    assert participation.state == 'completed'
    review = participation._review(users['business'], 5, 'CI synthetic completed work')
    assert not review.published
    participation._review(users['person'], 4, 'CI synthetic buyer feedback')
    assert review.published
    denied(lambda: participation._review(users['business'], 5, 'CI duplicate review'))
    denied(lambda: review.write({'rating': 1}))
    assert not env['ir.cron'].sudo().search_count([('active', '=', True)])
    assert not env['ir.mail_server'].sudo().search_count([('active', '=', True)])
    print('PASS native checks: credentials/owners retained; role/ACL/explicit-profile guards; real pair consent revocation/expiry; SSO revocation; bilateral work and immutable reviews')
finally:
    env.cr.rollback()
