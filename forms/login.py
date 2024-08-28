from flask_wtf import FlaskForm
from wtforms import EmailField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from forms.custom_validators import *


class LoginForm(FlaskForm):
    username = EmailField('Username', validators=[DataRequired(message=empty_field), Length(min=1, max=20),
                                                  Email(message=user_error_message)])
    password = PasswordField('Password', validators=[DataRequired(message=empty_field), Length(min=1, max=8)])
    submit = SubmitField('Log In')
