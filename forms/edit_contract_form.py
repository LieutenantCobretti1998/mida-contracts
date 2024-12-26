from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, DateField, DecimalField, SelectField, TextAreaField, BooleanField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.validators import NumberRange, Length, Optional
from forms.create_contract_form import CreateContractForm
from forms.custom_validators import *


class AdditionalFileForm(FlaskForm):
    file = FileField(
        "Əlavə fayl",
        validators=[
            Optional(),
            FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"],selected_files_only)
        ]
    )
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
    contract_number = StringField("Müqavilə nömrəsi",validators=[Length(min=1, max=16, message=symbol_error_message),
                                              Optional(),
                                              whitespace_check])
    start_date = DateField("Başlama tarixi", validators=[Optional(), is_date_valid])
    end_date = DateField("Bitmə tarixi", validators=[Optional(), is_date_valid])
    amount = DecimalField("Məbləğ", validators=[NumberRange(min=1, max=1000000000, message=amount_error_message),
                                      Optional(),
                                      ])

    categories = SelectField("Kategoriyalar", validate_choice=False, coerce=int,
                             validators=[Optional()])

    status = BooleanField("Bitib", validators=[Optional()])

    pdf_file = FileField("Müqavilə yüklə",validators=[Optional(),
                                                FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"], selected_files_only)]
                         )
    additional_files = FieldList(
        FormField(AdditionalFileForm),
        min_entries=0,
        max_entries=5,
        label="Əlavə fayllar"
    )
    comments = TextAreaField("Əlavə qeydlər", validators=[Optional()])
    save = SubmitField("Saxla")
