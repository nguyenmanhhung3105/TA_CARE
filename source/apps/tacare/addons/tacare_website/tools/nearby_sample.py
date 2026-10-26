"""Manual LOCAL-only position trial on existing account-owned records.

Run in Odoo shell after backup: apply(env). No install hook, new records or
consent grants; never overwrite a point already selected by a user.
"""
import random


def apply(env):
    if env.cr.dbname != 'tacare_local':
        raise RuntimeError('Only tacare_local is authorized')
    # Approximate city reference points for artificial positions, not addresses.
    centers = {'HCM': (10.7769, 106.7009), 'SG': (10.7769, 106.7009),
               'HN': (21.0285, 105.8542), 'DN': (16.0544, 108.2022),
               'CT': (10.0452, 105.7469), 'HP': (20.8449, 106.6881),
               'LD': (11.9404, 108.4583)}
    changed = {}
    domains = {
        'hr.job': [('care_opportunity_kind', '=', 'flexible'), ('tacare_owner_user_id.active', '=', True)],
        'care.profile.capability': [('profile_id.user_id.active', '=', True), ('profile_id.status', '=', 'active')],
    }
    for model, domain in domains.items():
        records = env[model].sudo().search(domain + [('geo_set', '=', False), ('flex_mode', '!=', 'remote')])
        count = 0
        for record in records:
            region = record.flex_region_id
            code = (region.code or '').upper()
            center = centers.get(code)
            name = (region.name or '').casefold()
            if not center:
                center = next((value for key, value in [
                    ('hồ chí minh', centers['HCM']), ('hà nội', centers['HN']),
                    ('đà nẵng', centers['DN']), ('cần thơ', centers['CT']),
                    ('hải phòng', centers['HP']), ('lâm đồng', centers['LD'])] if key in name), None)
            if not center:
                continue  # Never silently place another province in HCMC.
            rng = random.Random('tacare-location-trial-20261026-%s-%s' % (model, record.id))
            record.write(dict(geo_set=True, geo_lat=round(center[0] + rng.uniform(-.035, .035), 6),
                geo_lon=round(center[1] + rng.uniform(-.035, .035), 6),
                geo_address='Điểm thử ngẫu nhiên · ' + region.name,
                geo_share=True, geo_sample=True))
            count += 1
        changed[model] = count
    env.cr.commit()
    print('LOCAL sample positions updated:', changed)
    return changed
