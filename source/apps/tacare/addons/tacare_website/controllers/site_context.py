"""Shared product identity, role-aware switching and safe login return paths."""
from urllib.parse import urlsplit

from odoo.http import request


SITE_LABELS = {'khovieclam': 'Kho Việc Làm', 'tuhoso': 'Tủ Hồ Sơ', 'tacare': 'TA.CARE'}
ROLE_SITES = {'business': ('khovieclam', 'tacare'), 'candidate': ('khovieclam', 'tuhoso', 'tacare'),
              'admin': tuple(SITE_LABELS), 'pending': ()}


def safe_next(value, languages=('en', 'vi')):
    value = value if isinstance(value, str) else '/'
    if any(ord(c) < 32 for c in value) or '\\' in value:
        return '/'
    try:
        parsed = urlsplit(value)
    except ValueError:
        return '/'
    if parsed.scheme or parsed.netloc or not value.startswith('/') or value.startswith('//'):
        return '/'
    path = parsed.path
    first = path.split('/')[1] if path.startswith('/') else ''
    if first in languages:
        path = path[len(first) + 1:] or '/'
    if path != '/' and not path.startswith(('/kvl/', '/tuhoso/', '/tacare/')):
        return '/'
    return value


def site_context(site, urls):
    user = request.env.user
    public = user._is_public()
    role = 'admin' if user.has_group('base.group_system') else user.sudo().tacare_account_role
    allowed = ROLE_SITES.get(role, ()) if not public else tuple(SITE_LABELS)
    feedback = getattr(request, '_tacare_login_feedback', {})
    return {
        'site_labels': SITE_LABELS,
        'url_languages': request.website.language_ids.mapped('url_code'),
        'switch_sites': allowed,
        'access_guest': public or site not in allowed,
        'login_open': bool(feedback) or request.params.get('login') == '1',
        'login_error': feedback.get('error', ''),
        'login_value': feedback.get('login', ''),
        'login_next': safe_next(feedback.get('next') or request.params.get('next') or '/',
                                request.website.language_ids.mapped('url_code')),
        'login_role_notice': request.params.get('reason') == 'role' or not public and site not in allowed,
    }
