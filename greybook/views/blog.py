from flask import render_template, flash, redirect, url_for, request, \
    current_app, Blueprint, abort, make_response, send_from_directory
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.orm import with_parent

from greybook.emails import send_new_comment_email, send_new_reply_email
from greybook.core.extensions import db
from greybook.forms import CommentForm, AdminCommentForm
from greybook.models import Post, Category, Comment
from greybook.utils import redirect_back

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['GREYBOOK_POST_PER_PAGE']
    pagination = db.paginate(
        select(Post).order_by(Post.created_at.desc()),
        page=page,
        per_page=per_page,
    )
    posts = pagination.items
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = db.get_or_404(Category, category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['GREYBOOK_POST_PER_PAGE']
    pagination = db.paginate(
        select(Post)
        .filter(with_parent(category, Category.posts))
        .order_by(Post.created_at.desc()),
        page=page,
        per_page=per_page,
    )
    posts = pagination.items
    return render_template(
        'blog/category.html',
        category=category,
        pagination=pagination,
        posts=posts
    )


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = db.get_or_404(Post, post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['GREYBOOK_COMMENT_PER_PAGE']
    pagination = db.paginate(
        select(Comment)
        .filter(with_parent(post, Post.comments))
        .filter_by(reviewed=True)
        .order_by(Comment.created_at.asc()),
        page=page,
        per_page=per_page,
    )
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config['GREYBOOK_ADMIN_EMAIL']
        form.site.data = url_for('.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author,
            email=email,
            site=site,
            body=body,
            from_admin=from_admin,
            post_id=post_id,
            reviewed=reviewed
        )
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = db.get_or_404(Comment, replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:  # send message based on authentication status
            flash('Comment published.', 'success')
        else:
            flash('Thanks, your comment will be published after reviewed.', 'info')
            send_new_comment_email(post)  # send notification email to admin
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template(
        'blog/post.html',
        post=post,
        pagination=pagination,
        form=form,
        comments=comments
    )


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = db.get_or_404(Comment, comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for(
            '.show_post',
            post_id=comment.post_id,
            reply=comment_id,
            author=comment.author
        ) + '#comment-form'
    )


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['GREYBOOK_THEMES']:
        abort(400, description='Invalid theme name.')

    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
    return response


@blog_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['GREYBOOK_UPLOAD_PATH'], filename)