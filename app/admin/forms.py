from flask_wtf import FlaskForm as Form
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from flask_login import current_user


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
            raise ValidationError('Provided password does not match your current password')
