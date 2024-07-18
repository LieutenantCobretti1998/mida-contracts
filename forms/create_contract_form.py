from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, DecimalField, RadioField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms.validators import DataRequired, NumberRange, Length
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
    date = DateField("date", validators=[DataRequired(message=empty_field),
                                         is_date_valid])
    amount = DecimalField("amount", validators=[DataRequired(message=empty_field),
                                                NumberRange(min=1, max=1000000000, message=amount_error_message)]
                          )

    is_adv_payer = RadioField("is adv payer",
                              choices=[("Yes", "Yes"), ("No", "No")],
                              validators=[DataRequired(message=check_adv)]
                              )

    pdf_file = FileField("Upload pdf", validators=[FileRequired(message=empty_field),
                                                   FileAllowed(["pdf"], pdf_files_only)]
                         )
    save = SubmitField('save')
