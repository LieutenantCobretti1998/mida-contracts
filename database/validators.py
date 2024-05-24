from typing import Any, Type
from flask_sqlalchemy.session import Session
from sqlalchemy import or_, desc, asc
from sqlalchemy.exc import NoResultFound, IntegrityError, ArgumentError
from database.models import *
from database.models import Companies


class ContractManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session

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

    def one_voen_one_company(self, voen: str) -> bool:
        if not voen:
            return False


class SearchEngine:
    def __init__(self, db_session: Session, search: str = None):
        self.search = search
        self.db_session = db_session

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

    def search_voen(self) -> list:
        searched_voen = (self.db_session.query(Companies).join(Contract, Companies.id == Contract.company_id)
                         .filter(Companies.voen == self.search))
        return searched_voen

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

    def update_data(self, changes: dict) -> None:
        result = self.db_session.query(Contract).join(Contract.company).filter(Contract.id == int(self.search)).first()
        print(changes)
        print(result)
        if result:
            for key, value in changes.items():
                if hasattr(result, key):
                    current_value = getattr(result, key)
                    if current_value != value and value is not None:
                        setattr(result, key, value)
                        print(f"Updated {key} from {current_value} to {value}")
                    self.db_session.flush()
                elif hasattr(result.company, key):
                    current_value = getattr(result.company, key)
                    print(f"Updated {key} from {current_value}")
                    if current_value != value and value is not None:
                        setattr(result.company, key, value)
                        print(f"Updated {key} from {current_value} to {value}")
                    self.db_session.flush()
            self.db_session.commit()

    def is_company_exists(self, company_name: str, voen: str) -> bool:
        result = self.db_session.query(Companies).filter(or_(Companies.company_name == company_name,
                                                             Companies.voen == voen)).first()
        if result is not None:
            return True
        return False

