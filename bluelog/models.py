import os
import re
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, \
    Boolean, DateTime
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, url_for

from bluelog.extensions import db


class Admin(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    username = Column(String(20))
    password_hash = Column(String(128))
    blog_title = Column(String(60))
    blog_sub_title = Column(String(100))
    name = Column(String(30))
    about = Column(Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    posts = relationship('Post', back_populates='category')

    def delete(self):
        default_category = db.session.get(Category, 1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(60))
    body = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    can_comment = Column(Boolean, default=True)

    category_id = Column(Integer, ForeignKey('category.id'))

    category = relationship('Category', back_populates='posts')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')

    @property
    def reviewed_comments_count(self):
        return len([comment for comment in self.comments if comment.reviewed])

    def delete(self):
        upload_path = current_app.config['BLUELOG_UPLOAD_PATH']
        upload_url = url_for('blog.get_image', filename='')
        images = re.findall(rf'<img.*?src="{upload_url}(.*?)"', self.body)
        for image in images:
            file_path = os.path.join(upload_path, image)
            if os.path.exists(file_path):
                os.remove(file_path)


class Comment(db.Model):
    id = Column(Integer, primary_key=True)
    author = Column(String(30))
    email = Column(String(254))
    site = Column(String(255))
    body = Column(Text)
    from_admin = Column(Boolean, default=False)
    reviewed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    replied_id = Column(Integer, ForeignKey('comment.id'))
    post_id = Column(Integer, ForeignKey('post.id'))

    post = relationship('Post', back_populates='comments')
    replies = relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    replied = relationship('Comment', back_populates='replies', remote_side=[id])
    # Same with:
    # replies = relationship('Comment', backref=backref('replied', remote_side=[id]),
    # cascade='all,delete-orphan')


class Link(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    url = Column(String(255))
