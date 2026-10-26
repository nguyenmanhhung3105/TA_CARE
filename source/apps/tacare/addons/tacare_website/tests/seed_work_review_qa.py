"""Extend seed_seasonal_qa.py fixtures for the two work/review browser checks.

Run after seasonal_browser_check.cjs, then work_review_browser_check.cjs,
work_capacity_browser_check.cjs and cleanup_seasonal_qa.py. No install hook.
"""
import json
from pathlib import Path

assert env.cr.dbname == 'tacare_local'
receipt = Path('/var/lib/odoo/seasonal_qa.json')
qa = json.loads(receipt.read_text())
assert not qa.get('review_connection_id') and not qa.get('capacity_connections')
actors = {a['role']: env['res.users'].sudo().browse(a['user_id']).exists() for a in qa['accounts']}
assert len(actors) == 5 and all(u and u.login.startswith('qa-seasonal-') and u.login.endswith('@example.invalid') for u in actors.values())
client, provider = actors['client'], actors['provider']
source = env['hr.job'].sudo().browse(qa['client_job_id']).exists()
assert source and source.tacare_owner_user_id == client and not source.flex_demo_key
profile = env['tacare.profile'].sudo().browse(qa['profile_id'])
assert profile.user_id == provider and not profile.flex_demo_key
connection = env['tacare.connection'].sudo().create(dict(type='application', job_id=source.id,
    profile_id=profile.id, sender_id=provider.id, receiver_id=client.id, status='accepted'))
qa['review_connection_id'] = connection.id
qa['offer_id'] = profile.capability_ids[:1].id
assert qa['offer_id']
job = source.copy(dict(name='QA atomic last slot', tacare_owner_user_id=client.id,
    tacare_owner_partner_id=client.partner_id.id, website_id=source.website_id.id,
    tacare_status='published', is_published=True, no_of_recruitment=1, flex_demo_key=False))
order = env['care.work.order'].sudo().create({'job_id': job.id})
ids = []
for role in ('provider', 'outsider'):
    user = actors[role]
    p = env['tacare.profile'].sudo().search([('user_id', '=', user.id)], limit=1)
    if not p:
        p = env['tacare.profile'].sudo().create(dict(user_id=user.id, name='QA capacity participant'))
    cap = p.capability_ids[:1] or env['care.profile.capability'].sudo().create(dict(
        profile_id=p.id, title='QA capacity offer', flex_category_id=job.flex_category_id.id, flex_state='available'))
    c = env['tacare.connection'].sudo().create(dict(type='application', job_id=job.id,
        profile_id=p.id, sender_id=user.id, receiver_id=client.id, status='accepted'))
    env['care.work.participation'].sudo().create(dict(work_order_id=order.id, connection_id=c.id,
        profile_id=p.id, capability_id=cap.id, buyer_partner_id=client.partner_id.id,
        provider_user_id=user.id, terms='QA simultaneous confirmation, local test only.', provider_confirmed=True))
    ids.append(c.id)
qa.update(capacity_connections=ids, capacity_job_id=job.id)
receipt.write_text(json.dumps(qa))
env.cr.commit()
print('PASS local-only work/review QA fixtures; no real actors, credential output or ratings')
