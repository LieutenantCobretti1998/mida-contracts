from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, DateField, DecimalField
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import BooleanField
from wtforms.validators import NumberRange, Length, Optional
from forms.create_contract_form import CreateContractForm
from forms.custom_validators import *


class EditContractForm(CreateContractForm):
    company = StringField(
        validators=[Length(min=1, max=16, message=symbol_error_message),
                    Optional(),
                    whitespace_check])
    voen = StringField(
        validators=[Length(min=10, max=10, message=voen_number_enough_error), check_voen,
                    Optional(),
                    whitespace_check])
    contract_number = StringField(validators=[Length(min=1, max=16, message=symbol_error_message),
                                              Optional(),
                                              whitespace_check])
    date = DateField(validators=[Optional(), is_date_valid])
    amount = DecimalField(validators=[NumberRange(min=1, max=1000000000, message=amount_error_message),
                                      Optional(),
                                      ])

    pdf_file = FileField(validators=[Optional(),
                                     FileAllowed(["pdf"], pdf_files_only)]
                         )
    save = SubmitField("Save")
