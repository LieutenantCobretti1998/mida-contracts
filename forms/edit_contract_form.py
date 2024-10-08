from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField
from wtforms.validators import NumberRange, Length, Optional
from forms.create_contract_form import CreateContractForm
from forms.custom_validators import *


class EditContractForm(CreateContractForm):
    company = StringField(
        "Şirkət",
        validators=[Length(min=1, max=16, message=symbol_error_message),
                    Optional(),
                    whitespace_check])
    voen = StringField(
        "Vöen",
        validators=[Length(min=10, max=10, message=voen_number_enough_error), check_voen,
                    Optional(),
                    ])
    contract_number = StringField("Kontrakt Nömrəsi",validators=[Length(min=1, max=16, message=symbol_error_message),
                                              Optional(),
                                              whitespace_check])
    start_date = DateField("Başlama Tarixi", validators=[Optional(), is_date_valid])
    end_date = DateField("Bitmə Tarixi", validators=[Optional(), is_date_valid])
    amount = DecimalField("Məbləğ", validators=[NumberRange(min=1, max=1000000000, message=amount_error_message),
                                      Optional(),
                                      ])

    categories = SelectField("Kategoriyalar", validate_choice=False, coerce=int,
                             validators=[Optional()])

    pdf_file = FileField("Fayl",validators=[Optional(),
                                                FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"], selected_files_only)]
                         )
    save = SubmitField("Save")
