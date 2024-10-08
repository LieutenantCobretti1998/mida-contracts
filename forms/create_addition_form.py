from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, HiddenField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.validators import DataRequired, NumberRange, Length
from forms.custom_validators import *


class CreateAddition(FlaskForm):
    addition_date = DateField('Tarix', validators=[DataRequired()])
    addition_number = StringField('Əlavə Nömrəsi', validators=[DataRequired(message=empty_field)])
    addition_amount = DecimalField("Məbləğ", validators=[DataRequired(message=empty_field),
                                                    NumberRange(min=1, max=1000000000, message=amount_error_message)]
                              )
    company_name = StringField("Şirkət Seçin",
                               validators=[DataRequired(message=empty_field),
                                           Length(min=1, max=16, message=symbol_error_message),
                                           ])
    contracts_list = SelectField("Əlaqəli Müqavilələr", validators=[DataRequired(message=empty_field)],
                                 default="Choose the contract", validate_choice=False)
    pdf_file_act = FileField("Fayl Yüklə", validators=[FileRequired(message=empty_field),
                                                      FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"], selected_files_only)]
                             )
    contract_id = HiddenField("contract_id")
    save = SubmitField('Saxla')