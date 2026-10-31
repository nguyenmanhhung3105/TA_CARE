"""Allowlisted browser configuration; never project a secret Mapbox token."""
import re


def browser_config(provider, token):
    token = (token or '').strip()
    if provider == 'mapbox' and re.fullmatch(r'pk\.[A-Za-z0-9_.-]{20,2000}', token):
        return {'provider': 'mapbox', 'token': token}
    return {'provider': 'openfreemap', 'token': ''}
