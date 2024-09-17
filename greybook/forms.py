from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from sqlalchemy import select
from wtforms import (
    BooleanField,
    HiddenField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    ValidationError,
)
from wtforms.validators import URL, DataRequired, Email, Length, Optional

from greybook.core.extensions import db
from greybook.models import Category


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    custom_footer = TextAreaField('Custom Footer (HTML)', validators=[Optional()])
    custom_css = TextAreaField('Custom CSS', validators=[Optional()])
    custom_js = TextAreaField('Custom JavaScript', validators=[Optional()])
    submit = SubmitField()


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('Category', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = db.session.scalars(select(Category).order_by(Category.name))
        self.category.choices = [(category.id, category.name) for category in categories]


class NewCategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if db.session.scalar(select(Category).filter_by(name=field.data)):
            raise ValidationError('Name already in use.')


class EditCategoryForm(NewCategoryForm):
    def __init__(self, current_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_name = current_name

    def validate_name(self, field):
        new_name = field.data
        if new_name != self.current_name and db.session.scalar(select(Category).filter_by(name=new_name)):
            raise ValidationError('Name already in use.')


class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()
