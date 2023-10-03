from flask import Flask

from greybook.views.admin import admin_bp
from greybook.views.auth import auth_bp
from greybook.views.blog import blog_bp
from greybook.core.extensions import bootstrap, db, login_manager, csrf, \
    ckeditor, mail, toolbar, migrate
from greybook.models import Admin, Post, Category, Comment
from greybook.settings import config
from greybook.core.commands import register_commands
from greybook.core.logging import register_logging
from greybook.core.templating import register_template_handlers
from greybook.core.request import register_request_handlers
from greybook.core.errors import register_errors


def create_app(config_name):
    app = Flask('greybook')
    app.config.from_object(config[config_name])

    # blueprints
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # extensions
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    toolbar.init_app(app)
    migrate.init_app(app, db)

    register_logging(app)
    register_commands(app)
    register_errors(app)
    register_template_handlers(app)
    register_request_handlers(app)

    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)

    return app
