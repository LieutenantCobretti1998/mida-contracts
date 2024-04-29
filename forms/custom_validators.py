from wtforms.validators import ValidationError

company_error_message = "Please enter company name between 1 and 16 characters."
empty_space_message = "Please enter a value instead of a pure space"
voen_error_message = "Please enter voen's number  between 1 and 12 characters."
voen_error = "VOEN should contain only numbers"

# Check voen for any letters


def check_only_numbers(form, field) -> None:
    if not field.data.isdigit():
        raise ValidationError(voen_error)
