import os

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


def add_contract_pdf(dir: str, company_name: str, pdf_filename: str) -> str:
    company_folder = os.path.join(dir, company_name)
    if not os.path.exists(company_folder):
        os.mkdir(company_folder)
    file_path = os.path.join(company_folder, pdf_filename)
    return file_path

