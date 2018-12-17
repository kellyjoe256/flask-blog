from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (DataRequired, Email, Length, EqualTo,
                                ValidationError)
from app.utils import is_email
from app.models import User


class LoginForm(Form):
    username_email = StringField('Username or Email Address', validators=[
        DataRequired('Username or Email Address is required'), ])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required'), ])
    submit = SubmitField('Login')

    def validate_username_email(self, field):
        form_value = field.data
        if '@' in form_value and not is_email(form_value):
            raise ValidationError('Email provided is not valid')


class RegistrationForm(Form):
    name = StringField('Name', validators=[
        DataRequired('Name is required'),
        Length(max=120, message='Name must be a maximum of 120 characters')])
    username = StringField('Username', validators=[
        DataRequired('Username is required'),
        Length(max=30, message='Username must be a maximum of 30 characters')])
    email = StringField('Email Address', validators=[
        DataRequired('Email is required'),
        Email('Email provided is not valid')])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required'),
        Length(min=8, message='Password must be a minimum of 8 characters'),
        EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired('Confirm Password is required'), ])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use')
