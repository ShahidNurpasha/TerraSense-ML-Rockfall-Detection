import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app

class VercelPathFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        debug_info = {
            k: str(v) for k, v in environ.items()
            if any(w in k.upper() for w in ('PATH', 'URI', 'URL', 'MATCH', 'ROUTE', 'VERCEL', 'ORIGINAL', 'FORWARD', 'REQUEST'))
        }

        def custom_start_response(status, response_headers, exc_info=None):
            response_headers.append(('X-Debug-Vercel-Keys', ','.join(sorted(debug_info.keys()))[:200]))
            for k, v in list(debug_info.items())[:12]:
                clean_k = 'X-Env-' + k.replace('_', '-')[:30]
                clean_v = str(v).replace('\n', ' ')[:100]
                response_headers.append((clean_k, clean_v))
            return start_response(status, response_headers, exc_info)

        return self.wsgi_app(environ, custom_start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
app.debug = False
