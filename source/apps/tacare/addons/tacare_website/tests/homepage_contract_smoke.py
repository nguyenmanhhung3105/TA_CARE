"""Check the homepage markers required by the production deploy HTTP probe.

Run after updating the local addon:
    python3 tests/homepage_contract_smoke.py
"""

from html.parser import HTMLParser
from urllib.request import urlopen


class HomepageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.wrap_classes = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id') == 'wrap':
            self.wrap_classes = set(attributes.get('class', '').split())


def check_homepages():
    markers = {
        'tacare': 'tc-hub',
        'khovieclam': 'tc-jobs',
        'tuhoso': 'tc-profiles',
    }
    for site, expected in markers.items():
        with urlopen(f'http://{site}.localhost:8069/', timeout=20) as response:
            assert response.status == 200, (site, response.status)
            parser = HomepageParser()
            parser.feed(response.read().decode('utf-8'))
        assert expected in parser.wrap_classes, (site, parser.wrap_classes)
        assert not (set(markers.values()) - {expected}) & parser.wrap_classes, site
        print(f'{site}: HTTP 200, {expected}')

    for site in markers:
        with urlopen(f'http://{site}.localhost:8069/web/login', timeout=20) as response:
            assert response.status == 200, (site, response.status)
            assert '<form' in response.read().decode('utf-8'), site
        print(f'{site} login: HTTP 200')


if __name__ == '__main__':
    check_homepages()
