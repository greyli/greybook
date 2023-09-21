import random
from datetime import datetime

from faker import Faker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func

from bluelog.core.extensions import db
from bluelog.models import Admin, Category, Post, Comment, Link

fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='Bluelog',
        blog_sub_title="No, I'm the real thing.",
        name='Mima Kirigoe',
        about='Um, l, Mima Kirigoe, had a fun time as a member of CHAM...'
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    i = 0
    while i < count - 1:
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for _ in range(count):
        category_count = db.session.execute(select(func.count(Category.id))).scalars().one()
        created_date = fake.date_time_between_dates(
            datetime_start=datetime(2010, 1, 1),
            datetime_end=datetime(2020, 1, 1)
        )
        updated_date = fake.date_time_between_dates(
            datetime_start=datetime(2020, 1, 2),
            datetime_end=datetime(2022, 12, 31)
        )
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=db.session.get(Category, random.randint(1, category_count)),
            created_at=created_date,
            updated_at=updated_date
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for _ in range(count):
        post_count = db.session.execute(select(func.count(Post.id))).scalars().one()
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            created_at=fake.date_time_this_year(before_now=True, after_now=False),
            reviewed=random.choice([True, True, True, True, False]),
            from_admin=random.choice([False, False, False, False, True]),
            post=db.session.get(Post, random.randint(1, post_count))
        )
        if comment.from_admin:
            comment.reviewed = True
        db.session.add(comment)
    db.session.commit()


def fake_replies(count=50):
    for _ in range(count):
        comment_count = db.session.execute(select(func.count(Comment.id))).scalars().one()
        replied = db.session.get(Comment, random.randint(1, comment_count))
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            created_at=fake.date_time_this_year(before_now=False, after_now=True),
            reviewed=True,
            replied=replied,
            post=replied.post
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():
    twitter = Link(name='Twitter', url='https://twitter.com')
    facebook = Link(name='Facebook', url='https://facebook.com')
    linkedin = Link(name='LinkedIn', url='https://linkedin.com')
    google = Link(name='Google', url='https://google.com')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()
