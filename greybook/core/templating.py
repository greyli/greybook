from flask_login import current_user
from sqlalchemy import func, select

from greybook.core.extensions import db
from greybook.models import Admin, Category, Comment, Link


def register_template_handlers(app):
    @app.context_processor
    def make_template_context():
        admin = db.session.execute(select(Admin)).scalar()
        categories = db.session.execute(select(Category).order_by(Category.name)).scalars().all()
        links = db.session.execute(select(Link).order_by(Link.name)).scalars().all()

        if current_user.is_authenticated:
            unread_comments = (
                db.session.execute(select(func.count(Comment.id)).filter_by(reviewed=False)).scalars().one()
            )
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)
