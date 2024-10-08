from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, HiddenField
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import NumberRange, Length, Optional
from forms.create_act_form import CreateAct
from forms.custom_validators import *


class EditActForm(CreateAct):
    act_date = DateField('Tarix', validators=[Optional()])
    act_number = StringField('Akt nömrəsi', validators=[Optional()])
    act_amount = DecimalField("Məbləğ", validators=[Optional(),
                                                    NumberRange(min=1, max=1000000000, message=amount_error_message)]
                              )
    company_name = StringField("Şirkət seçin",
                               validators=[
                                           Length(min=1, max=16, message=symbol_error_message),
                                           ])
    contracts_list = SelectField("Əlaqəli müqavilələr",
                                 default="Choose the contract", validate_choice=False)
    pdf_file_act = FileField("Fayl Yüklə", validators=[Optional(),
                                                       FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"], selected_files_only)]
                             )
    contract_id = HiddenField("contract_id")
    save = SubmitField('saxla')