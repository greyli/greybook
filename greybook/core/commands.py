import click
from flask import current_app
from sqlalchemy import select

from greybook.core.extensions import db
from greybook.models import Admin, Category


def register_commands(app):
    @app.cli.command('init-db')
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def init_db_command(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Dropped tables.')
        db.create_all()
        click.echo('Initialized the database.')

    @app.cli.command('init-blog')
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option(
        '--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.'
    )
    def init_blog_command(username, password):
        """Initialize the blog."""
        db.create_all()
        click.echo('Initialized the database.')

        admin = db.session.scalar(select(Admin))
        if admin is not None:
            admin.username = username
            admin.password = password
            click.echo('Updated the existing administrator account.')
        else:
            admin = Admin(
                username=username,
                password=password,
                blog_title='Blog Title',
                blog_sub_title='Blog Sub Title',
                name='Admin',
                about='Anything about you.',
            )
            db.session.add(admin)
            click.echo('Created the administrator account.')

        category = db.session.scalar(select(Category))
        if category is None:
            category = Category(name='Default')
            db.session.add(category)
            click.echo('Created the default category.')

        db.session.commit()

        upload_path = current_app.config['GREYBOOK_UPLOAD_PATH']
        if not upload_path.exists():
            upload_path.mkdir(parents=True, exist_ok=True)
            click.echo('Created the upload folder.')

    @app.cli.command('lorem')
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    @click.option('--reply', default=50, help='Quantity of replies, default is 50.')
    def lorem_command(category, post, comment, reply):
        """Generate fake data."""
        from greybook.lorem import fake_admin, fake_categories, fake_comments, fake_links, fake_posts, fake_replies

        db.drop_all()
        db.create_all()

        fake_admin()
        click.echo('Generated the administrator.')

        fake_categories(category)
        click.echo(f'Generated {category} categories.')

        fake_posts(post)
        click.echo(f'Generated {post} posts.')

        fake_comments(comment)
        click.echo(f'Generated {comment} comments.')

        fake_replies(reply)
        click.echo(f'Generated {reply} replies.')

        fake_links()
        click.echo('Generated links.')
