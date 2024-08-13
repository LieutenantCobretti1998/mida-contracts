from wtforms import SearchField, SubmitField
from wtforms.validators import Length, Optional
from forms.categories_form import SearchForm


class EditCategoryForm(SearchForm):
    category = SearchField('Edit the selected category', validators=[Optional(), Length(max=30)])
    save = SubmitField('save')