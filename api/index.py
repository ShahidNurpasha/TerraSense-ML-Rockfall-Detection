import os
import sys
import urllib.parse

# Ensure the root project directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app

class VercelPathFixMiddleware:
    """
    WSGI Middleware to extract original request path and clean query string
    from Vercel rewrites (destination: /api/index?__vercel_path=$1).
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get('QUERY_STRING', '')
        if '__vercel_path' in qs:
            params = urllib.parse.parse_qs(qs, keep_blank_values=True)
            path_val = params.pop('__vercel_path', [''])[0]
            if path_val:
                environ['PATH_INFO'] = '/' + path_val.lstrip('/')
            else:
                environ['PATH_INFO'] = '/'
            environ['QUERY_STRING'] = urllib.parse.urlencode(params, doseq=True)
        else:
            path_info = environ.get('PATH_INFO', '')
            if path_info in ('/api/index', '/api/index/'):
                environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[len('/api/index'):]

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
app.debug = False
