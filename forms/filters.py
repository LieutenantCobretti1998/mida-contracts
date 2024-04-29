from typing import Dict

from sqlalchemy.exc import NoResultFound, IntegrityError
from flask import flash
from database.db_init import db
from database.models import Companies, VOEN, Contract
from sqlalchemy.sql import exists

# Here is the list of our filters


def filter_string_fields(string_data: str) -> str:
    if string_data != "":
        return ' '.join(string_data.lower().split())


def filter_voen(voen: str) -> str:
    if voen != "":
        return voen.strip()


def get_or_create_company(company_name: str) -> Companies | None:

    if not company_name:
        return

    try:
        filtered_company = filter_string_fields(company_name)
        company = db.session.query(Companies).filter_by(company_name=filter_string_fields(filtered_company)).one()
    except NoResultFound:
        company = Companies(company_name=filter_string_fields(company_name))
        db.session.add(company)
        db.session.flush()
    return company


def filter_contract_number(contract_number: str) -> str:
    if contract_number:
        return contract_number.strip().replace(" ", "")


def check_voen_contract_company_exists(voen_id: str, contract_number: str, amount: float) -> bool:
    print(voen_id)
    if isinstance(voen_id, str):
        return False
    try:
        existing_contract = db.session.query(Contract).filter(
            Contract.voen_id == voen_id,
            Contract.contract_number == contract_number,
            Contract.amount == float(amount)
        ).one()
        return True
    except NoResultFound:
        return False


def check_voen(voen: str, company_id: int) -> dict[int, None] | VOEN | int:
    if voen:
        filtered_voen = voen.replace(" ", "")
        try:
            voen = db.session.query(VOEN).filter_by(voen=filtered_voen).one()
            if voen.company_id != company_id:
                return {
                    "status": None,
                    "company_id": voen.company_id
                }
        except NoResultFound:
            new_voen = VOEN(voen=filtered_voen, company_id=company_id)
            db.session.add(new_voen)
            db.session.flush()
            return new_voen
        return voen.id


