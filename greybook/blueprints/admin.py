from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_ckeditor import upload_fail, upload_success
from flask_login import current_user, login_required
from sqlalchemy import select

from greybook.core.extensions import db
from greybook.forms import EditCategoryForm, LinkForm, NewCategoryForm, PostForm, SettingForm
from greybook.models import Category, Comment, Link, Post
from greybook.utils import allowed_file, random_filename, redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        current_user.custom_footer = form.custom_footer.data
        current_user.custom_css = form.custom_css.data
        current_user.custom_js = form.custom_js.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    if request.method == 'GET':
        form.name.data = current_user.name
        form.blog_title.data = current_user.blog_title
        form.blog_sub_title.data = current_user.blog_sub_title
        form.about.data = current_user.about
        form.custom_footer.data = current_user.custom_footer
        form.custom_css.data = current_user.custom_css
        form.custom_js.data = current_user.custom_js
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['GREYBOOK_MANAGE_POST_PER_PAGE']
    stmt = select(Post).order_by(Post.created_at.desc())
    pagination = db.paginate(
        stmt,
        page=page,
        per_page=per_page,
        error_out=False,
    )
    if page > pagination.pages:
        return redirect(url_for('.manage_post', page=pagination.pages))
    posts = pagination.items
    return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category_id = form.category.data
        post = Post(title=title, body=body, category_id=category_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = db.session.get(Post, post_id) or abort(404)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category_id = form.category.data
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    if request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
        form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id) or abort(404)
    post.delete()
    flash('Post deleted.', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@login_required
def set_comment(post_id):
    post = db.session.get(Post, post_id) or abort(404)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')  # 'all', 'unread', 'admin'
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['GREYBOOK_COMMENT_PER_PAGE']

    if filter_rule == 'unread':
        filtered_comments = select(Comment).filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = select(Comment).filter_by(from_admin=True)
    else:
        filtered_comments = select(Comment)

    stmt = filtered_comments.order_by(Comment.created_at.desc())
    pagination = db.paginate(
        stmt,
        page=page,
        per_page=per_page,
        error_out=False,
    )
    if page > pagination.pages:
        return redirect(url_for('.manage_comment', page=pagination.pages, filter=filter_rule))
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = db.session.get(Comment, comment_id) or abort(404)
    comment.reviewed = True
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()


@admin_bp.route('/comments/approve', methods=['POST'])
@login_required
def approve_all_comment():
    stmt = select(Comment).filter_by(reviewed=False)
    comments = db.session.scalars(stmt).all()
    for comment in comments:
        comment.reviewed = True
    db.session.commit()
    flash('All comments published.', 'success')
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = db.session.get(Comment, comment_id) or abort(404)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route('/category/manage')
@login_required
def manage_category():
    return render_template('admin/manage_category.html')


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = db.session.get(Category, category_id) or abort(404)
    if category.id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('blog.index'))
    form = EditCategoryForm(current_name=category.name)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))

    if request.method == 'GET':
        form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = db.session.get(Category, category_id) or abort(404)
    if category.id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/link/manage')
@login_required
def manage_link():
    return render_template('admin/manage_link.html')


@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'success')
        return redirect(url_for('.manage_link'))
    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    form = LinkForm()
    link = db.session.get(Link, link_id) or abort(404)
    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash('Link updated.', 'success')
        return redirect(url_for('.manage_link'))
    if request.method == 'GET':
        form.name.data = link.name
        form.url.data = link.url
    return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    link = db.session.get(Link, link_id) or abort(404)
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted.', 'success')
    return redirect(url_for('.manage_link'))


@admin_bp.route('/upload', methods=['POST'])
@login_required
def upload_image():
    f = request.files.get('upload')
    if not allowed_file(f.filename):
        return upload_fail('Image only!')
    filename = random_filename(f.filename)
    f.save(current_app.config['GREYBOOK_UPLOAD_PATH'] / filename)
    url = url_for('blog.get_image', filename=filename)
    return upload_success(url, filename)
