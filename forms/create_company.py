from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, Regexp
from forms.custom_validators import *


class CompanyForm(FlaskForm):
    company = StringField("Şirkət",
                          validators=[DataRequired(message=empty_field),
                                      Length(min=1, max=16, message=symbol_error_message),
                                      ])
    voen = StringField("Vöen", validators=[DataRequired(message=empty_field),
                                           Length(min=10, max=10, message=voen_number_enough_error),
                                           check_voen])
    bank_name = StringField("Bank Adı", validators=[Optional()])
    m_h = StringField("M/H", validators=[Optional()])
    h_h = StringField("H/H", validators=[Optional()])
    swift = StringField("Swift", validators=[Optional(), Length(min=8, max=11, message=swift_number_enough_error)])
    email = EmailField("E-poçt", validators=[Optional(), Email(message="Invalid Email Address")])
    telephone_number = TelField("Telefon Nömrəsi", validators=[Optional()])
    address = StringField("Ünvan", validators=[Optional()])
    website = StringField("Vebsayt", validators=[Optional(), Regexp(r'^(http[s]?://)?([a-zA-Z0-9]([a-zA-Z0-9-]{0,'
                                                                    r'61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}(?::\d{1,'
                                                                    r'5})?(?:/.*)?$', message="Invalid website url")])
    save = SubmitField('Saxla')