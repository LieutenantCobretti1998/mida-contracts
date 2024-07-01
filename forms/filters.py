# Here is the list of our filters
from uuid import uuid4

import regex


def filter_string_fields(string_data: str) -> str:
    if string_data != "":
        sanitized_name = sanitize_company(string_data)
        return ' '.join(sanitized_name.lower().split())


def sanitize_company(company_name: str) -> str:
    sanitized = regex.sub(r'[^\p{L}\p{N}\s]', '', company_name)
    return sanitized


def filter_voen(voen: str) -> str:
    if voen != "":
        return voen.strip().replace(" ", "")


def filter_contract_number(contract_number: str) -> str:
    if contract_number:
        return contract_number.strip().replace(" ", "")


def make_unique(filename: str) -> str:
    ident = str(uuid4())
    return f"{ident}_{filename}"
