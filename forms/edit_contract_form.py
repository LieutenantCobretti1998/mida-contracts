from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from forms.custom_validators import empty_field, symbol_error_message, check_voen, voen_number_enough_error, \
    amount_error_message


class EditContractForm(FlaskForm):
    company = StringField("company",
                          validators=[Length(min=1, max=16, message=symbol_error_message),
                                      Optional()])
    voen = StringField("voen",
                       validators=[Length(min=10, max=10, message=voen_number_enough_error), check_voen,
                                   Optional()])
    contract_number = StringField("contract number", validators=[Length(min=1, max=16, message=symbol_error_message),
                                                                 Optional()])
    date = DateField("date", validators=[Optional()])
    amount = DecimalField("amount", validators=[NumberRange(min=1, max=1000000000, message=amount_error_message),
                                                Optional()])
    save = SubmitField('Save')
