from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Length
from forms.custom_validators import empty_field


class EditContractForm(FlaskForm):
    company = StringField("company",
                          validators=[Length(min=1, max=16, message=empty_field),])
    voen = StringField("voen", validators=[
                                           Length(min=10, max=20),
                                           ])
    contract_number = StringField("contract number", validators=[Length(min=1, max=16, message=empty_field)])
    date = DateField("date")
    amount = DecimalField("amount", validators=[NumberRange(min=1, max=1000000000)])
    save = SubmitField('save')