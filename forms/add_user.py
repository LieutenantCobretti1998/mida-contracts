from wtforms.fields.choices import SelectField
from wtforms.fields.simple import SubmitField

from forms.login import LoginForm


class CreateUserForm(LoginForm):
    role = SelectField('User Role', choices=[('viewer', 'Viewer'), ('editor', 'Manager'), ('admin', 'Admin')])
    submit = SubmitField('Add User')