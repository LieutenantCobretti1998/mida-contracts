from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from forms.custom_validators import check_voen, voen_number_enough_error, \
    symbol_error_message, empty_field, amount_error_message


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
    date = DateField("date", validators=[DataRequired(message=empty_field)])
    amount = DecimalField("amount", validators=[DataRequired(message=empty_field),
                                                NumberRange(min=1, max=1000000000, message=amount_error_message)])
    save = SubmitField('save')
