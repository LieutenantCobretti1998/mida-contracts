from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, HiddenField
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import NumberRange, Length, Optional
from forms.create_act_form import CreateAct
from forms.custom_validators import *


class EditActForm(CreateAct):
    act_date = DateField('date', validators=[Optional()])
    act_number = StringField('act number', validators=[Optional()])
    act_amount = DecimalField("amount", validators=[Optional(),
                                                    NumberRange(min=1, max=1000000000, message=amount_error_message)]
                              )
    company_name = StringField("select a company",
                               validators=[Optional(),
                                           Length(min=1, max=16, message=symbol_error_message),
                                           ])
    contracts_list = SelectField("related contracts", validators=[Optional()],
                                 default="Choose the contract", validate_choice=False)
    pdf_file_act = FileField("Upload pdf", validators=[Optional(),
                                                       FileAllowed(["pdf"], pdf_files_only)]
                             )
    contract_id = HiddenField("contract_id")
    save = SubmitField('save')