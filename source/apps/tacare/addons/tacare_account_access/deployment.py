"""Exact product origins; UAT is enabled only by its process environment.

An unset environment preserves the existing local/production deployments. It
never accepts UAT hosts. Unknown settings fail at startup rather than silently
using a different environment's login or SSO destinations.
"""
import os
from urllib.parse import urlsplit


ENVIRONMENT = os.environ.get('TACARE_ENVIRONMENT', 'default')
NETWORKS = {
    'local': {site: f'http://{site}.localhost:8069'
              for site in ('khovieclam', 'tuhoso', 'tacare')},
    'production': {'khovieclam': 'https://khovieclam.vn',
                   'tuhoso': 'https://tuhoso.com', 'tacare': 'https://tacare.vn'},
    'uat': {'khovieclam': 'https://uat.khovieclam.vn',
            'tuhoso': 'https://uat.tuhoso.com', 'tacare': 'https://uat.tacare.vn'},
}
if ENVIRONMENT not in ('default', *NETWORKS):
    raise ValueError('Invalid TACARE_ENVIRONMENT')
ORIGINS = ({key: NETWORKS[key] for key in ('local', 'production')}
           if ENVIRONMENT == 'default' else {ENVIRONMENT: NETWORKS[ENVIRONMENT]})


def hostname(value):
    value = (value or '').strip()
    if not value:
        return ''
    return (urlsplit(value if '://' in value else '//' + value).hostname or '').lower().rstrip('.')


def origin_info(value):
    host = hostname(value)
    for network, sites in ORIGINS.items():
        for site, origin in sites.items():
            known = urlsplit(origin).hostname
            if host == known:
                return network, site, origin
            if network == 'production' and host == 'www.' + known:
                return network, site, 'https://' + host
    return None


def product_urls(value):
    info = origin_info(value)
    if not info:
        raise ValueError('Unrecognized product host')
    return {site: origin + '/' for site, origin in ORIGINS[info[0]].items()}


ROLE_SITES = {'business': ('khovieclam', 'tacare'),
              'candidate': ('khovieclam', 'tuhoso', 'tacare'), 'pending': ()}
ROLE_HOSTS = {}
for role, allowed in ROLE_SITES.items():
    hosts = set()
    for network, sites in ORIGINS.items():
        for site in allowed:
            host = hostname(sites[site])
            hosts.add(host)
            if network == 'production':
                hosts.add('www.' + host)
    ROLE_HOSTS[role] = hosts
