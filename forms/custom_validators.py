from wtforms.validators import ValidationError

symbol_error_message = "Please enter an input between 1 and 16 characters."
empty_field = "This field is required"
empty_space_message = "Please enter a value instead of a pure space"
voen_number_enough_error = "Please enter voen's number with 10 characters."
voen_only_number_error = "VOEN should contain only numbers"
amount_error_message = "The max sum is 1.000.000.000 "
pdf_files_only = "Only pdf files are allowed to download"


# Check voen for any letters and amount of symbols
def check_voen(form, field) -> None:
    if not field.data.isdigit():
        raise ValidationError(voen_only_number_error)


def whitespace_check(form, field) -> None:
    if field.data.replace(" ", "") == "":
        raise ValidationError(empty_space_message)
