# Here is the list of our filters

def filter_string_fields(string_data: str) -> str:
    if string_data != "":
        return ' '.join(string_data.lower().split())


def filter_voen(voen: str) -> str:
    if voen != "":
        return voen.strip().replace(" ", "")


def filter_contract_number(contract_number: str) -> str:
    if contract_number:
        return contract_number.strip().replace(" ", "")

