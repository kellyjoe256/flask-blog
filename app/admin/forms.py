from sqlalchemy import func
from flask_wtf import FlaskForm as Form
from wtforms import (BooleanField, SelectMultipleField, StringField,
                     TextAreaField, PasswordField, SubmitField)
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_login import current_user
from app import uploads
from app.models import Post, Tag


class PostForm(Form):
    title = StringField('Title', validators=[
        DataRequired('Title is required'),
        Length(max=255, message='Title must be a maximum of 255 characters')])
    cover_image = FileField('Cover Image', validators=[
        FileAllowed(uploads, u'Only images are allowed')])
    tags = SelectMultipleField('Tags', coerce=int, validators=[
        DataRequired('You must select at least one')])
    content = TextAreaField('Content', validators=[
        DataRequired('Content is required')])
    publish = BooleanField('Publish')
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        tags = Tag.query.with_entities(Tag.tag_id, Tag.name).\
            order_by(Tag.name).all()
        self.tags.choices = [(tag.tag_id, tag.name)
                             for tag in tags]


class TagForm(Form):
    name = StringField('Tag Name', validators=[
        DataRequired('Tag Name is required'),
        Length(max=30, message='Tag Name must be a maximum of 30 characters')])
    submit = SubmitField()

    def __init__(self, tag, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)
        self.tag = tag

    def validate_name(self, field):
        field_data = field.data
        # True when editing
        if self.tag:
            if field_data != self.tag.name and \
                    Tag.query.filter(
                        func.lower(Tag.name) == func.lower(field_data)).first():
                raise ValidationError('Tag Name already exists')
            return

        if Tag.query.filter(
                func.lower(Tag.name) == func.lower(field_data)).first():
            raise ValidationError('Tag Name already exists')


class AdminChangePasswordForm(Form):
    password = PasswordField('New Password', validators=[
        DataRequired('Password is required'),
        Length(min=8, message='Password must be a minimum of 8 characters'),
        EqualTo('confirm_password', 'Passwords must match'), ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired('Confirm Password is required'), ])
    submit = SubmitField('Change Password')


class ChangePasswordForm(Form):
    current_password = PasswordField('Current Password', validators=[
        DataRequired('Current Password is required'), ])
    password = PasswordField('New Password', validators=[
        DataRequired('Password is required'),
        Length(min=8, message='Password must be a minimum of 8 characters'),
        EqualTo('confirm_password', 'Passwords must match'), ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired('Confirm Password is required'), ])
    submit = SubmitField('Change Password')

    def validate_current_password(self, field):
        form_value = field.data
        if not current_user.verify_password(form_value):
            raise ValidationError(
                'Provided password does not match your current password')
