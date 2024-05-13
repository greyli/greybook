from flask import Flask

from greybook.blueprints.admin import admin_bp
from greybook.blueprints.auth import auth_bp
from greybook.blueprints.blog import blog_bp
from greybook.core.extensions import bootstrap, db, login_manager, csrf, \
    ckeditor, mail, toolbar, migrate
from greybook.settings import config
from greybook.core.commands import register_commands
from greybook.core.logging import register_logging
from greybook.core.templating import register_template_handlers
from greybook.core.request import register_request_handlers
from greybook.core.errors import register_errors
from greybook.core.shell import register_shell_handlers


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
    register_shell_handlers(app)

    return app
