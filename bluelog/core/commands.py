import os

import click
from flask import current_app
from sqlalchemy import select

from bluelog.core.extensions import db
from bluelog.models import Admin, Category


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building Bluelog, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = db.session.execute(select(Admin)).scalar()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = db.session.execute(select(Category)).scalar()
        if category is None:
            click.echo('Creating the default category...')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()

        upload_path = os.path.join(current_app.config['BLUELOG_UPLOAD_PATH'])
        if not os.path.exists(upload_path):
            click.echo('Creating the upload folder...')
            os.makedirs(upload_path)

        click.echo('Done.')

    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    @click.option('--reply', default=50, help='Quantity of replies, default is 50.')
    def fake(category, post, comment, reply):
        """Generate fake data."""
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, \
            fake_comments, fake_replies, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo(f'Generating {category} categories...')
        fake_categories(category)

        click.echo(f'Generating {post} posts...')
        fake_posts(post)

        click.echo(f'Generating {comment} comments...')
        fake_comments(comment)

        click.echo(f'Generating {reply} replies...')
        fake_replies(reply)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')
