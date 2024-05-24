from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from forms.custom_validators import company_error_message, voen_error_message, check_only_numbers


class EditContractForm(FlaskForm):
    company = StringField("company",
                          validators=[Length(min=1, max=16, message=company_error_message),])
    voen = StringField("voen", validators=[
                                           Length(min=1, max=20, message=voen_error_message),
                                           check_only_numbers])
    contract_number = StringField("contract number", validators=[Length(min=1, max=16, message=company_error_message)])
    date = DateField("date")
    amount = DecimalField("amount", validators=[NumberRange(min=1, max=1000000000)])
    save = SubmitField('save')