from flask import Flask

from greybook.blueprints.admin import admin_bp
from greybook.blueprints.auth import auth_bp
from greybook.blueprints.blog import blog_bp
from greybook.core.commands import register_commands
from greybook.core.errors import register_errors
from greybook.core.extensions import bootstrap, ckeditor, csrf, db, login_manager, mail, migrate, toolbar
from greybook.core.logging import register_logging
from greybook.core.request import CustomRequest, register_request_handlers
from greybook.core.shell import register_shell_handlers
from greybook.core.templating import register_template_handlers
from greybook.settings import config


def create_app(config_name):
    app = Flask('greybook')
    app.config.from_object(config[config_name])
    app.request_class = CustomRequest

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
