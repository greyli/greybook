import os
from unittest.mock import call, patch

from greybook.core.extensions import db
from greybook.models import Category, Comment, Post
from tests import BaseTestCase


class AdminTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.login()

    def test_new_post(self):
        response = self.client.get('/admin/post/new')
        data = response.get_data(as_text=True)
        self.assertIn('New Post', data)

        response = self.client.post(
            '/admin/post/new', data=dict(title='Something', category=1, body='Hello, world.'), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Post created.', data)
        self.assertIn('Something', data)
        self.assertIn('Hello, world.', data)

    def test_edit_post(self):
        response = self.client.get('/admin/post/1/edit')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Post', data)
        self.assertIn('Test Post Title', data)
        self.assertIn('Test post body', data)

        post = db.session.get(Post, 1)
        updated_at_before = post.updated_at

        response = self.client.post(
            '/admin/post/1/edit',
            data=dict(title='Something Edited', category=1, body='New post body.'),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn('Post updated.', data)
        self.assertIn('New post body.', data)
        self.assertNotIn('Test post body', data)

        updated_post = db.session.get(Post, 1)
        self.assertNotEqual(updated_at_before, updated_post.updated_at)

    def test_save_edited_post_when_validation_failed(self):
        response = self.client.post(
            '/admin/post/1/edit', data=dict(title='Something Edited', category=1, body='  '), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Edit Post', data)
        self.assertIn('This field is required', data)
        self.assertIn('Something Edited', data)

    def test_delete_post(self):
        response = self.client.get('/admin/post/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Post deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post('/admin/post/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post deleted.', data)

    @patch('os.remove')
    @patch('os.path.exists')
    def test_delete_post_with_images(self, mock_exists, mock_remove):
        post = db.session.get(Post, 1)
        post.body = '<img src="/uploads/test.png"> <img alt="" src="/uploads/test2.png">'
        db.session.commit()

        image_path = os.path.join(self.app.config['GREYBOOK_UPLOAD_PATH'], 'test.png')
        image_path2 = os.path.join(self.app.config['GREYBOOK_UPLOAD_PATH'], 'test2.png')

        mock_exists.return_value = True
        self.client.post('/admin/post/1/delete')
        self.assertEqual(os.remove.call_count, 2)
        mock_remove.assert_has_calls([call(image_path), call(image_path2)])

    def test_delete_comment(self):
        response = self.client.get('/admin/comment/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Comment deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post('/admin/comment/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment deleted.', data)
        self.assertNotIn('Test comment body', data)

    def test_enable_comment(self):
        post = db.session.get(Post, 1)
        post.can_comment = False
        db.session.commit()

        response = self.client.post('/admin/post/1/set-comment', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment enabled.', data)

        response = self.client.post('/post/1')
        data = response.get_data(as_text=True)
        self.assertIn('<div id="comment-form">', data)

    def test_disable_comment(self):
        response = self.client.post('/admin/post/1/set-comment', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment disabled.', data)

        response = self.client.post('/post/1')
        data = response.get_data(as_text=True)
        self.assertNotIn('<div id="comment-form">', data)

    def test_approve_comment(self):
        self.logout()
        response = self.client.post(
            '/post/1',
            data=dict(
                author='Guest',
                email='a@b.com',
                site='http://greyli.com',
                body='I am a guest comment.',
                post=db.session.get(Post, 1),
            ),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn('Thanks, your comment will be published after reviewed.', data)
        self.assertNotIn('I am a guest comment.', data)

        self.login()
        response = self.client.post('/admin/comment/2/approve', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)

        response = self.client.post('/post/1')
        data = response.get_data(as_text=True)
        self.assertIn('I am a guest comment.', data)

    def test_approve_all_comment(self):
        comment1 = Comment(
            author='Guest',
            email='a@b.com',
            body='Test comment 1.',
            post=db.session.get(Post, 1),
        )
        comment2 = Comment(
            author='Guest',
            email='a@b.com',
            body='Test comment 2.',
            post=db.session.get(Post, 1),
        )
        db.session.add(comment1)
        db.session.add(comment2)
        db.session.commit()

        response = self.client.post('/admin/comments/approve', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('All comments published.', data)

        response = self.client.post('/post/1')
        data = response.get_data(as_text=True)
        self.assertIn('Test comment 1.', data)
        self.assertIn('Test comment 2.', data)

    def test_new_category(self):
        response = self.client.get('/admin/category/new')
        data = response.get_data(as_text=True)
        self.assertIn('New Category', data)

        response = self.client.post('/admin/category/new', data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category created.', data)
        self.assertIn('Tech', data)

        response = self.client.post('/admin/category/new', data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Name already in use.', data)

        category = db.session.get(Category, 1)
        post = Post(title='Post title', body='Post body', category=category)
        db.session.add(post)
        db.session.commit()
        response = self.client.get('/category/1')
        data = response.get_data(as_text=True)
        self.assertIn('Post Title', data)

    def test_edit_category(self):
        response = self.client.post('/admin/category/1/edit', data=dict(name='Edited'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category updated.', data)
        self.assertIn('Test Category', data)
        self.assertNotIn('Edited', data)
        self.assertIn('You can not edit the default category', data)

        response = self.client.post('/admin/category/new', data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category created.', data)
        self.assertIn('Tech', data)

        response = self.client.get('/admin/category/2/edit')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Category', data)
        self.assertIn('Tech', data)

        response = self.client.post('/admin/category/2/edit', data=dict(name='Life'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category updated.', data)
        self.assertIn('Life', data)
        self.assertNotIn('Tech', data)

    def test_delete_category(self):
        category = Category(name='Tech')
        post = Post(title='Post title', body='Post body', category=category)
        db.session.add(category)
        db.session.add(post)
        db.session.commit()

        response = self.client.get('/admin/category/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post('/admin/category/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('You can not delete the default category.', data)
        self.assertNotIn('Category deleted.', data)
        self.assertIn('Test Category', data)

        response = self.client.post('/admin/category/2/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category deleted.', data)
        self.assertIn('Test Category', data)
        self.assertNotIn('Tech', data)

        post = db.session.get(Post, 2)
        self.assertEqual(post.category_id, 1)

    def test_new_link(self):
        response = self.client.get('/admin/link/new')
        data = response.get_data(as_text=True)
        self.assertIn('New Link', data)

        response = self.client.post(
            '/admin/link/new', data=dict(name='HelloFlask', url='http://helloflask.com'), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Link created.', data)
        self.assertIn('HelloFlask', data)

    def test_edit_link(self):
        response = self.client.get('/admin/link/1/edit')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Link', data)
        self.assertIn('Test Link', data)
        self.assertIn('http://example.com', data)

        response = self.client.post(
            '/admin/link/1/edit', data=dict(name='Github', url='https://github.com/helloflask'), follow_redirects=True
        )
        data = response.get_data(as_text=True)
        self.assertIn('Link updated.', data)
        self.assertIn('https://github.com/helloflask', data)

    def test_delete_link(self):
        response = self.client.get('/admin/link/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Link deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post('/admin/link/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link deleted.', data)

    def test_manage_post_page(self):
        response = self.client.get('/admin/post/manage')
        data = response.get_data(as_text=True)
        self.assertIn('Manage Posts', data)

    def test_manage_comment_page(self):
        response = self.client.get('/admin/comment/manage')
        data = response.get_data(as_text=True)
        self.assertIn('Manage Comments', data)

    def test_manage_category_page(self):
        response = self.client.get('/admin/category/manage')
        data = response.get_data(as_text=True)
        self.assertIn('Manage Categories', data)

    def test_manage_link_page(self):
        response = self.client.get('/admin/link/manage')
        data = response.get_data(as_text=True)
        self.assertIn('Manage Links', data)

    def test_blog_setting(self):
        response = self.client.post(
            '/admin/settings',
            data=dict(
                name='Grey Li',
                blog_title='My Blog',
                blog_sub_title='Just some raw ideas.',
                bio='I am ...',
                about='Example about page',
                custom_footer='Powered by Grey Li',
                custom_css='body { color: red; }',
                custom_js='console.log("Hello");',
            ),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn('Setting updated.', data)
        self.assertIn('My Blog', data)

        response = self.client.get('/admin/settings')
        data = response.get_data(as_text=True)
        self.assertIn('Grey Li', data)
        self.assertIn('My Blog', data)

        response = self.client.get('/about', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Example about page', data)

        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Powered by Grey Li', data)
        self.assertNotIn('@ 2023', data)
        self.assertIn('body { color: red; }', data)
        self.assertIn('console.log("Hello");', data)
