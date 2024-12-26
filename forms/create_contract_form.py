from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField
from flask_wtf.file import FileRequired, FileAllowed, FileField, MultipleFileField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import BooleanField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from forms.custom_validators import *


# Form installation
class CreateContractForm(FlaskForm):
    company = StringField("Şirkət",
                          validators=[DataRequired(message=empty_field),
                                      Length(min=1, max=16, message=symbol_error_message),
                                      ])
    voen = StringField("Vöen", validators=[DataRequired(message=empty_field),
                                           Length(min=10, max=10, message=voen_number_enough_error),
                                           check_voen])
    contract_number = StringField("Kontrakt nömrəsi",
                                  validators=[DataRequired(message=empty_field),
                                              Length(min=1, max=16,
                                                     message=symbol_error_message)])
    start_date = DateField("Başlama tarixi", validators=[DataRequired(message=empty_field)])
    end_date = DateField("Bitmə tarixi", validators=[DataRequired(message=empty_field)])
    amount = DecimalField("Məbləğ", validators=[DataRequired(message=empty_field),
                                                NumberRange(min=1, max=1000000000, message=amount_error_message)]
                          )

    is_adv_payer = BooleanField("Ədv ödəyicisi", validators=[Optional()])

    categories = SelectField("Kategoriyalar", validate_choice=False, coerce=int, validators=[DataRequired(message=empty_field)])

    pdf_file = FileField("Müqavilə yüklə", validators=[FileRequired(message=empty_field),
                                                  FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"], selected_files_only)]
                         )
    additional_files = MultipleFileField("Əlavə sənədlər. (Maksimum 5 fayl)", validators=[
        Optional(),
        FileAllowed(["pdf", "gif", "png", "jpeg", "jpg"], selected_files_only)])
    comments = TextAreaField("Əlavə qeydlər", validators=[whitespace_check])
    save = SubmitField('Saxla')

    def validate_additional_files(self, field):
        if len(field.data) > 5:
            raise ValidationError("Maksimum 5 əlavə fayl yükləyə bilərsiniz.")


