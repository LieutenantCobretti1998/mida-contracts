from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from forms.custom_validators import *


class EditContractForm(FlaskForm):
    company = StringField("company",
                          validators=[Length(min=1, max=16, message=symbol_error_message),
                                      Optional(strip_whitespace=False),
                                      whitespace_check])
    voen = StringField("voen",
                       validators=[Length(min=10, max=10, message=voen_number_enough_error), check_voen,
                                   Optional(strip_whitespace=False),
                                   whitespace_check])
    contract_number = StringField("contract number", validators=[Length(min=1, max=16, message=symbol_error_message),
                                                                 Optional(strip_whitespace=False),
                                                                 whitespace_check])
    date = DateField("date", validators=[Optional(strip_whitespace=False), is_date_valid])
    amount = DecimalField("amount", validators=[NumberRange(min=1, max=1000000000, message=amount_error_message),
                                                Optional(strip_whitespace=False),
                                                ])
    save = SubmitField('Save')
