import shutil
from typing import Any, Type
import os
from flask import current_app
from werkzeug.utils import secure_filename
from flask_sqlalchemy.session import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from database.models import *
from abc import ABC


class ValidatorWrapper(ABC):
    def __init__(self, db_session: Session):
        self.db_session = db_session


class ContractManager(ValidatorWrapper):
    def __init__(self, db_session: Session):
        super().__init__(db_session)

    def get_or_create_company(self, company_name: str, voen: str) -> None | Type[Companies] | Companies:
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
            self.db_session.flush()
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
    def __init__(self, db_session: Session, search: str = None):
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
            Companies.voen.ilike(f"%{self.search}"),
            Contract.contract_number.ilike(f"%{self.search}")
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
                "total_contracts": total_results
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

    def search_company(self) -> Contract:
        result = self.db_session.query(Contract).join(Companies).filter(Contract.id == int(self.search)).first()
        return result

    def get_all_results(self, db, page: int, per_page: int) -> dict[str, int | Any]:
        stmt = self.db_session.query(Contract).join(Contract.company).distinct()
        total_contracts = stmt.count()
        limited_results = db.paginate(stmt, page=page, per_page=per_page, error_out=False).items
        return {"results_per_page": limited_results,
                "total_contracts": total_contracts
                }


class Edit(ValidatorWrapper):
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

    def change_pdf_file_path(self, company_id: int, old_file_path: str, contract_id: int) -> None:
        new_company_name = self.db_session.query(Companies).where(Companies.id == company_id).first().company_name
        print(new_company_name)
        company_upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_company_name)
        company_upload_path = os.path.normpath(company_upload_path)
        print(company_upload_path)
        old_file_path = os.path.normpath(old_file_path)
        new_file_path = os.path.join(str(company_upload_path), os.path.basename(old_file_path))
        print(f"Old File Path: {old_file_path}")
        print(f"New File Path: {new_file_path}")

        os.rename(old_file_path, new_file_path)
        save_in_db = self.db_session.query(Contract).where(Contract.id == contract_id).first()
        new_file_path = new_file_path.replace("\\", "/")
        save_in_db.pdf_file_path = new_file_path

    # Helpers methods for update logic

    #  Main update logic is here
    def update_data(self, changes: dict) -> tuple[bool, str]:
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
                    if current_value != value and value is not None:
                        setattr(contract_to_update, key, value)
                        print(f"Updated {key} from {current_value} to {value}")
                elif hasattr(contract_to_update.company, key) and not update_status["company_and_voen_updated"]:
                    current_value = getattr(contract_to_update.company, key)
                    if current_value != value:
                        match key:
                            case "company_name":
                                existed_company_id = self.is_company_exists(value)
                                if existed_company_id:
                                    # If company exists, change the company association
                                    self.change_pdf_file_path(existed_company_id,
                                                              contract_to_update.pdf_file_path,
                                                              contract_to_update.id)
                                    contract_to_update.company_id = existed_company_id
                                else:
                                    return False, (f"There is no such company in the database: {value}.Please go to the"
                                                   f" create contract form page")
                            case "voen":
                                existed_voen_id = self.is_voen_exists(value)
                                if existed_voen_id:
                                    self.change_pdf_file_path(existed_voen_id,
                                                              contract_to_update.pdf_file_path,
                                                              contract_to_update.id)
                                    contract_to_update.company_id = existed_voen_id
                                else:
                                    return False, (f"There is no such voen related to any company in the database: "
                                                   f"{value}.Please go to the"
                                                   f"create contract form page")
            self.db_session.commit()
            return True, f"Contract updated successfully"
        except SQLAlchemyError as e:
            print("An error occurred:", e)
            self.db_session.rollback()
            return False, f"An error occurred in the server"
