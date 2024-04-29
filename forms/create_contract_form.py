from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from forms.custom_validators import company_error_message, voen_error_message, check_only_numbers


# Form installation
class CreateContractForm(FlaskForm):
    company = StringField("company",
                          validators=[DataRequired(message="Company is required."),
                                      Length(min=1, max=16, message=company_error_message),
                                      ])
    voen = StringField("voen", validators=[DataRequired(),
                                           Length(min=1, max=12, message=voen_error_message),
                                           check_only_numbers])
    contract_number = StringField("contract_number",
                                  validators=[DataRequired(), Length(min=1, max=16, message=company_error_message)])
    date = DateField("date", validators=[DataRequired()])
    amount = DecimalField("amount", validators=[DataRequired(), NumberRange(min=1, max=1000000000)])
    save = SubmitField('save')
