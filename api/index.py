import os
import sys
import json

# Ensure the root project directory is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app

class VercelPathFixMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get('QUERY_STRING', '')
        if 'dump_environ=1' in query_string:
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            dump = {k: str(v) for k, v in environ.items() if not k.startswith('wsgi.')}
            return [json.dumps(dump, indent=2).encode('utf-8')]

        matched = (
            environ.get('HTTP_X_MATCHED_PATH')
            or environ.get('x-matched-path')
            or environ.get('HTTP_X_FORWARDED_PATH')
        )
        if matched:
            environ['PATH_INFO'] = matched
        else:
            path_info = environ.get('PATH_INFO', '')
            if path_info in ('/api/index', '/api/index/'):
                environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[len('/api/index'):]

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelPathFixMiddleware(app.wsgi_app)
app.debug = False
