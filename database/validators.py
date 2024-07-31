import re
from typing import Any, Type, List, Dict
import os
import shutil
import flask
import sqlalchemy
from flask import current_app
from flask_sqlalchemy.session import Session
from sqlalchemy import or_, desc, asc, func, and_
from sqlalchemy.exc import NoResultFound, SQLAlchemyError, DBAPIError
from sqlalchemy.orm import InstrumentedAttribute
from database.models import *
from abc import ABC
from database.models import Companies


class ValidatorWrapper(ABC):
    def __init__(self, db_session: Session):
        self.db_session = db_session


class ContractManager(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def delete_pdf_file(self, contract_id: int) -> None:
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                contract_pdf_path = str(contract.pdf_file_path)
                os.remove(contract_pdf_path)
            except FileNotFoundError:
                raise FileNotFoundError("Pdf file is not found")

    def delete_contract(self, contract_id: int) -> bool:
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                self.delete_pdf_file(contract_id)
                self.db_session.delete(contract)
                return True
            except DBAPIError:
                return False
            except FileNotFoundError:
                return False
        return False

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
            "adv_payer": bool(contract.adv_payer)
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
        .filter(or_(
            Companies.company_name.ilike(f"%{self.search}%"),
            Companies.voen.ilike(f"%{self.search}%"),
            Contract.contract_number.ilike(f"%{self.search}%"),
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
            "amount": contract.amount,
            "adv_payer": bool(contract.adv_payer)
        } for contract in contracts]
        return contract_list, total_count


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
        """
        new_company_name = self.db_session.query(Companies).where(Companies.id == company_id).first().company_name
        new_company_voen = self.db_session.query(Companies).where(Companies.id == company_id).first().voen
        company_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_company_name)
        company_upload_path = os.path.normpath(company_upload_path)
        old_file_path = os.path.normpath(old_file_path)
        new_file_path = os.path.join(str(company_upload_path), os.path.basename(re.sub(r"_\d{10}_",
                                                                                       f"_{new_company_voen}_",
                                                                                       old_file_path)))
        os.rename(old_file_path, new_file_path)
        new_file_path = os.path.normpath(new_file_path)
        return new_file_path

    @staticmethod
    def change_pdf_itself(previous_pdf_file_path: str, new_pdf_file_name: str) -> str:
        """
        :param previous_pdf_file_path:
        :param new_pdf_file_name:
        :return: str
        """
        new_pdf_path = os.path.join(os.path.dirname(previous_pdf_file_path), new_pdf_file_name)
        new_pdf_path = os.path.normpath(new_pdf_path)
        os.remove(previous_pdf_file_path)
        return new_pdf_path

    # Helpers methods for update logic

    #  Main update logic is here
    def update_data(self, changes: dict, pdf_file: flask) -> tuple[bool, str]:
        """
            The main update logic after contract's edit. it will check all the possibilities of updating or refuse the
            contract to update based on different situations
        """
        update_status = {'company_and_voen_updated': False}
        contract_to_update = self.db_session.query(Contract).join(Contract.company).filter(
            Contract.id == int(self.id)).first()
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
                                    return False, (f"There is no such company in the database: {value}.Please go to the"
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

            self.db_session.commit()
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
        """
        company = self.db_session.query(Companies).filter_by(id=company_id).first()
        if company:
            try:
                self.delete_pdf_folder(str(company.company_name))
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

    def update_company_pdf_and_path(self, new_company_name: str, old_company_name: str) -> None:
        company = self.db_session.query(Companies).filter_by(company_name=new_company_name).first()
        folder_updated = self.update_folder(new_company_name, old_company_name)
        if folder_updated:
            print(f'Updated {new_company_name}')
            related_contracts = company.contracts
            list(map(lambda contract: setattr(contract, "pdf_file_path",
                                              re.sub(r'(?<=\\contracts\\)[^\\]+(?=\\)',
                                                     new_company_name, contract.pdf_file_path)),
                     related_contracts))

    def update_data(self, changes: dict, pdf_file: flask = None, *args, **kwargs) -> tuple[bool, str]:
        """
                    The main update logic after company's edit. it will check all the possibilities of updating or refuse the
                    company to update based on different situations
                """
        company_to_update = self.db_session.query(Companies).filter_by(id=self.id).first()
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
