"""Read/rollback-only checks for the owner-authorized multi-profile map trial."""
import json
from pathlib import Path
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import patch

from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.tacare_website.geo_utils import approximate
from odoo.addons.tacare_website.sites.tacare.nearby import Nearby
from odoo.addons.tacare_website.tools.map_test_profiles import PREFIX, account, prepare

assert env.cr.dbname == 'tacare_local'
receipt=json.loads(Path('/var/lib/odoo/map_test_accounts_20261027/map_test_receipt_20261027.json').read_text())
controller=Nearby()
modules=('controllers.shared.routes','controllers.profiles','controllers.flexible_work',
         'sites.khovieclam.routes','sites.tacare.routes','sites.tacare.examples',
         'sites.tacare.work_reviews','sites.tacare.live_pairs','sites.tacare.nearby')


def actor(user):
    mocked=SimpleNamespace(env=env(user=user.id,context={**env.context,'allowed_company_ids':user.company_ids.ids}),
        params={},httprequest=SimpleNamespace(method='GET',host='tacare.localhost:8069'))
    stack=ExitStack()
    for name in modules:
        stack.enter_context(patch('odoo.addons.tacare_website.'+name+'.request',mocked))
    return stack


try:
    profiles=env['tacare.profile'].sudo().search([('flex_demo_key','=like',PREFIX+'%')])
    assert len(profiles)==27 and set(profiles.ids)=={r['profile_id'] for r in receipt['created']}
    assert len(profiles.mapped('user_id'))==3 and len(profiles.capability_ids)==27
    assert len(profiles.capability_ids.filtered('geo_set'))==24
    assert len(profiles.capability_ids.filtered(lambda o:o.flex_mode=='remote'))==3
    assert prepare(env)['additional_profiles']==0
    for p in profiles:
        assert p.scope=='members' and p.visible and not p.care_recruitment_enabled
        assert p.name==p.user_id.name
        grants=p.consent_ids
        assert len(grants)==2 and set(grants.mapped('purpose'))=={'discovery','matching'}
        assert all(g.recipient_kind=='organization' and g.recipient_partner_id==p.source_job_id.tacare_owner_partner_id
            and g.granted_by==p.user_id and g.valid_until and g.is_current(g.purpose,g.recipient_partner_id) for g in grants)
        assert not p.share_contact
    for code in sorted({r['code'] for r in receipt['created']}):
        rows=[r for r in receipt['created'] if r['code']==code]
        assert len(rows)==3
        offered=env['care.profile.capability'].sudo().browse([r['offer_id'] for r in rows])
        assert len(set(offered.mapped('title')))==3 and len(set(offered.mapped('description')))==3
        assert len(set(offered.mapped('flex_rate_min')))==3
        job=env['hr.job'].sudo().browse(rows[0]['job_id'])
        if code=='digital':
            for o in offered:
                with actor(o.profile_id.user_id):
                    data=controller._nearby_payload('receive',o.id,10)
                    assert data['source']['remote'] and not data['markers']
            continue
        with actor(job.tacare_owner_user_id):
            for radius,expected in [(2,1),(5,2),(10,3)]:
                data=controller._nearby_payload('hire',job.id,radius)
                own=[m for m in data['markers'] if int(m['key'].split('-')[1]) in {r['profile_id'] for r in rows}]
                assert len(own)==expected,(code,radius,len(own))
                if radius==10:
                    assert len({tuple(m['point']) for m in own})==3
                    for m in own:
                        o=offered.filtered(lambda o:o.profile_id.id==int(m['key'].split('-')[1]))
                        assert m['point']==approximate(o.geo_lat,o.geo_lon)
                        assert not {'address','email','geo_lat','geo_lon'} & set(m)
        for o in offered:
            with actor(o.profile_id.user_id):
                data=controller._nearby_payload('receive',o.id,10)
                assert str(job.id)+'-'+str(o.profile_id.id) in [m['key'] for m in data['markers']]
    sample=profiles.filtered(lambda p:p.capability_ids.flex_category_id.code=='cleaning')[:1]
    job=sample.source_job_id
    class RollbackProbe(Exception): pass
    try:
        with env.cr.savepoint():
            sample.consent_ids.write({'state':'revoked'})
            with actor(job.tacare_owner_user_id):
                assert str(job.id)+'-'+str(sample.id) not in [m['key'] for m in controller._nearby_payload('hire',job.id,10)['markers']]
            raise RollbackProbe()
    except RollbackProbe:
        pass
    for user in [account(env,'provider_green'),env.ref('base.public_user')]:
        with actor(user):
            try:
                controller._flex_own('care.profile.capability',sample.capability_ids.id)
            except (Forbidden,NotFound):
                pass
            else:
                raise AssertionError('Foreign/private owner access succeeded')
    print('PASS 27 owner-linked profiles, 24 mapped/3 remote; unique scope/content/prices; 3 separate coarse cells per mapped profession; exact 2/5/10 km counts 1/2/3; bilateral actual matches; exact-org/time-bound discovery+matching only; no contact grant; revoke and foreign/guest denial; all probes rolled back')
finally:
    env.cr.rollback()
