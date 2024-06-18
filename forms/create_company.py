from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from forms.custom_validators import *


class CompanyForm(FlaskForm):
    company = StringField("company",
                          validators=[DataRequired(message=empty_field),
                                      Length(min=1, max=16, message=symbol_error_message),
                                      ])
    voen = StringField("voen", validators=[DataRequired(message=empty_field),
                                           Length(min=10, max=10, message=voen_number_enough_error),
                                           check_voen])
    email = EmailField("email", validators=[Optional()])

    telephone_number = TelField("telephone_number", validators=[Optional()])
    address = StringField("address", validators=[Optional()])
    website = StringField("website", validators=[Optional()])
    save = SubmitField('Save')