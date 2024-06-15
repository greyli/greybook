from threading import Thread

from flask import current_app, url_for
from flask_mailman import EmailMessage


def _send_async_mail(app, message):
    with app.app_context():
        message.send()


def send_mail(subject, body, to):
    if current_app.debug:
        current_app.logger.debug('Skip sending email in debug mode.')
        current_app.logger.debug(f'To: {to}')
        current_app.logger.debug(f'Subject: {subject}')
        current_app.logger.debug(f'Body: {body}')
        return
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
        body=f'<p>New comment in post <i>{post.title}</i>, click the link below to check:</p>'
        f'<p><a href="{post_url}">{post_url}</a></P>'
        '<p><small style="color: #868e96">Do not reply this email.</small></p>',
        to=current_app.config['GREYBOOK_ADMIN_EMAIL'],
    )


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_mail(
        subject='New reply',
        body=f'<p>New reply for the comment you left in post <i>{comment.post.title}</i>, '
        f'click the link below to check: </p><p><a href="{post_url}">{post_url}</a></p>'
        '<p><small style="color: #868e96">Do not reply this email.</small></p>',
        to=comment.email,
    )
