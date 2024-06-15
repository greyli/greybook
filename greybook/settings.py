import os
import sys
from pathlib import Path

basedir = Path(__file__).resolve().parent.parent

# SQLite URI compatible
prefix = 'sqlite:///' if sys.platform.startswith('win') else 'sqlite:////'


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev key')

    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ENABLED = False

    SQLALCHEMY_RECORD_QUERIES = True

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = 'admin.upload_image'

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = f'Greybook <{MAIL_USERNAME}>'

    GREYBOOK_ADMIN_EMAIL = os.getenv('GREYBOOK_ADMIN_EMAIL')
    GREYBOOK_POST_PER_PAGE = 10
    GREYBOOK_MANAGE_POST_PER_PAGE = 15
    GREYBOOK_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    GREYBOOK_THEMES = {'default': 'Default', 'perfect_blue': 'Perfect Blue'}
    GREYBOOK_SLOW_QUERY_THRESHOLD = 1

    GREYBOOK_UPLOAD_PATH = os.getenv('GREYBOOK_UPLOAD_PATH', basedir / 'uploads')
    GREYBOOK_ALLOWED_IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
    GREYBOOK_LOGGING_PATH = os.getenv('GREYBOOK_LOGGING_PATH', basedir / 'logs/greybook.log')
    GREYBOOK_ERROR_EMAIL_SUBJECT = '[Greybook] Application Error'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + str(basedir / 'data-dev.db')


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + str(basedir / 'data.db'))


config = {'development': DevelopmentConfig, 'testing': TestingConfig, 'production': ProductionConfig}
