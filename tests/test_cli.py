from sqlalchemy import select, func

from greybook.models import Admin, Post, Category, Comment
from greybook.core.extensions import db
from tests import BaseTestCase


class CommandTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        db.drop_all()

    def test_initdb_command(self):
        result = self.cli_runner.invoke(args=['initdb'])
        self.assertIn('Initialized the database.', result.output)

    def test_initdb_command_with_drop(self):
        result = self.cli_runner.invoke(args=['initdb', '--drop'], input='y\n')
        self.assertIn(
            'This operation will delete the database, do you want to continue?',
            result.output
        )
        self.assertIn('Dropped tables.', result.output)

    def test_init_command(self):
        result = self.cli_runner.invoke(
            args=['init', '--username', 'grey', '--password', '123']
        )
        self.assertIn('Created the administrator account.', result.output)
        self.assertIn('Created the default category.', result.output)
        self.assertEqual(db.session.execute(select(func.count(Admin.id))).scalars().one(), 1)
        self.assertEqual(db.session.execute(select(Admin)).scalar().username, 'grey')
        self.assertEqual(db.session.execute(select(Category)).scalar().name, 'Default')

    def test_init_command_with_update(self):
        self.cli_runner.invoke(args=['init', '--username', 'grey', '--password', '123'])
        result = self.cli_runner.invoke(
            args=['init', '--username', 'new grey', '--password', '123']
        )
        self.assertIn('Updated the existing administrator account.', result.output)
        self.assertNotIn('Created the administrator account.', result.output)
        self.assertEqual(db.session.execute(select(func.count(Admin.id))).scalars().one(), 1)
        self.assertEqual(db.session.execute(select(Admin)).scalar().username, 'new grey')
        self.assertEqual(db.session.execute(select(Category)).scalar().name, 'Default')

    def test_fake_command(self):
        default_post_count = 50
        default_category_count = 10
        default_comment_count = 500
        default_reply_count = 50

        result = self.cli_runner.invoke(args=['fake'])

        self.assertEqual(db.session.execute(select(func.count(Admin.id))).scalars().one(), 1)
        self.assertIn('Generated the administrator.', result.output)

        self.assertEqual(
            db.session.execute(select(func.count(Post.id))).scalars().one(),
            default_post_count
        )
        self.assertIn(f'Generated {default_post_count} posts.', result.output)

        self.assertEqual(db.session.execute(
            select(func.count(Category.id))).scalars().one(),
            default_category_count
        )
        self.assertIn(f'Generated {default_category_count} categories.', result.output)

        self.assertEqual(
            db.session.execute(select(func.count(Comment.id))).scalars().one(),
            default_comment_count + default_reply_count
        )
        self.assertIn(f'Generated {default_comment_count} comments.', result.output)
        self.assertIn(f'Generated {default_reply_count} replies.', result.output)

        self.assertIn('Generated links.', result.output)

    def test_fake_command_with_custom_count(self):
        category_count = 5
        post_count = 20
        comment_count = 100
        reply_count = 20

        result = self.cli_runner.invoke(
            args=[
                'fake',
                '--category', category_count,
                '--post', post_count,
                '--comment', comment_count,
                '--reply', reply_count
            ]
        )

        self.assertEqual(db.session.execute(select(func.count(Admin.id))).scalars().one(), 1)
        self.assertIn('Generated the administrator.', result.output)

        self.assertEqual(
            db.session.execute(select(func.count(Category.id))).scalars().one(),
            category_count
        )
        self.assertIn(f'Generated {category_count} categories.', result.output)

        self.assertEqual(
            db.session.execute(select(func.count(Post.id))).scalars().one(),
            post_count
        )
        self.assertIn(f'Generated {post_count} posts.', result.output)

        self.assertEqual(
            db.session.execute(select(func.count(Comment.id))).scalars().one(),
            comment_count + reply_count
        )
        self.assertIn(f'Generated {comment_count} comments.', result.output)
        self.assertIn(f'Generated {reply_count} replies.', result.output)

        self.assertIn('Generated links.', result.output)
