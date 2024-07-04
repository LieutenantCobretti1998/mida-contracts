import re
from typing import Any, Type
import os
import flask
import sqlalchemy
from flask import current_app
from flask_sqlalchemy.session import Session
from sqlalchemy import or_, desc, asc, func
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
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

    def delete_contract(self, contract_id: int) -> bool:
        contract = self.db_session.query(Contract).filter_by(id=contract_id).first()
        if contract:
            try:
                self.db_session.delete(contract)
                self.db_session.commit()
                return True
            except Exception:
                self.db_session.rollback()
                return False



    def get_or_create_company(self, company_name: str, voen: str, *args, **kwargs) -> None | Type[
        Companies] | Companies:
        if not company_name:
            return None

        try:
            company = self.db_session.query(Companies).filter_by(company_name=company_name).one()
            if company.voen != voen:
                raise ValueError(f"The {company_name} company already has a voen {company.voen}")
            return company
        except NoResultFound:
            if self.check_voen(voen):
                raise ValueError(
                    f"VOEN is already linked to {self.db_session.query(Companies).filter_by(voen=voen).one().company_name} company")
            company = Companies(company_name=company_name, voen=voen)
            self.db_session.add(company)
            return company

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
    def __init__(self, db_session: Session, search: str | int = None):
        super().__init__(db_session)
        self.search = search

    def search_query(self, page: int, per_page: int, filters: str, order: str) -> dict:
        # results = self.db_session.query(Companies).join(Contract).filter(or_(
        #     Companies.company_name.ilike(f"%{self.search}%"),
        #     Companies.voen.ilike(f"%{self.search}%"),
        #     Contract.contract_number.ilike(f"%{self.search}%")
        # )).all()
        results = self.db_session.query(Contract).join(Contract.company).filter(or_(
            Companies.company_name.ilike(f"%{self.search}%"),
            Companies.voen.ilike(f"%{self.search}%"),
            Contract.contract_number.ilike(f"%{self.search}%"),
        ))
        # Filters
        match filters:
            case "company":
                results = results.order_by(desc(Companies.company_name) if order == "descending"
                                           else asc(Companies.company_name))

            case "date":
                results = results.order_by(desc(Contract.date) if order == "descending"
                                           else asc(Contract.date))

            case "amount":
                results = results.order_by(desc(Contract.amount) if order == "descending"
                                           else asc(Contract.amount))

        total_results = results.count()
        paginated_results = results.offset((page - 1) * per_page).limit(per_page).all()
        return {"results_per_page": paginated_results,
                "total_contracts": total_results + 1 if total_results == 0 else total_results
                }

    # def search_voen(self) -> list:
    #     searched_voen = (self.db_session.query(Companies).join(Contract, Companies.id == Contract.company_id)
    #                      .filter(Companies.voen == self.search))
    #     return searched_voen

    # def filter_results(self, results: list) -> list:
    #     filtered_results = []
    #     for result in results:
    #         # print(result.company_name, result.voen)
    #         if (result.voen.find(self.search) != -1) or (result.company_name.find(self.search) != -1):
    #             filtered_results.append(result)
    #         else:
    #             for contract in result.contracts:
    #                 filtered_results.append(contract) if contract.contract_number.find(self.search) != -1 else None
    #     # print(filtered_results)
    #     return filtered_results

    # @staticmethod
    # def flat_results(results: list) -> list:
    #     flat_results = []
    #     for result in results:
    #         if isinstance(result, Companies):
    #             for contract in result.contracts:
    #                 flat_results.append(contract)
    #         else:
    #             flat_results.append(result)
    #     return flat_results

    def search_company_with_contract(self) -> Contract | None:
        result = self.db_session.query(Contract).join(Companies).filter(Contract.id == self.search).first()
        return result

    def search_company(self) -> Companies | None:
        result = self.db_session.query(Companies).filter_by(id=self.search).first()
        return result

    def get_all_results(self, db, page: int, per_page: int) -> dict[str, int | Any]:
        stmt = self.db_session.query(Contract).join(Contract.company).distinct()
        total_contracts = stmt.count()
        limited_results = db.paginate(stmt, page=page, per_page=per_page, error_out=False).items
        return {"results_per_page": limited_results,
                "total_contracts": total_contracts
                }


class EditContract(ValidatorWrapper):
    def __init__(self, db_session: Session, contract_id: int):
        super().__init__(db_session)
        self.id = contract_id

    # Helpers methods for update logic
    def is_company_exists(self, company_name: str) -> int | None:
        """
            Checks if the company exists in the database. If it exists then update the contract foreign key to the other
            company and voen else flash error
        """
        result = self.db_session.query(Companies).filter(Companies.company_name == company_name).first()
        return result.id if result else None

    def is_voen_exists(self, voen_result: str) -> int | None:
        """
               Checks if the voen exists in the database. If it exists then update the contract foreign key to the other
               company and voen else flash error
               """
        result = self.db_session.query(Companies).filter_by(voen=voen_result).first()
        return result.id if result else None

    def voen_and_company_matched(self, company_name: str, voen_result: str) -> int | None:
        """
            Check if there is an existing company with the given name and VOEN.
            Returns the company's ID if found, None otherwise.
        """
        result = self.db_session.query(Companies).filter_by(company_name=company_name, voen=voen_result).first()
        return result.id if result else None

    def change_pdf_file_path(self, company_id: int, old_file_path: str, contract_id: int) -> str:
        new_company_name = self.db_session.query(Companies).where(Companies.id == company_id).first().company_name
        new_company_voen = self.db_session.query(Companies).where(Companies.id == company_id).first().voen
        print(f"New company voen: {new_company_voen}")
        print(os.path.basename(old_file_path))
        company_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_company_name)
        company_upload_path = os.path.normpath(company_upload_path)
        print(company_upload_path)
        old_file_path = os.path.normpath(old_file_path)
        new_file_path = os.path.join(str(company_upload_path), os.path.basename(re.sub(r"_\d{10}_",
                                                                                       f"_{new_company_voen}_",
                                                                                       old_file_path)))
        print(f"Old File Path: {old_file_path}")
        print(f"New File Path: {new_file_path}")

        os.rename(old_file_path, new_file_path)
        new_file_path = os.path.normpath(new_file_path)
        return new_file_path

    @staticmethod
    def change_pdf_itself(previous_pdf_file_path: str, new_pdf_file_name: str) -> str:
        print(f"{new_pdf_file_name}: {previous_pdf_file_path}")
        new_pdf_path = os.path.join(os.path.dirname(previous_pdf_file_path), new_pdf_file_name)
        new_pdf_path = os.path.normpath(new_pdf_path)
        print(f"New File Path: {new_pdf_path}")
        os.remove(previous_pdf_file_path)
        return new_pdf_path

    # Helpers methods for update logic

    #  Main update logic is here
    def update_data(self, changes: dict, pdf_file: flask) -> tuple[bool, str]:
        """
            The main update logic after contract's edit. it will check all the possibilities of updating or refuse the
            contract to update based on different situations
        """
        contract_to_update = self.db_session.query(Contract).join(Contract.company).filter(
            Contract.id == int(self.id)).first()
        if not contract_to_update:
            return False, f"Contract was not found in database"
        try:
            company_name = changes.get("company_name")
            voen = changes.get("voen")
            update_status = {'company_and_voen_updated': False}
            if voen != contract_to_update.company.voen and company_name != contract_to_update.company.company_name:
                existed_company_id = self.voen_and_company_matched(company_name, voen)
                if existed_company_id:
                    contract_to_update.company_id = existed_company_id
                    update_status["company_and_voen_updated"] = True
                else:
                    return False, ("The provided company name and VOEN do not match any existing company. "
                                   "Please check your information or create a new company record.")

            for key, value in changes.items():
                if hasattr(contract_to_update, key):
                    current_value = getattr(contract_to_update, key)
                    if key == "pdf_file_path" and current_value != value:
                        try:
                            new_pdf_path = self.change_pdf_itself(current_value, value)
                            setattr(contract_to_update, key, new_pdf_path)
                            pdf_file.save(new_pdf_path)
                        except FileNotFoundError:
                            return False, "There is the file path problem. It was corrupted or not existed."

                    elif current_value != value:
                        setattr(contract_to_update, key, value)
                elif hasattr(contract_to_update.company, key) and not update_status["company_and_voen_updated"]:
                    current_value = getattr(contract_to_update.company, key)
                    if current_value != value:
                        match key:
                            case "company_name":
                                existed_company_id = self.is_company_exists(value)
                                if existed_company_id:
                                    try:
                                        new_pdf_file_path = self.change_pdf_file_path(existed_company_id,
                                                                                      contract_to_update.pdf_file_path,
                                                                                      contract_to_update.id)
                                        contract_to_update.company_id = existed_company_id
                                        contract_to_update.pdf_file_path = new_pdf_file_path
                                    except FileNotFoundError:
                                        return False, ("There is the file path problem. It was corrupted or not existed."
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
                                                                                      contract_to_update.id)
                                        contract_to_update.company_id = existed_voen_id
                                        contract_to_update.pdf_file_path = new_pdf_file_path
                                    except FileNotFoundError:
                                        return False, ("There is the file path problem. It was corrupted or not existed."
                                                       "Please, load a new pdf first")
                                else:
                                    return False, (f"There is no such voen related to any company in the database: "
                                                   f"{value}.Please go to the"
                                                   f"create contract form page")
            self.db_session.commit()
            return True, f"Contract updated successfully"
        except sqlalchemy.exc.DBAPIError as e:
            print("An error occurred:", e)
            self.db_session.rollback()
            return False, f"An error occurred in the server. Please try again later"


class CompanyManager(ContractManager):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def check_swift(self, swift_code: str) -> bool | ValueError:
        if not swift_code:
            return False
        swift_code_query = self.db_session.query(Companies).filter_by(swift=swift_code).first()
        if swift_code_query:
            raise ValueError(
                f"Invalid swift code: {swift_code}. It is already linked to a {swift_code_query.company_name} company") \
                if swift_code_query is not None else False
        return False

    def get_or_create_company(self, company_name: str, voen: str, company_data=None, *args, **kwargs) -> None:
        try:
            company = self.db_session.query(Companies).filter_by(company_name=company_name).one()
            if company.voen != voen:
                raise ValueError(f"The {company_name} company already has a voen {company.voen}")

            for key, value in company_data.items():
                if value is not None:
                    print(f"{key}: {value}")
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


class CompanySearchEngine(SearchEngine):
    def __init__(self, db_session: Session, search: str = None):
        super().__init__(db_session, search)

    def get_all_results(self, page: int, per_page: int, db=None, *args, **kwargs) -> dict[str, int | Any]:
        # list_of_colmns = self.db_session.query(Companies)
        stmt = self.db_session.query(
            Companies.id,
            Companies.company_name,
            Companies.voen,
            func.count(Contract.id).label('contract_count')).outerjoin(Contract, Companies.contracts).group_by(
            Companies.id)
        total_companies = self.db_session.query(func.count(Companies.id)).scalar()
        offset = (page - 1) * per_page
        limited_results = stmt.offset(offset).limit(per_page).all()
        results = [{
            "id": id,
            "company_name": company_name,
            "voen": voen,
            "contract_count": contract_count
        } for id, company_name, voen, contract_count in limited_results]
        return {"results_per_page": results,
                "total_companies": total_companies,
                }

    def search_query(self, page: int, per_page: int, filters: str, order: str) -> dict:
        results = (self.db_session.query(
            Companies.id,
            Companies.company_name,
            Companies.voen,
            func.count(Contract.id).label("contract_count")
        )
                   .filter(or_(
            Companies.company_name.ilike(f"%{self.search}%"),
            Companies.voen.ilike(f"%{self.search}%")
        ))
                   .outerjoin(Contract, Companies.contracts)
                   .group_by(Companies.id))
        print(results)
        # Filters
        match filters:
            case "company":
                results = results.order_by(desc(Companies.company_name) if order == "descending"
                                           else asc(Companies.company_name))

            case "contracts":
                results = results.order_by(desc("contract_count") if order == "descending"
                                           else asc("contract_count"))

        total_results = results.count()
        paginated_results = results.offset((page - 1) * per_page).limit(per_page).all()
        return {"results_per_page": paginated_results,
                "total_companies": total_results + 1 if total_results == 0 else total_results,
                }

    def search_company(self) -> Type[Companies] | None:
        result = self.db_session.query(Companies).filter_by(id=self.search).first()
        return result


class EditCompany(EditContract):
    def __init__(self, db_session: Session, company_id: int):
        super().__init__(db_session, company_id)
        self.company_id = company_id

    def update_company_voen_or_swift(self, key: str, value: str | int) -> InstrumentedAttribute | None:
        result = self.db_session.query(Companies).filter_by(**{key: value}).first()
        if result:
            return result.company_name
        return None

    def update_data(self, changes: dict, pdf_file: flask = None, *args, **kwargs) -> tuple[bool, str]:
        """
                    The main update logic after company's edit. it will check all the possibilities of updating or refuse the
                    company to update based on different situations
                """
        company_to_update = self.db_session.query(Companies).filter_by(id=self.id).first()
        if not company_to_update:
            return False, f"Contract was not found in database"
        company_to_update_dict = {column.name: getattr(company_to_update, column.name) for column in company_to_update.__table__.columns}
        for key, value in changes.items():
            try:
                if value != company_to_update_dict[key]:
                    if key in ["voen", "swift", "company_name"]:
                        print(key)
                        check_voen_or_swift = self.update_company_voen_or_swift(key, value)
                        if check_voen_or_swift:
                            return False, f"This {key} is already linked to {check_voen_or_swift}."
                        setattr(company_to_update, key, value)
                    setattr(company_to_update, key, value)
                else:
                    continue
                self.db_session.commit()
            except sqlalchemy.exc.DBAPIError as e:
                self.db_session.rollback()
                return False, "An error occurred with the database. Please try again later"
        return True, "The contract was updated successfully"

