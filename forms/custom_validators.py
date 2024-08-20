import os
from wtforms.validators import ValidationError
from forms.filters import *

symbol_error_message = "Please enter an input between 1 and 16 characters."
empty_field = "This field is required"
empty_space_message = "Please enter a value instead of a pure space"
voen_number_enough_error = "Please enter voen's number with 10 characters."
swift_number_enough_error = "Please enter the swift number with characters between 8 and 11 symbols."
voen_only_number_error = "VOEN should contain only numbers"
amount_error_message = "The max sum should be greater than 1 and until 1 million "
pdf_files_only = "Only pdf files are allowed to download"
check_adv = "Please choose yes or no, please"


# Check voen for any letters and amount of symbols
def check_voen(form, field) -> None:
    if not field.data.isdigit():
        raise ValidationError(voen_only_number_error)


# White space check
def whitespace_check(form, field) -> None:
    if field.data.replace(" ", "") == "":
        raise ValidationError(empty_space_message)


# Check if the date is not actually just an empty date
def is_date_valid(form, field) -> None:
    if not field:
        raise ValidationError(empty_field)

    # Make the file name unique


# Create a folder for newly added pdf
def add_contract_pdf(directory: str, pdf_filename: str, company_name: str = None) -> str:
    """
    :param directory:
    :param company_name:
    :param pdf_filename:
    :return: str
    Help to construct file path for uploaded pdf by users
    """
    if company_name:
        # If company_name is provided, create a folder for the company
        company_folder = os.path.join(directory, company_name)
        company_folder = os.path.normpath(company_folder)
        if not os.path.exists(company_folder):
            os.mkdir(company_folder)
        unique_filename = make_unique(f"{pdf_filename}")
        file_path = os.path.join(company_folder, unique_filename)
    else:
        # If no company_name is provided, save in the given directory
        unique_filename = make_unique(f"{pdf_filename}")
        directory_folder = os.path.normpath(directory)
        file_path = os.path.join(directory_folder, unique_filename)

    return file_path


def check_amount(act_amount: float, total_amount: float) -> float:
    """
    :param act_amount:
    :param total_amount:
    :return: float
    Simple validation logic to be sure that act's amount is smaller:3
    """
    remained_amount = total_amount - act_amount
    if remained_amount < 0:
        raise ValueError
    return remained_amount


def check_act_amount_difference(new_act_amount: float, old_act_amount: float) -> float:
    """
    :param new_act_amount:
    :param old_act_amount:
    :return: float
    Check the act difference between the new amount and the old amount.
    """
    difference = new_act_amount - old_act_amount
    return difference


def calculate_amount(original_amount: float, new_amount: float, old_remained_amount: float = 0) -> float:
    """
    :param original_amount:
    :param new_amount:
    :param old_remained_amount:
    :return:
    If the user edit the amount then calculate and add new amount to remained one
    """
    new_remained_amount = None
    if original_amount > new_amount:
        new_remained_amount = (new_amount - original_amount) + old_remained_amount
    elif original_amount < new_amount:
        new_remained_amount = (new_amount - original_amount) + old_remained_amount
    if new_remained_amount < 0:
        raise ValueError
    return new_remained_amount
