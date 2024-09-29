from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    category = SearchField('Kateqoriya əlavə edin', validators=[DataRequired(), Length(max=15)])
    save = SubmitField('Saxla')