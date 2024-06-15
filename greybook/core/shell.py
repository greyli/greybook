from greybook.core.extensions import db
from greybook.models import Admin, Category, Comment, Post


def register_shell_handlers(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Admin=Admin, Post=Post, Category=Category, Comment=Comment)
