from flask_login import current_user
from sqlalchemy import func, select

from greybook.core.extensions import db
from greybook.models import Admin, Category, Comment, Link


def register_template_handlers(app):
    @app.context_processor
    def make_template_context():
        admin = db.session.scalar(select(Admin))
        categories = db.session.scalars(select(Category).order_by(Category.name)).all()
        links = db.session.scalars(select(Link).order_by(Link.name)).all()

        if current_user.is_authenticated:
            stmt = select(func.count(Comment.id)).filter_by(reviewed=False)
            unread_comments = db.session.scalars(stmt).one()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)
