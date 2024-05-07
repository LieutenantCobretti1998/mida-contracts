from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired


class SearchContract(FlaskForm):
    search = SearchField("Search")
