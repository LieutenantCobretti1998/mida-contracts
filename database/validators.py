import re
from datetime import datetime, timedelta
from typing import Any, Type, List, Union, Dict
import os
import shutil
import flask
import sqlalchemy
from flask import current_app
from flask_login import current_user
from flask_sqlalchemy.session import Session
from sqlalchemy import or_, desc, asc, func, and_, cast, Float
from sqlalchemy.exc import NoResultFound, SQLAlchemyError, DBAPIError, OperationalError
from sqlalchemy.orm import InstrumentedAttribute
from werkzeug.exceptions import NotFound

from configuration import PERCENTAGE_AMOUNT
from database.models import *
from abc import ABC
from database.models import Companies, Category
from forms.custom_validators import check_amount, NegativeAmountError


class ValidatorWrapper(ABC):
    def __init__(self, db_session: Session):
        self.db_session = db_session


class ContractManager(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def search_categories(self) -> list[Type[Category]]:
        """
        :return: list[Type[Category]]
        """
        categories = self.db_session.query(Category).all()
        return categories

    @staticmethod
    def delete_pdf_file(contract: Type[Contract]) -> None:
        try:
            contract_pdf_path = str(contract.pdf_file_path)
            os.remove(contract_pdf_path)
        except FileNotFoundError:
            raise FileNotFoundError("Pdf file is not found")

    def delete_contract(self, contract_id: int) -> bool:
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                self.delete_pdf_file(contract)
                self.delete_related_acts_pdf_file(contract)
                self.delete_related_additions_pdf_file(contract)
                self.db_session.delete(contract)
                return True
            except DBAPIError:
                return False
            except FileNotFoundError:
                return False
        return False

    def delete_related_additions_pdf_file(self, contract: Type[Contract]) -> None:
        """
        :param contract: contract: Type[Contract]
        :return:
        """
        related_additions = contract.additions
        for addition in related_additions:
            self.delete_addition(addition)

    @staticmethod
    def delete_addition(addition: Type[Additions]) -> None:
        """
        :param addition: Type[Additions]
        :return:
        """
        addition_path = str(addition.pdf_file_path)
        os.remove(addition_path)

    @staticmethod
    def delete_act(act: Type[Acts]) -> None:
        """
        :param act: Type[Acts]
        :return:
        Function for deleting each act of contract
        """
        act_path = str(act.pdf_file_path)
        os.remove(act_path)

    def delete_related_acts_pdf_file(self, contract: Type[Contract]) -> None:
        """
        :param contract: Type[Contract]
        :return:
        """
        related_acts = contract.acts
        for act in related_acts:
            self.delete_act(act)

    def get_or_create_company(self, company_name: str, voen: str, *args, **kwargs) -> None | Type[
        Companies] | Companies:
        if not company_name:
            return None

        try:
            existed_company = self.db_session.query(Companies).filter_by(company_name=company_name).one()
            if existed_company.voen != voen:
                raise ValueError(f"The {company_name} company already has a voen {existed_company.voen}")
            return existed_company
        except NoResultFound:
            if self.check_voen(voen):
                raise ValueError(
                    f"VOEN is already linked to {self.db_session.query(Companies).filter_by(voen=voen).one().company_name} company")
            new_company = Companies(company_name=company_name, voen=voen)
            self.db_session.add(new_company)
            self.db_session.flush()
            return new_company

    def check_voen(self, voen: str) -> bool:
        if not voen:
            return False
        try:
            self.db_session.query(Companies).filter_by(voen=voen).one()
            return True
        except NoResultFound:
            return False

    @staticmethod
    def one_voen_one_company(voen: str) -> bool:
        if not voen:
            return False


class SearchEngine(ValidatorWrapper):
    """
    Engine for searching, filtering and formatting purposes in contracts / contract tables
    """

    def __init__(self, db_session: Session, search: str | int = None):
        super().__init__(db_session)
        self.search = search

    def search_company(self) -> Companies | None:
        result = self.db_session.query(Companies).filter_by(id=self.search).first()
        return result

    def search_company_with_contract(self) -> Contract | None:
        result = self.db_session.query(Contract).join(Companies).filter(Contract.id == self.search).first()
        if result:
            return result
        else:
            raise NoResultFound

    def asc_or_desc(self, query, sort_direction: str, mapping: tuple):
        """
        :param mapping:
        :param query:
        :param sort_direction:
        :return: None
        This method is for avoiding duplication of the sorting the columns
        """
        if mapping[0] == "category_id":
            # Join the Category table directly with the Contract table
            query = query.join(Category, Category.id == Contract.category_id)

            # Sort by category_name instead of category_id
            if sort_direction == "asc":
                return query.order_by(asc(Category.category_name))
            else:
                return query.order_by(desc(Category.category_name))
        else:
            # For other columns, sort normally
            if sort_direction == "asc":
                return query.order_by(asc(getattr(mapping[1], mapping[0])))
            else:
                return query.order_by(desc(getattr(mapping[1], mapping[0])))

    # APIs for the table
    def get_all_results_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> tuple[
        list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param mapping:
        :param sort_dir:
        :param offset:
        :param per_page:
        :return: list[dict[str, InstrumentedAttribute | Any]]
        This method is for put all results of the contract in the table
        """
        query = (self.db_session.query(Contract)
                 .join(Companies, Companies.id == Contract.company_id)
                 )
        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        contracts = query.offset(offset).limit(per_page).all()
        contract_list = [{
            "id": contract.id,
            "company_name": contract.company.company_name,
            "voen": contract.company.voen,
            "contract_number": contract.contract_number,
            "date": contract.date,
            "amount": float(contract.amount),
            "remained_amount": float(contract.remained_amount),
            "adv_payer": bool(contract.adv_payer),
            "category": contract.category.category_name
        } for contract in contracts]
        return contract_list, total_count

    def search_query_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param mapping:
        :param sort_dir:
        :param offset:
        :param per_page:
        :return: list[dict[str, InstrumentedAttribute | Any]]
        server-side search from db directly to table via api
        """
        query = (self.db_session
        .query(Contract)
        .join(Companies, Companies.id == Contract.company_id)
        .join(Category, Category.id == Contract.category_id)
        .filter(or_(
            Companies.company_name.ilike(f"%{self.search}%"),
            Companies.voen.ilike(f"%{self.search}%"),
            Contract.contract_number.ilike(f"%{self.search}%"),
            Category.category_name.ilike(f"%{self.search}%"),
        )))

        query = self.asc_or_desc(query, sort_dir, mapping)

        total_count = query.count()
        contracts = query.offset(offset).limit(per_page).all()

        contract_list = [{
            "id": contract.id,
            "company_name": contract.company.company_name,
            "voen": contract.company.voen,
            "contract_number": contract.contract_number,
            "date": contract.date,
            "amount": float(contract.amount),
            "remained_amount": float(contract.remained_amount),
            "adv_payer": bool(contract.adv_payer),
            "category": contract.category.category_name
        } for contract in contracts]
        return contract_list, total_count

    def search_related_companies_api(self) -> Union[list[InstrumentedAttribute], list[None]]:
        query = self.db_session.query(Companies).filter(Companies.company_name.ilike(f"%{self.search}%"))
        if query:
            companies = [company.company_name for company in query]
            return companies
        return []

    def search_related_contracts_api(self) -> Union[list[dict[str, int]] | list[None]]:
        company = self.db_session.query(Companies).filter_by(company_name=self.search).first()
        if company:
            contracts = [
                {
                    "id": contract.id,
                    "contract_number": contract.contract_number
                } for contract in company.contracts
            ]

            return contracts
        return []

    def search_related_contract_api(self) -> Union[dict[any] | dict[None]]:
        contract = self.db_session.query(Contract).filter_by(id=self.search).first()
        if contract:
            contract = dict(
                id=contract.id,
                contract_number=contract.contract_number,
                date=contract.date,
                amount=contract.amount,
                remained_amount=contract.remained_amount,
                adv_payer=contract.adv_payer,
                pdf_file=None
            )
            return contract
        return {}


class EditContract(ValidatorWrapper):
    def __init__(self, db_session: Session, contract_id: int):
        super().__init__(db_session)
        self.id = contract_id

    # Helpers methods for update logic
    def is_company_exists(self, company_name: str) -> int | bool:
        """
            Checks if the company exists in the database. If it exists then update the contract foreign key to the other
            company and voen else flash error
        """
        result = self.db_session.query(Companies).filter_by(company_name=company_name).first()
        return result.id if result else False

    def is_voen_exists(self, voen_result: str) -> int | bool:
        """
               Checks if the voen exists in the database. If it exists then update the contract foreign key to the other
               company and voen else flash error
               """
        result = self.db_session.query(Companies).filter_by(voen=voen_result).first()
        return result.id if result else False

    def voen_and_company_matched(self, company_name: str, voen_result: str) -> int | bool:
        """

        """
        result = self.db_session.query(Companies).filter_by(company_name=company_name, voen=voen_result).first()
        return result.id if result else False

    def change_pdf_file_path(self, company_id: int, old_file_path: str) -> str:
        """
        :param company_id:
        :param old_file_path:
        :return: str
        The method which help to change the pdf file path
        """
        new_company_name = self.db_session.query(Companies).where(Companies.id == company_id).first().company_name

        company_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_company_name)
        company_upload_path = os.path.normpath(company_upload_path)

        old_file_path = os.path.normpath(old_file_path)
        old_file_pattern = r'(?<=\\contracts\\)[^\\]+(?=\\)'
        new_file_path = os.path.join(str(company_upload_path),
                                     os.path.basename(re.sub(old_file_pattern, new_company_name, old_file_path)))
        os.rename(old_file_path, new_file_path)
        new_file_path = os.path.normpath(new_file_path)
        return new_file_path

    @staticmethod
    def change_pdf_itself(previous_pdf_file_path: str, new_pdf_file_name: str) -> str:
        """
        :param previous_pdf_file_path:
        :param new_pdf_file_name:
        :return: str:
        Help to change pdf in the main folder logic of upload files of contracts
        """
        new_pdf_path = os.path.join(os.path.dirname(previous_pdf_file_path), new_pdf_file_name)
        new_pdf_path = os.path.normpath(new_pdf_path)
        os.remove(previous_pdf_file_path)
        return new_pdf_path

    # Helpers methods for update logic
    #  Main update logic is here
    def update_data(self, changes: dict, pdf_file: flask) -> tuple[bool, str]:
        """
        :param changes:
        :param pdf_file:
        :return: tuple[bool, str]
        The main update logic after contract's edit. it will check all the possibilities of updating or refuse the
            contract to update based on different situations
        """
        update_status = {'company_and_voen_updated': False}
        contract_to_update = self.db_session.query(Contract).join(Contract.company).filter(
            Contract.id == int(self.id)).with_for_update().first()
        if not contract_to_update:
            self.db_session.close()
            return False, f"Contract was not found in database"
        try:
            company_name = changes.get("company_name")
            voen = changes.get("voen")
            if voen != contract_to_update.company.voen and company_name != contract_to_update.company.company_name:
                existed_company_id = self.voen_and_company_matched(company_name, voen)
                if existed_company_id:
                    contract_to_update.company_id = existed_company_id
                    update_status["company_and_voen_updated"] = True
                else:
                    return False, ("The provided company name and VOEN do not match to any existing company. "
                                   "Please check your information or create a new company record.")
            for key, value in changes.items():
                if hasattr(contract_to_update.company, key) and not update_status["company_and_voen_updated"]:
                    current_value = getattr(contract_to_update.company, key)
                    if current_value != value:
                        match key:
                            case "company_name":
                                existed_company_id = self.is_company_exists(value)
                                if existed_company_id:
                                    try:
                                        new_pdf_file_path = self.change_pdf_file_path(existed_company_id,
                                                                                      contract_to_update.pdf_file_path,
                                                                                      )
                                        contract_to_update.company_id = existed_company_id
                                        contract_to_update.pdf_file_path = new_pdf_file_path
                                    except FileNotFoundError:
                                        return False, (
                                            "There is the file path problem. It was corrupted or not existed."
                                            "Please, load a new pdf first")
                                else:
                                    return False, (
                                        f"There is no such company in the database or remained amount is corrupted: {value}.Please go to the"
                                        f" create contract form page")
                            case "voen":
                                existed_voen_id = self.is_voen_exists(value)
                                if existed_voen_id:
                                    try:
                                        new_pdf_file_path = self.change_pdf_file_path(existed_voen_id,
                                                                                      contract_to_update.pdf_file_path,
                                                                                      )
                                        contract_to_update.company_id = existed_voen_id
                                        contract_to_update.pdf_file_path = new_pdf_file_path
                                    except FileNotFoundError:
                                        return False, (
                                            "There is the file path problem. It was corrupted or not existed."
                                            "Please, load a new pdf first")
                                else:
                                    return False, (f"There is no such voen related to any company in the database: "
                                                   f"{value}.Please go to the"
                                                   f"create contract form page")
                elif hasattr(contract_to_update, key):
                    current_value = getattr(contract_to_update, key)
                    if key == "pdf_file_path":
                        if value is not None:
                            try:
                                new_pdf_path = self.change_pdf_itself(current_value, value)
                                setattr(contract_to_update, key, new_pdf_path)
                                pdf_file.save(new_pdf_path)
                            except FileNotFoundError:
                                return False, "There is the file path problem. It was corrupted or not existed."
                    else:
                        setattr(contract_to_update, key, value)

            return True, f"Contract updated successfully"
        except sqlalchemy.exc.DBAPIError as e:
            self.db_session.rollback()
            return False, f"An error occurred in the server. Please try again later"


class CompanyManager(ContractManager):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    @staticmethod
    def delete_pdf_folder(company_name: str) -> None:
        base_path = f"./uploads/contracts/{company_name}"
        if os.path.exists(base_path):
            try:
                shutil.rmtree(base_path)
            except OSError:
                raise FileNotFoundError()

    @staticmethod
    def create_pdf_folder(company_name: str) -> None:
        """
        :param company_name:
        :return:
        """
        base_path = f"./uploads/contracts/{company_name}"
        if os.path.exists(base_path):
            return
        os.makedirs(base_path)

    def delete_company(self, company_id: int) -> bool:
        """
        :param company_id:
        :return: bool
        delete company method which also delete all the files from related to contracts and acts related to contracts
        """
        company = self.db_session.query(Companies).filter_by(id=company_id).first()
        contracts = company.contracts
        if company:
            try:
                self.delete_pdf_folder(str(company.company_name))
                for contract in contracts:
                    self.delete_related_acts_pdf_file(contract)
                    self.delete_related_additions_pdf_file(contract)
                self.db_session.delete(company)
                return True
            except DBAPIError:
                return False
            except FileNotFoundError:
                return False
        return False

    def check_swift(self, swift_code: str) -> bool | ValueError:
        """
        :param swift_code:
        :return: bool or ValueError
        """
        if not swift_code:
            return False
        swift_code_query = self.db_session.query(Companies).filter_by(swift=swift_code).first()
        if swift_code_query:
            raise ValueError(
                f"Invalid swift code: {swift_code}. It is already linked to a {swift_code_query.company_name} company") \
                if swift_code_query is not None else False
        return False

    def get_or_create_company(self, company_name: str, voen: str, company_data=None, *args, **kwargs) -> None:
        """

        :param company_name:
        :param voen:
        :param company_data:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            company = self.db_session.query(Companies).filter_by(company_name=company_name).one()
            if company.voen != voen:
                raise ValueError(f"The {company_name} company already has a voen {company.voen}")

            for key, value in company_data.items():
                if value is not None:
                    setattr(company, key, value)
        except NoResultFound:
            if self.check_voen(voen):
                raise ValueError(
                    f"VOEN is already linked to {self.db_session.query(Companies).filter_by(voen=voen).one().company_name} company")
            else:
                company = Companies(
                    company_name=company_name,
                    voen=voen,
                    bank_name=company_data['bank_name'],
                    m_h=company_data['m_h'],
                    h_h=company_data['h_h'],
                    swift=company_data['swift'],
                    email=company_data['email'],
                    telephone_number=company_data['telephone_number'],
                    address=company_data['address'],
                    website=company_data['website']
                )
                self.db_session.add(company)
                self.create_pdf_folder(company_name)


class CompanySearchEngine(SearchEngine):
    def __init__(self, db_session: Session, search: str = None):
        super().__init__(db_session, search)

    def search_company(self) -> Type[Companies]:
        result = self.db_session.query(Companies).filter_by(id=self.search).one()
        try:
            return result
        except NoResultFound:
            raise NoResultFound

    def get_all_results_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
         :param per_page:
         :param offset:
         :param sort_dir:
         :param mapping:
         :return:
         This method is for put all results of the contract in the table
        """
        query = (self.db_session.query(Companies, func.count(Contract.id).label("contract_count"))
                 .outerjoin(Contract, Companies.contracts).group_by(Companies.id))
        if mapping[0] == "related_contracts":
            match sort_dir:
                case "asc":
                    query = query.order_by(asc("contract_count"))
                case "desc":
                    query = query.order_by(desc("contract_count"))
        else:
            query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        companies = query.offset(offset).limit(per_page).all()
        company_list = [{
            "id": company[0].id,
            "company_name": company[0].company_name,
            "voen": company[0].voen,
            "related_contracts": company[1]
        } for company in companies]
        return company_list, total_count

    def search_query_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param per_page:
        :param offset:
        :param sort_dir:
        :param mapping:
        :return:
        """

        query = (self.db_session
        .query(Companies, func.count(Contract.id).label("contract_count"))
        .outerjoin(Contract, Companies.contracts).group_by(Companies.id)
        .filter(or_(
            Companies.company_name.ilike(f"%{self.search}%"),
            Companies.voen.ilike(f"%{self.search}%"),
        )))
        if mapping[0] == "related_contracts":
            match sort_dir:
                case "asc":
                    query = query.order_by(asc("contract_count"))
                case "desc":
                    query = query.order_by(desc("contract_count"))
        else:
            query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        companies = query.offset(offset).limit(per_page).all()
        company_list = [{
            "id": company[0].id,
            "company_name": company[0].company_name,
            "voen": company[0].voen,
            "related_contracts": company[1]
        } for company in companies]
        return company_list, total_count


class EditCompany(EditContract):
    def __init__(self, db_session: Session, company_id: int):
        super().__init__(db_session, company_id)
        self.company_id = company_id

    def update_company_voen_or_swift(self, key: str, value: str | int) -> InstrumentedAttribute | None:
        result = self.db_session.query(Companies).filter_by(**{key: value}).first()
        if result:
            return result.company_name
        return None

    @staticmethod
    def update_folder(new_company_name: str, old_company_name: str) -> bool:
        base_dir = "./uploads/contracts/"
        subfolders = os.listdir('./uploads/contracts/')
        for folder in subfolders:
            if folder == old_company_name:
                os.rename(f'{base_dir}{folder}', f'{base_dir}{new_company_name}')
                return True
        return False
        # if company:

    @staticmethod
    def update_path(contract, new_company_name: str) -> None:
        pattern = re.compile(r'(?<=\\contracts\\)[^\\]+(?=\\)')
        updated_path = pattern.sub(new_company_name, contract.pdf_file_path)
        setattr(contract, 'pdf_file_path', updated_path)

    def update_company_pdf_and_path(self, new_company_name: str, old_company_name: str) -> None:
        company = self.db_session.query(Companies).filter_by(company_name=new_company_name).first()
        folder_updated = self.update_folder(new_company_name, old_company_name)
        if folder_updated:
            related_contracts = company.contracts
            list(map(lambda contract: self.update_path(contract, new_company_name), related_contracts))

    def update_data(self, changes: dict, pdf_file: flask = None, *args, **kwargs) -> tuple[bool, str]:
        """
            The main update logic after company's edit. it will check all the possibilities of updating or refuse the
            company to update based on different situations
        """
        company_to_update = self.db_session.query(Companies).filter_by(id=self.company_id).first()
        if not company_to_update:
            return False, f"Contract was not found in database"
        company_to_update_dict = {column.name: getattr(company_to_update, column.name) for column in
                                  company_to_update.__table__.columns}
        for key, value in changes.items():
            try:
                if value != company_to_update_dict[key]:
                    if key in ["voen", "swift", "company_name"]:
                        check_voen_or_swift = self.update_company_voen_or_swift(key, value)
                        if check_voen_or_swift:
                            return False, f"This {key} is already linked to {check_voen_or_swift}."
                        setattr(company_to_update, key, value)
                        if key == "company_name":
                            self.update_company_pdf_and_path(value, company_to_update_dict["company_name"])

                    setattr(company_to_update, key, value)
                else:
                    continue
            except sqlalchemy.exc.DBAPIError:
                self.db_session.rollback()
                return False, "An error occurred with the database. Please try again later"
        self.db_session.commit()
        return True, "The contract was updated successfully"


class ActsManager(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create_act(self, acts_info_dict: dict) -> None:
        act = Acts(**acts_info_dict)
        self.db_session.add(act)

    def delete_pdf_file(self, act_id: int) -> None:
        act = self.db_session.query(Acts).filter_by(id=act_id).first()
        if act:
            try:
                act_pdf_path = act.pdf_file_path
                os.remove(act_pdf_path)
            except FileNotFoundError:
                raise FileNotFoundError("Pdf file is not found")

    def delete_act(self, act_id: int) -> bool:
        """
            :param act_id:
            :return: bool
            The method which is help to delete the act
        """
        act = self.db_session.query(Acts).filter_by(id=act_id).first()
        if act:
            try:
                related_contract = act.contract.id
                self.delete_pdf_file(act_id)
                self.add_amount_to_contract(related_contract, act.amount)
                self.db_session.delete(act)
                return True
            except DBAPIError:
                return False
            except FileNotFoundError:
                return False
            except NoResultFound:
                return False
            except AttributeError:
                return False
        return False

    def add_amount_to_contract(self, contract_id: int, act_amount: float):
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            new_remained_amount = contract.remained_amount + act_amount
            contract.remained_amount = new_remained_amount
        else:
            raise NoResultFound


class ActsSearchEngine(SearchEngine):
    def __init__(self, db_session: Session, act_id: int = None, contract_id: int = None, search: str | int = None):
        super().__init__(db_session, search)
        self.contract_id = contract_id
        self.act_id = act_id

    def get_all_results_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> tuple[
        list[dict[str, InstrumentedAttribute | Any]], int]:
        """
                :param mapping:
                :param sort_dir:
                :param offset:
                :param per_page:
                :return: list[dict[str, InstrumentedAttribute | Any]]
                This method is for put all results of the related acts in the table
                """
        query = self.db_session.query(Acts).filter_by(contract_id=self.contract_id)

        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        acts = query.offset(offset).limit(per_page).all()
        acts_list = [{
            "id": act.id,
            "act_number": act.act_number,
            "date": act.date,
            "amount": float(act.amount),
        } for act in acts]
        return acts_list, total_count

    def search_query_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param per_page:
        :param offset:
        :param sort_dir:
        :param mapping:
        :return:
        """
        query = (self.db_session
        .query(Acts)
        .filter_by(contract_id=self.contract_id)
        .join(Contract, Contract.id == Acts.contract_id)
        .filter(or_(
            Acts.act_number.ilike(f"%{self.search}%"),
            Acts.amount.ilike(f"%{self.search}%"),
            Acts.date.ilike(f"%{self.search}%"),
        )))

        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        acts = query.offset(offset).limit(per_page).all()
        acts_list = [{
            "id": act.id,
            "act_number": act.act_number,
            "date": act.date,
            "amount": float(act.amount),
        } for act in acts]
        return acts_list, total_count

    def search_act(self):
        query = self.db_session.query(Acts).filter_by(id=self.act_id).first()
        if query:
            return query

        raise NoResultFound

    def search_related_contract_amount(self, contract_id: int) -> float:
        """
        :param contract_id:
        :return:
        """
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            return contract.remained_amount
        raise NoResultFound

    def decrease_amount(self, contract_id: int, remained_amount: float) -> None:
        """
        :param contract_id:
        :param remained_amount:
        :return None:
        """
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                contract.remained_amount = remained_amount
            except DBAPIError:
                raise DBAPIError
            except OperationalError:
                raise OperationalError
        else:
            raise NoResultFound

    def decrease_or_increase_difference_amount(self, contract_id: int, remained_amount: float) -> None:
        """
        :param contract_id:
        :param remained_amount:
        :return None:
        """
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                contract.remained_amount -= remained_amount
            except DBAPIError:
                raise DBAPIError
            except OperationalError:
                raise OperationalError
        else:
            raise NoResultFound

    def add_amount(self, contract_id: int, difference: float):
        """
        :param contract_id:
        :param difference:
        :return:
        """
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                contract.remained_amount -= difference
            except DBAPIError:
                raise DBAPIError
            except OperationalError:
                raise OperationalError
        else:
            raise NoResultFound


class EditAct(EditContract):
    def __init__(self, db_session: Session, act_id: int):
        super().__init__(db_session, act_id)
        self.act_id = act_id

    def change_amount(self, old_contract_id: int, new_contract_id: int, act_amount: float,
                      old_act_amount: float) -> None:
        """
        :param old_contract_id:
        :param new_contract_id:
        :param act_amount:
        :return:
        Proper change of the amount during contract changes
        """
        old_contract = self.db_session.query(Contract).filter_by(id=old_contract_id).first()
        new_contract = self.db_session.query(Contract).filter_by(id=new_contract_id).first()
        if not old_contract and not new_contract:
            raise NoResultFound

        try:
            check_amount(act_amount, new_contract.remained_amount)
            old_contract.remained_amount += old_act_amount
            new_contract.remained_amount -= act_amount
        except ValueError:
            raise ValueError

    def update_data(self, changes: dict, pdf_file: flask = None, *args, **kwargs) -> tuple[bool, str]:
        """
        :param changes:
        :param pdf_file:
        :param args:
        :param kwargs:
        :return: tuple[bool, str]:
        The main update logic after contract's edit. it will check all the possibilities of updating or refuse the
        contract to update based on different situations
        """
        act_to_update = self.db_session.query(Acts).filter_by(id=self.act_id).first()
        if not act_to_update:
            return False, f"Act was not found in database"
        act_to_update_dict = {column.name: getattr(act_to_update, column.name) for column in
                              act_to_update.__table__.columns}
        for key, value in changes.items():
            try:
                if value != act_to_update_dict[key] and value is not None:
                    if key == "pdf_file_path":
                        try:
                            new_pdf_path = self.change_pdf_itself(act_to_update_dict[key], value)
                            setattr(act_to_update, key, new_pdf_path)
                            pdf_file.save(new_pdf_path)
                        except FileNotFoundError:
                            return False, "There is the file path problem. It was corrupted or not existed."
                    elif key == "contract_id":
                        try:
                            setattr(act_to_update, key, value)
                            old_contract = act_to_update_dict["contract_id"]
                            old_act_amount = act_to_update_dict["amount"]
                            new_act_amount = changes["amount"]

                            self.change_amount(old_contract, value, new_act_amount, old_act_amount)
                        except NoResultFound:
                            return False, "There is no such contract in db."
                        except ValueError:
                            return False, "The contract's you want to link the act is smaller than act's amount."
                        except (DBAPIError, OperationalError):
                            self.db_session.rollback()
                            return False, "An error occurred with the database. Please try again later"
                    else:
                        setattr(act_to_update, key, value)
                else:
                    continue
            except sqlalchemy.exc.DBAPIError:
                self.db_session.rollback()
                return False, "An error occurred with the database. Please try again later"
        return True, "The act was updated successfully"


class CategoriesManager(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def add_category(self, category_name: str) -> None:
        """
        :param category_name:
        :return:
        """
        try:
            category = Category(category_name=category_name)
            self.db_session.add(category)
            self.db_session.commit()
        except SQLAlchemyError:
            self.db_session.rollback()
            raise SQLAlchemyError

    def all_categories(self) -> list[dict[str]]:
        """
        :return list[Any]:
        """
        categories = self.db_session.query(Category).all()
        category_list = [{
            "id": category.id,
            "category_name": category.category_name
        } for category in categories]
        return category_list

    def delete_category(self, category_id: int) -> None:
        """
        :param category_id:
        :return:
        """
        query = self.db_session.query(Category).filter_by(id=category_id).first()
        if query:
            try:
                self.db_session.delete(query)
                self.db_session.commit()
            except SQLAlchemyError:
                self.db_session.rollback()
                raise SQLAlchemyError


class CategoriesSearchEngine(SearchEngine):
    def __init__(self, db_session: Session, search: str | int = None):
        super().__init__(db_session, search)

    def search_query_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
                :param per_page:
                :param offset:
                :param sort_dir:
                :param mapping:
                :return:
                """

        query = (self.db_session
        .query(Category)
        .filter(
            Category.category_name.ilike(f"%{self.search}%"),
        ))

        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        categories = query.offset(offset).limit(per_page).all()
        category_list = [{
            "id": category.id,
            "category_name": category.category_name,
        } for category in categories]
        return category_list, total_count

    def get_all_results_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> tuple[
        list[dict[str, InstrumentedAttribute | Any]], int]:
        """
                :param mapping:
                :param sort_dir:
                :param offset:
                :param per_page:
                :return: list[dict[str, InstrumentedAttribute | Any]]
                This method is for put all results of the contract in the table
                """
        query = (self.db_session.query(Category))
        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        categories = query.offset(offset).limit(per_page).all()
        category_list = [{
            "id": category.id,
            "category_name": category.category_name,
        } for category in categories]
        return category_list, total_count

    def search_category(self):
        query = self.db_session.query(Category).filter_by(id=self.search).first()
        if query:
            return query

        raise NoResultFound


class EditCategory(EditContract):
    def __init__(self, db_session: Session, category_id: int):
        super().__init__(db_session, category_id)
        self.category_id = category_id

    def category_update(self, new_category_name: str) -> bool:
        category = self.db_session.query(Category).filter_by(id=self.category_id).first()
        if category:
            category.category_name = new_category_name
            self.db_session.commit()
            return True
        self.db_session.rollback()
        raise NoResultFound


class AdditionManager(ActsManager):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def create_addition(self, addition_info_dict: dict) -> None:
        addition = Additions(**addition_info_dict)
        self.db_session.add(addition)

    def delete_pdf_file(self, addition_id: int) -> None:
        addition = self.db_session.query(Additions).filter_by(id=addition_id).first()
        if addition:
            try:
                act_pdf_path = addition.pdf_file_path
                os.remove(act_pdf_path)
            except FileNotFoundError:
                raise FileNotFoundError("Pdf file is not found")

    def decrease_amount_from_contract(self, contract_id: int, addition_amount: float):
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            acts_amount = sum(act.amount for act in contract.acts)
            new_contract_amount = contract.amount - addition_amount - acts_amount
            if new_contract_amount < 0:
                raise ValueError
            contract.amount -= addition_amount
            contract.remained_amount -= addition_amount
        else:
            raise NoResultFound

    def delete_addition(self, addition_id: int) -> bool:
        """
            :param act_id:
            :return: bool
            The method which is help to delete the addition
        """
        addition = self.db_session.query(Additions).filter_by(id=addition_id).first()
        if addition:
            try:
                related_contract = addition.contract.id
                self.decrease_amount_from_contract(related_contract, addition.amount)
                self.delete_pdf_file(addition_id)
                self.db_session.delete(addition)
                return True
            except DBAPIError:
                return False
            except FileNotFoundError:
                return False
            except NoResultFound:
                return False
            except AttributeError:
                return False
            except ValueError:
                raise ValueError
        return False


class AdditionSearchEngine(ActsSearchEngine):
    def __init__(self, db_session: Session, addition_id: int = None, contract_id: int = None, search: str | int = None):
        super().__init__(db_session, contract_id=contract_id, search=search)
        self.addition_id = addition_id

    def increase_amount(self, contract_id: int, addition: float) -> None:
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                contract.remained_amount += addition
                contract.amount += addition
            except DBAPIError:
                raise DBAPIError
            except OperationalError:
                raise OperationalError
        else:
            raise NoResultFound

    def get_all_results_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> tuple[
        list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param per_page:
        :param offset:
        :param sort_dir:
        :param mapping:
        :return:
        """
        query = self.db_session.query(Additions).filter_by(contract_id=self.contract_id)

        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        additions = query.offset(offset).limit(per_page).all()
        addition_list = [{
            "id": addition.id,
            "addition_number": addition.addition_number,
            "date": addition.date,
            "amount": float(addition.amount),
        } for addition in additions]
        return addition_list, total_count

    def search_query_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param per_page:
        :param offset:
        :param sort_dir:
        :param mapping:
        :return:
        """
        query = (self.db_session
        .query(Additions)
        .filter_by(contract_id=self.contract_id)
        .join(Contract, Contract.id == Additions.contract_id)
        .filter(or_(
            Additions.addition_number.ilike(f"%{self.search}%"),
            Additions.amount.ilike(f"%{self.search}%"),
            Additions.date.ilike(f"%{self.search}%"),
        )))

        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        additions = query.offset(offset).limit(per_page).all()
        addition_list = [{
            "id": addition.id,
            "addition_number": addition.addition_number,
            "date": addition.date,
            "amount": float(addition.amount),
        } for addition in additions]
        return addition_list, total_count

    def search_addition(self) -> Type[Additions]:
        query = self.db_session.query(Additions).filter_by(id=self.addition_id).first()
        if query:
            return query

        raise NoResultFound


class EditAddition(EditContract):
    def __init__(self, db_session: Session, addition_id: int):
        super().__init__(db_session, addition_id)
        self.addition_id = addition_id

    def change_old_contract(self, remained_amount: float, new_total_amount: float, contract_id: int) -> None:
        """
        :param remained_amount:
        :param new_total_amount:
        :param contract_id:
        :return: None
        Just change the total and remained amount of old contract from where the addition was moved.
        """
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            contract.remained_amount = remained_amount
            contract.amount = new_total_amount
        raise NoResultFound

    def change_amount(self, old_contract_id: int, new_contract_id: int, addition_amount: float,
                      old_addition_amount: float) -> None:
        """
        :param old_contract_id:
        :param new_contract_id:
        :param addition_amount:
        :param old_addition_amount:
        :return:
        Proper change of the amount during contract changes
        """
        old_contract = self.db_session.query(Contract).filter_by(id=old_contract_id).first()
        new_contract = self.db_session.query(Contract).filter_by(id=new_contract_id).first()
        if not old_contract and not new_contract:
            raise NoResultFound
        old_contract.remained_amount -= old_addition_amount
        old_contract.amount -= old_addition_amount
        if old_contract.remained_amount < 0:
            raise NegativeAmountError
        new_contract.remained_amount += addition_amount
        new_contract.amount += addition_amount

    def update_data(self, changes: dict, pdf_file: flask) -> tuple[bool, str]:
        """
        :param changes:
        :param pdf_file:
        :return: tuple[bool, str]
        """
        addition_to_update = self.db_session.query(Additions).filter_by(id=self.addition_id).first()
        if not addition_to_update:
            return False, f"Act was not found in database"
        addition_to_update_dict = {column.name: getattr(addition_to_update, column.name) for column in
                                   addition_to_update.__table__.columns}
        for key, value in changes.items():
            try:
                if value != addition_to_update_dict[key] and value is not None:
                    if key == "pdf_file_path":
                        try:
                            new_pdf_path = self.change_pdf_itself(addition_to_update_dict[key], value)
                            setattr(addition_to_update, key, new_pdf_path)
                            pdf_file.save(new_pdf_path)
                        except FileNotFoundError:
                            return False, "There is the file path problem. It was corrupted or not existed."
                    elif key == "contract_id":
                        try:
                            setattr(addition_to_update, key, value)
                            old_contract = addition_to_update_dict["contract_id"]
                            old_addition_amount = addition_to_update_dict["amount"]
                            new_addition_amount = changes["amount"]

                            self.change_amount(old_contract, value, new_addition_amount, old_addition_amount)
                        except NoResultFound:
                            return False, "There is no such contract in db."
                        except NegativeAmountError:
                            return False, "Please check acts and make necessary changes in order to make acts refer to contracts."
                        except ValueError:
                            return False, "The contract's you want to link the act is smaller than act's amount."
                        except (DBAPIError, OperationalError):
                            self.db_session.rollback()
                            return False, "An error occurred with the database. Please try again later"
                    else:
                        setattr(addition_to_update, key, value)
                else:
                    continue
            except sqlalchemy.exc.DBAPIError:
                self.db_session.rollback()
                return False, "An error occurred with the database. Please try again later"
        return True, "The act was updated successfully"


class DashBoard(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    @staticmethod
    def check_days_left(contract_date: Contract.end_date, today_date: datetime.today) -> datetime.date:
        """
        :param contract_date
        :param today_date:
        :return datetime.date:
        Calculates days left for ending contracts
        """
        return abs((today_date - contract_date).days)

    def get_card_information(self) -> dict:
        """
        :return: dict
        Get card information api for the tables in dashboard
        """
        total_contracts = self.db_session.query(Contract).count()
        total_companies = self.db_session.query(Companies).count()
        total_acts = self.db_session.query(Acts).count()
        total_additions = self.db_session.query(Additions).count()
        return {
            "total_contracts": total_contracts,
            "total_companies": total_companies,
            "total_acts": total_acts,
            "total_additions": total_additions,
        }

    def get_card_inf_apiget_contracts_information_date_api(self, per_page: int, offset: int) -> dict:
        """
        :param per_page:
        :param offset:
        :return: dict
        Get card information api for the tables in dashboard
        """
        today = datetime.today().date()
        end_date_threshold = today + timedelta(days=90)
        contracts_in_ending = ((self.db_session.query(Contract)
                                .filter(Contract.end_date <= end_date_threshold, Contract.end_date >= today))
        )
        total_count = contracts_in_ending.count()
        filtered_contracts = contracts_in_ending.order_by(Contract.end_date.asc()).offset(offset).limit(per_page)
        return {
            "total_count": total_count,
            "contracts_to_end": [{
                "offset": offset,
                "company_name": contract.company.company_name,
                "contract_name": contract.contract_number,
                "contract_days_left": self.check_days_left(contract.end_date, today)
            } for contract in filtered_contracts]
        }

    def get_contracts_information_amount_api(self, per_page: int, offset: int) -> dict:
        """
        :param per_page:
        :param offset:
        :return: dict
        Get card information api for the tables in dashboard
        """
        percentage = PERCENTAGE_AMOUNT
        contracts = self.db_session.query(Contract,
                                          (cast(Contract.remained_amount, Float) / cast(Contract.amount, Float) * 100)
                                          .label('percentage_remained')).order_by(Contract.remained_amount.asc()).all()
        filtered_contracts = []
        for contract, remained_amount in contracts:
            if remained_amount <= PERCENTAGE_AMOUNT:
                filtered_contracts.append(contract)
            continue
        total_count = len(filtered_contracts)
        filtered_contracts = filtered_contracts[offset: offset + per_page]
        return {
            "total_count": total_count,
            "contracts_to_end": [{
                "offset": offset,
                "company_name": contract.company.company_name,
                "contract_name": contract.contract_number,
                "contract_amount_left": contract.remained_amount
            } for contract in filtered_contracts]
        }


class UserManager(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def is_user_existed(self, username: str) -> bool:
        """
        :param username:
        :return: bool
        Simple checking of user's existence
        """
        query = self.db_session.query(User).filter(User.username == username).first()
        if query:
            return True if query.username == username else False
        return False

    def delete_user(self, user_id: str):
        try:
            query = self.db_session.query(User).filter(User.id == user_id).first()
            print(query.username)
            if query:
                self.db_session.delete(query)
            else:
                raise NoResultFound
        except OperationalError:
            raise OperationalError


class UserSearchEngine(SearchEngine):
    def __init__(self, db_session: Session, search: str | int = None):
        super().__init__(db_session, search)

    def get_all_results_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> tuple[
        list[dict[str, InstrumentedAttribute | Any]], int]:
        """
                :param mapping:
                :param sort_dir:
                :param offset:
                :param per_page:
                :return: list[dict[str, InstrumentedAttribute | Any]]
                This method is for put all results of the users in the table
                """
        query = self.db_session.query(User).filter(User.username != current_user.username)
        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        users = query.offset(offset).limit(per_page).all()
        user_list = [{
            "id": user.id,
            "user_name": user.username,
            "role": user.role
        } for user in users]
        return user_list, total_count

    def search_query_api(self, per_page: int, offset: int, sort_dir: str, mapping: tuple) -> (
            tuple)[list[dict[str, InstrumentedAttribute | Any]], int]:
        """
        :param mapping:
        :param sort_dir:
        :param offset:
        :param per_page:
        :return: list[dict[str, InstrumentedAttribute | Any]]
        server-side search from db directly to user table via api
        """
        query = (self.db_session
        .query(User)
        .filter(User.username != current_user.username, or_(
            User.username.ilike(f"%{self.search}%"),
            User.role.ilike(f"%{self.search}%"),
        )))

        query = self.asc_or_desc(query, sort_dir, mapping)
        total_count = query.count()
        users = query.offset(offset).limit(per_page).all()
        user_list = [{
            "id": user.id,
            "user_name": user.username,
            "role": user.role
        } for user in users]
        return user_list, total_count
