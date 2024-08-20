from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, HiddenField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

from forms.create_addition_form import CreateAddition
from forms.custom_validators import *


class EditAdditionForm(CreateAddition):
    addition_date = DateField('date', validators=[Optional()])
    addition_number = StringField('addition number', validators=[Optional()])
    addition_amount = DecimalField("amount", validators=[Optional(),
                                                    NumberRange(min=1, max=1000000000, message=amount_error_message)]
                              )
    pdf_file_act = FileField("Upload pdf", validators=[Optional(),
                                                       FileAllowed(["pdf"], pdf_files_only)]
                             )