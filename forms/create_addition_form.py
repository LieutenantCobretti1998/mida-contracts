from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, HiddenField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.validators import DataRequired, NumberRange, Length
from forms.custom_validators import *


class CreateAddition(FlaskForm):
    addition_date = DateField('date', validators=[DataRequired()])
    addition_number = StringField('addition number', validators=[DataRequired(message=empty_field)])
    addition_amount = DecimalField("amount", validators=[DataRequired(message=empty_field),
                                                    NumberRange(min=1, max=1000000000, message=amount_error_message)]
                              )
    company_name = StringField("select a company",
                               validators=[DataRequired(message=empty_field),
                                           Length(min=1, max=16, message=symbol_error_message),
                                           ])
    contracts_list = SelectField("related contracts", validators=[DataRequired(message=empty_field)],
                                 default="Choose the contract", validate_choice=False)
    pdf_file_act = FileField("Upload pdf", validators=[FileRequired(message=empty_field),
                                                       FileAllowed(["pdf"], pdf_files_only)]
                             )
    contract_id = HiddenField("contract_id")
    save = SubmitField('save')