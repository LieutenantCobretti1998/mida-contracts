from wtforms import StringField
from wtforms.validators import Length, Optional

from forms.create_company import CompanyForm
from forms.custom_validators import *


class EditCompanyForm(CompanyForm):
    company = StringField("company",
                          validators=[Optional(),
                                      Length(min=1, max=16, message=symbol_error_message),
                                      ])
    voen = StringField("voen", validators=[Optional(),
                                           Length(min=10, max=10, message=voen_number_enough_error),
                                           check_voen])

