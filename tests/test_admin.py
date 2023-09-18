from bluelog.models import Post, Category, Link, Comment
from bluelog.extensions import db

from tests.base import BaseTestCase


class AdminTestCase(BaseTestCase):

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.login()

        category = Category(name='Default')
        post = Post(title='Hello', category=category, body='Blah...')
        comment = Comment(body='A comment', post=post, from_admin=True)
        link = Link(name='GitHub', url='https://github.com/greyli')
        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_new_post(self):
        response = self.client.get('/admin/post/new')
        data = response.get_data(as_text=True)
        self.assertIn('New Post', data)

        response = self.client.post('/admin/post/new', data=dict(
            title='Something',
            category=1,
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post created.', data)
        self.assertIn('Something', data)
        self.assertIn('Hello, world.', data)

    def test_edit_post(self):
        response = self.client.get('/admin/post/1/edit')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Post', data)
        self.assertIn('Hello', data)
        self.assertIn('Blah...', data)

        post = db.session.get(Post, 1)
        updated_at_before = post.updated_at

        response = self.client.post('/admin/post/1/edit', data=dict(
            title='Something Edited',
            category=1,
            body='New post body.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post updated.', data)
        self.assertIn('New post body.', data)
        self.assertNotIn('Blah...', data)

        updated_post = db.session.get(Post, 1)
        self.assertNotEqual(updated_at_before, updated_post.updated_at)

    def test_save_edited_post_when_validation_failed(self):
        response = self.client.post('/admin/post/1/edit', data=dict(
            title='Something Edited',
            category=1,
            body='  '
        ), follow_redirects=True)
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

    def test_delete_comment(self):
        response = self.client.get('/admin/comment/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Comment deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post('/admin/comment/1/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment deleted.', data)
        self.assertNotIn('A comment', data)

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
        response = self.client.post('/post/1', data=dict(
            author='Guest',
            email='a@b.com',
            site='http://greyli.com',
            body='I am a guest comment.',
            post=db.session.get(Post, 1),
        ), follow_redirects=True)
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
        post = Post(title='Post Title', category=category)
        db.session.add(post)
        db.session.commit()
        response = self.client.get('/category/1')
        data = response.get_data(as_text=True)
        self.assertIn('Post Title', data)

    def test_edit_category(self):
        response = self.client.post('/admin/category/1/edit',
                                    data=dict(name='Default edited'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category updated.', data)
        self.assertIn('Default', data)
        self.assertNotIn('Default edited', data)
        self.assertIn('You can not edit the default category', data)

        response = self.client.post('/admin/category/new', data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category created.', data)
        self.assertIn('Tech', data)

        response = self.client.get('/admin/category/2/edit')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Category', data)
        self.assertIn('Tech', data)

        response = self.client.post('/admin/category/2/edit',
                                    data=dict(name='Life'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category updated.', data)
        self.assertIn('Life', data)
        self.assertNotIn('Tech', data)

    def test_delete_category(self):
        category = Category(name='Tech')
        post = Post(title='test', category=category)
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
        self.assertIn('Default', data)

        response = self.client.post('/admin/category/2/delete', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category deleted.', data)
        self.assertIn('Default', data)
        self.assertNotIn('Tech', data)

    def test_new_link(self):
        response = self.client.get('/admin/link/new')
        data = response.get_data(as_text=True)
        self.assertIn('New Link', data)

        response = self.client.post('/admin/link/new', data=dict(
            name='HelloFlask',
            url='http://helloflask.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link created.', data)
        self.assertIn('HelloFlask', data)

    def test_edit_link(self):
        response = self.client.get('/admin/link/1/edit')
        data = response.get_data(as_text=True)
        self.assertIn('Edit Link', data)
        self.assertIn('GitHub', data)
        self.assertIn('https://github.com/greyli', data)

        response = self.client.post('/admin/link/1/edit', data=dict(
            name='Github',
            url='https://github.com/helloflask'
        ), follow_redirects=True)
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
        response = self.client.post('/admin/settings', data=dict(
            name='Grey Li',
            blog_title='My Blog',
            blog_sub_title='Just some raw ideas.',
            bio='I am ...',
            about='Example about page',
        ), follow_redirects=True)
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
