from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, RadioField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from forms.custom_validators import *


# Form installation
class CreateContractForm(FlaskForm):
    company = StringField("company",
                          validators=[DataRequired(message=empty_field),
                                      Length(min=1, max=16, message=symbol_error_message),
                                      ])
    voen = StringField("voen", validators=[DataRequired(message=empty_field),
                                           Length(min=10, max=10, message=voen_number_enough_error),
                                           check_voen])
    contract_number = StringField("contract number",
                                  validators=[DataRequired(message=empty_field),
                                              Length(min=1, max=16,
                                                     message=symbol_error_message)])
    start_date = DateField("start date", validators=[DataRequired(message=empty_field)])
    end_date = DateField("end date", validators=[DataRequired(message=empty_field)])
    amount = DecimalField("amount", validators=[DataRequired(message=empty_field),
                                                NumberRange(min=1, max=1000000000, message=amount_error_message)]
                          )

    is_adv_payer = BooleanField("Is_Adv Payer", validators=[Optional()])

    categories = SelectField("categories", validate_choice=False, coerce=int, validators=[DataRequired(message=empty_field)])

    pdf_file = FileField("Upload pdf", validators=[FileRequired(message=empty_field),
                                                   FileAllowed(["pdf"], pdf_files_only)]
                         )
    save = SubmitField('save')
