"""Owner-scoped location editing and consent-scoped nearby matching."""
import math

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.fields import Domain
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from ...geo_utils import approximate, cover, distance_km
from .live_pairs import LivePairs

GEO_INPUTS = {'geo_lat', 'geo_lon', 'geo_address', 'geo_share'}
ICONS = {'repair': 'hammer', 'cleaning': 'broom', 'cooking': 'cooking-pot',
         'garden': 'plant', 'farm': 'plant', 'loading': 'package',
         'tutoring': 'book-open', 'digital': 'laptop', 'pets': 'paw-print'}


def parse_location(values):
    lat, lon = (str(values.get(k) or '').strip() for k in ('geo_lat', 'geo_lon'))
    label = (values.get('geo_address') or '').strip()
    if len(label) > 1000:
        raise ValidationError('Địa chỉ đầy đủ tối đa 1.000 ký tự.')
    if bool(lat) != bool(lon):
        raise ValidationError('Điền cả vĩ độ và kinh độ, hoặc xóa cả hai.')
    try:
        latitude, longitude = float(lat or 0), float(lon or 0)
    except (ValueError, TypeError):
        raise ValidationError('Tọa độ không hợp lệ.')
    if not all(math.isfinite(v) for v in (latitude, longitude)):
        raise ValidationError('Tọa độ phải là số hữu hạn.')
    if lat and not (8 <= latitude <= 24 and 102 <= longitude <= 110):
        raise ValidationError('Chọn vị trí trong Việt Nam (8–24°B, 102–110°Đ).')
    shared = values.get('geo_share') == 'on'
    if shared and not lat:
        raise ValidationError('Chọn vị trí trước khi chia sẻ khu vực.')
    return dict(geo_set=bool(lat), geo_lat=latitude, geo_lon=longitude,
                geo_address=label if lat else False, geo_share=shared, geo_sample=False)


class Nearby(LivePairs):
    def _nearby_sources(self, view):
        self._flex_user()
        if view == 'hire':
            jobs = self._hire_matching_data()[0]
            # Viewing matches and editing a need are separate capabilities.
            return jobs
        if view != 'receive' or self._role() == 'business':
            raise Forbidden('Chọn hướng kết nối phù hợp với tài khoản.')
        return request.env['care.profile.capability'].sudo().search([
            ('profile_id.user_id', '=', self._user().id), ('profile_id.status', '=', 'active'),
            ('profile_id.care_recruitment_enabled', '=', False),
            ('company_id', 'in', self._user().company_ids.ids),
            ('active', '=', True), ('flex_state', '=', 'available')], order='id desc')

    def _nearby_payload(self, view, source_id=0, radius=10):
        if radius not in (2, 5, 10, 20, 50):
            raise BadRequest('Chọn bán kính 2, 5, 10, 20 hoặc 50 km.')
        sources = self._nearby_sources(view)
        source = sources.filtered(lambda r: r.id == source_id) if source_id else sources.filtered('geo_set')[:1] or sources[:1]
        if source_id and not source:
            raise NotFound()
        def label(r):
            return r.name if view == 'hire' else '%s · %s' % (r.profile_id.profile_title or r.profile_id.name, r.title)
        result = dict(view=view, sources=[dict(id=r.id, label=label(r), located=r.geo_set) for r in sources],
                      source=False, markers=[], radius=radius, missing_location=0)
        if not source:
            return result
        editable = view == 'receive' or self._role() == 'admin' or (
            source.tacare_owner_partner_id in self._authorized_organizations('manage') if self._role() == 'business'
            else source.tacare_owner_user_id == self._user())
        result['source'] = dict(id=source.id, label=label(source), located=source.geo_set,
            point=[source.geo_lat, source.geo_lon] if source.geo_set else False,
            address=source.geo_address or '', shared=source.geo_share, sample=source.geo_sample,
            editable=bool(editable), remote=source.flex_mode == 'remote',
            edit_url=self._urls()['khovieclam' if view == 'hire' else 'tuhoso'] +
                ('kvl/flexible/%s/edit' if view == 'hire' else 'tuhoso/work/%s/edit') % source.id)
        if not source.geo_set or source.flex_mode == 'remote':
            return result
        prefixes = cover(source.geo_lat, source.geo_lon, radius)
        spatial = list(Domain.OR([Domain('geo_hash', '=like', p + '%') for p in prefixes]))
        geo_domain = [('geo_set', '=', True), ('geo_share', '=', True), ('flex_mode', '!=', 'remote')]
        if view == 'hire':
            matches = self._hire_matching_data(source.id)[2]
            offer_ids = [reason.get('capability_id', 0) for _, reason in matches]
            nearby = request.env['care.profile.capability'].sudo().search(
                [('id', 'in', offer_ids)] + geo_domain + spatial)
            pairs = [(source, profile, reason, nearby.filtered(lambda o: o.id == reason.get('capability_id')))
                     for profile, reason in matches]
        else:
            # The selected offer must be the actual winning capability.
            # Never locate a different offer using this one's coordinates.
            if not source.geo_share:
                return result
            nearby = request.env['hr.job'].sudo().search(self._job_domain() + geo_domain + spatial)
            pairs = [(job, source.profile_id, reason, job if job in nearby else False)
                     for job, reason in self._receive_matching_data(source.profile_id)
                     if reason.get('capability_id') == source.id and
                     source.profile_id in self._visible_profiles(job.tacare_owner_partner_id)]
        for job, profile, reason, target in pairs:
            if job.company_id not in self._user().company_ids:
                continue
            if not target:
                continue
            if distance_km(source.geo_lat, source.geo_lon, target.geo_lat, target.geo_lon) > radius:
                continue
            pair = self._live_pair(job, profile, reason, view)
            if not pair:
                continue
            category = job.flex_category_id
            result['markers'].append(dict(
                key='%s-%s' % (job.id, profile.id), point=approximate(target.geo_lat, target.geo_lon),
                title=profile.name if view == 'hire' else job.name,
                subtitle=pair['offer'].title if view == 'hire' else job.tacare_owner_partner_id.name,
                category=category.name, icon=ICONS.get(category.code, 'map-pin'),
                price=target._flex_price_label(), region=target.flex_region_id.name or 'Việt Nam',
                url=pair['detail_url'], sample=bool(source.geo_sample or target.geo_sample)))
        # Preserve existing matching order, not a distance/rating rank.
        result['markers'] = result['markers'][:60]
        return result

    @http.route('/tacare/nearby/data', auth='user', website=True, methods=['GET'])
    def nearby_data(self, view='hire', source_id='0', radius='10', **kw):
        self._flex_user()
        try:
            payload = self._nearby_payload(view, int(source_id), int(radius))
            if not int(source_id) and not payload['markers']:
                for source in payload['sources']:
                    if source['located'] and source['id'] != (payload['source'] or {}).get('id'):
                        candidate = self._nearby_payload(view, source['id'], int(radius))
                        if candidate['markers']:
                            payload = candidate
                            break
        except (ValueError, TypeError):
            raise BadRequest('Bộ lọc vị trí không hợp lệ.')
        return request.make_json_response(payload, headers=[('Cache-Control', 'private, no-store')])
