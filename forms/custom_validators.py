import os
from wtforms.validators import ValidationError
from forms.filters import *

login_password_error_message = "Zəhmət olmasa düzgün formada parol təqdim edin."
user_error_message = "Zəhmət olmasa düzgün formada e-poçt yazın."
symbol_error_message = "Zəhmət olmasa 1 və 16 simvol arasında bir giriş daxil edin."
empty_field = "Bu sahə tələb olunur."
empty_space_message = "Lütfən, təmiz boşluq yerinə dəyər daxil edin."
voen_number_enough_error = "Zəhmət olmasa voen nömrəsini 10 simvolla daxil edin."
swift_number_enough_error = "Zəhmət olmasa, 8 və 11 simvol arasında olan Swift nömrəni daxil edin."
voen_only_number_error = "Vöen yalnız rəqəmlərdən ibarət olmalıdır."
amount_error_message = "Maksimum məbləğ 1-dən 1 milyona qədər olmalıdır."
selected_files_only = "Yalnız PDF, GIF və şəkil fayllarına yükləməyə icazə verilir."
check_adv = "Zəhmət olmasa bəli və ya yox seçin"


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
        new_remained_amount = (original_amount - new_amount) + old_remained_amount
    elif original_amount < new_amount:
        new_remained_amount = (new_amount - original_amount) + old_remained_amount
    if new_remained_amount < 0:
        raise ValueError
    return new_remained_amount


def calculate_new_amount(new_amount: float, total_addition_amount: float, total_act_amount: float) -> float:
    new_contract_remained_amount = new_amount + total_addition_amount - total_act_amount
    if new_contract_remained_amount < 0:
        raise ValueError
    return new_contract_remained_amount


class NegativeAmountError(ValueError):
    """Exception raised when an amount is negative."""

    def __init__(self, message="Amount cannot be negative"):
        self.message = message
        super().__init__(self.message)
