from flask import Request
from flask_sqlalchemy.record_queries import get_recorded_queries


def register_request_handlers(app):
    @app.after_request
    def query_profiler(response):
        for q in get_recorded_queries():
            if q.duration >= app.config['GREYBOOK_SLOW_QUERY_THRESHOLD']:
                app.logger.warning(
                    'Slow query: Duration: ' f'{q.duration:f}s\n Context: {q.context}\nQuery: {q.statement}\n'
                )
        return response


class CustomRequest(Request):
    @property
    def full_path(self):
        return super().full_path.rstrip('?')
