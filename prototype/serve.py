"""Local-only SPA server for the TA.CARE prototype."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _route(self):
        path = self.path.split('?', 1)[0]
        if path.startswith(('/khovieclam', '/tuhoso', '/tacare')):
            self.path = '/index.html'

    def do_GET(self):
        self._route()
        return super().do_GET()

    def do_HEAD(self):
        self._route()
        return super().do_HEAD()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 4173), Handler)
    print('TA.CARE prototype: http://127.0.0.1:4173/')
    server.serve_forever()
