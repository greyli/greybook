from flask import render_template
from flask_wtf.csrf import CSRFError


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html', description=error.description), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', description=error.description), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', description=error.description), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return render_template('errors/400.html', description=error.description), 400
