import random
from datetime import datetime

from faker import Faker
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from greybook.core.extensions import db
from greybook.models import Admin, Category, Comment, Link, Post

fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
        password='greybook',
        blog_title='Greybook',
        blog_sub_title='Just some random thoughts',
        name='Grey Li',
        about='This is an example Flask project for <a href="https://helloflask.com/book/4/">this book</a>.',
    )
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    i = 0
    while i < count - 1:
        category = Category(name=fake.word().title())
        db.session.add(category)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for _ in range(count):
        category_count = db.session.scalars(select(func.count(Category.id))).one()
        created_date = fake.date_time_between_dates(
            datetime_start=datetime(2010, 1, 1), datetime_end=datetime(2020, 1, 1)
        )
        updated_date = fake.date_time_between_dates(
            datetime_start=datetime(2020, 1, 2), datetime_end=datetime(2022, 12, 31)
        )
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=db.session.get(Category, random.randint(1, category_count)),
            created_at=created_date,
            updated_at=updated_date,
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for _ in range(count):
        post_count = db.session.scalars(select(func.count(Post.id))).one()
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            created_at=fake.date_time_this_year(before_now=True, after_now=False),
            reviewed=random.choice([True, True, True, True, False]),
            from_admin=random.choice([False, False, False, False, True]),
            post=db.session.get(Post, random.randint(1, post_count)),
        )
        if comment.from_admin:
            comment.author = 'Grey Li'
            comment.email = 'admin@example.com'
            comment.site = 'https://helloflask.com'
            comment.reviewed = True
        db.session.add(comment)
    db.session.commit()


def fake_replies(count=50):
    for _ in range(count):
        comment_count = db.session.scalars(select(func.count(Comment.id))).one()
        replied = db.session.get(Comment, random.randint(1, comment_count))
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            created_at=fake.date_time_this_year(before_now=False, after_now=True),
            reviewed=True,
            replied=replied,
            post=replied.post,
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():
    helloflask = Link(name='HelloFlask', url='https://helloflask.com')
    github = Link(name='GitHub', url='https://github.com/greyli')
    twitter = Link(name='Twitter', url='https://twitter.com/greylihui')
    linkedin = Link(name='LinkedIn', url='https://www.linkedin.com/in/greyli/')
    google = Link(name='Stack Overflow', url='https://stackoverflow.com/users/5511849/grey-li')
    db.session.add_all([helloflask, github, twitter, linkedin, google])
    db.session.commit()
