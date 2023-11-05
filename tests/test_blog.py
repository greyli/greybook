from greybook.models import Post
from greybook.core.extensions import db

from tests import BaseTestCase


class BlogTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.login()

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Home', data)
        self.assertIn('Test Blog Title', data)
        self.assertIn('Test sub title', data)
        self.assertIn('Test Post Title', data)
        self.assertIn('Test Link', data)

    def test_post_page(self):
        response = self.client.get('/post/1')
        data = response.get_data(as_text=True)
        self.assertIn('Test Post Title', data)
        self.assertIn('Test comment body', data)

    def test_change_theme(self):
        response = self.client.get('/change-theme/default', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('css/default.min.css', data)
        self.assertNotIn('css/perfect_blue.min.css', data)

        response = self.client.get('/change-theme/perfect_blue', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('css/perfect_blue.min.css', data)
        self.assertNotIn('css/default.min.css', data)

    def test_about_page(self):
        response = self.client.get('/about')
        data = response.get_data(as_text=True)
        self.assertIn('Test about page.', data)
        self.assertIn('About', data)

    def test_category_page(self):
        response = self.client.get('/category/1')
        data = response.get_data(as_text=True)
        self.assertIn('Category: Test Category', data)
        self.assertIn('Test Post Title', data)

    def test_new_admin_comment(self):
        response = self.client.post(
            '/post/1',
            data=dict(body='I am an admin comment.'),
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertIn('I am an admin comment.', data)

    def test_new_guest_comment(self):
        self.logout()
        response = self.client.post(
            '/post/1',
            data=dict(
                author='Guest',
                email='a@b.com',
                site='http://greyli.com',
                body='I am a guest comment.',
            ),
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Thanks, your comment will be published after reviewed.', data)
        self.assertNotIn('I am a guest comment.', data)

    def test_reply_status(self):
        response = self.client.get('/reply/comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Reply to', data)
        self.assertIn('Cancel', data)

        post = db.session.get(Post, 1)
        post.can_comment = False
        db.session.commit()

        response = self.client.get('/reply/comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment is disabled.', data)
        self.assertNotIn('Reply to', data)
        self.assertNotIn('Cancel', data)

    def test_new_admin_reply(self):
        response = self.client.post(
            '/post/1' + '?reply=1',
            data=dict(body='I am an admin reply comment.'),
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertIn('I am an admin reply comment.', data)
        self.assertIn('Reply', data)

    def test_new_guest_reply(self):
        self.logout()
        response = self.client.post(
            '/post/1' + '?reply=1', data=dict(
                author='Guest',
                email='a@b.com',
                site='http://greyli.com',
                body='I am a guest comment.',
            ),
            follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Thanks, your comment will be published after reviewed.', data)
        self.assertNotIn('I am a guest comment.', data)
