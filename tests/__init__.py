import unittest

from greybook import create_app
from greybook.core.extensions import db
from greybook.models import Admin, Category, Comment, Link, Post


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        self.client = self.app.test_client()
        self.cli_runner = self.app.test_cli_runner()

        db.create_all()
        user = Admin(
            name='Test Admin',
            username='admin',
            password='greybook',
            about='Test about page.',
            blog_title='Test Blog Title',
            blog_sub_title='Test sub title',
        )
        category = Category(name='Test Category')
        post = Post(title='Test Post Title', category=category, body='Test post body')
        comment = Comment(
            author='Test comment author', email='test@example.com', body='Test comment body', post=post, reviewed=True
        )
        link = Link(name='Test Link', url='http://example.com')
        db.session.add_all([user, category, post, comment, link])
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, username='admin', password='greybook'):
        return self.client.post('/auth/login', data=dict(username=username, password=password), follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
