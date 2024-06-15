import logging
from logging.handlers import RotatingFileHandler, SMTPHandler

from flask import request
from flask.logging import wsgi_errors_stream


def register_logging(app):
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super().format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] %(remote_addr)s requested %(url)s\n' '%(levelname)s in %(module)s: %(message)s'
    )

    logging_path = app.config['GREYBOOK_LOGGING_PATH']
    if logging_path == 'stream':
        file_handler = logging.StreamHandler(wsgi_errors_stream)
    else:
        file_handler = RotatingFileHandler(logging_path, maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=['ADMIN_EMAIL'],
        subject=app.config['GREYBOOK_ERROR_EMAIL_SUBJECT'],
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
    )
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(request_formatter)

    if not app.debug:
        app.logger.addHandler(mail_handler)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
