from wtforms import EmailField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import PasswordField, SubmitField
from wtforms.validators import Length, Email, Optional
from forms.add_user import CreateUserForm
from forms.custom_validators import *


class EditUserForm(CreateUserForm):
    username = EmailField('İstifadəçi adı', validators=[Optional(), Length(min=1, max=20),
                                                  Email(message=user_error_message)])
    password = PasswordField('Parol', validators=[Optional(), Length(min=1, max=8)])
    role = SelectField('İstifadəçi Rolu', choices=[('viewer', 'Viewer'), ('editor', 'Manager'), ('admin', 'Admin')])
    submit = SubmitField('Saxla')