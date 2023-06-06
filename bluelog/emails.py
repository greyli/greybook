from threading import Thread

from flask import url_for, current_app
from flask_mailman import EmailMessage


def _send_async_mail(app, message):
    with app.app_context():
        message.send()


def send_mail(subject, body, to):
    app = current_app._get_current_object()
    message = EmailMessage(subject, body=body, to=[to])
    message.content_subtype = 'html'
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_new_comment_email(post):
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_mail(
        subject='New comment',
        body='<p>New comment in post <i>%s</i>, click the link below to check:</p>'
             '<p><a href="%s">%s</a></P>'
             '<p><small style="color: #868e96">Do not reply this email.</small></p>'
             % (post.title, post_url, post_url),
        to=current_app.config['BLUELOG_ADMIN_EMAIL']
    )


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_mail(
        subject='New reply',
        body='<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>'
             '<p><a href="%s">%s</a></p>'
             '<p><small style="color: #868e96">Do not reply this email.</small></p>'
            % (comment.post.title, post_url, post_url),
        to=comment.email
    )
