from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    category = SearchField('Add the category', validators=[DataRequired(), Length(max=30)])
    save = SubmitField('save')