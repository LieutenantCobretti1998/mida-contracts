from typing import Any
from flask_sqlalchemy.session import Session
from sqlalchemy import or_
from sqlalchemy.exc import NoResultFound, IntegrityError, ArgumentError
from database.models import *
from database.models import Companies


class ContractManager:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_or_create_company(self, company_name: str, voen: str) -> Companies:
        if not company_name:
            return None

        try:
            company = self.db_session.query(Companies).filter_by(company_name=company_name).one()
            if company.voen != voen:
                raise ValueError(f"The {company_name} company already has a voen {company.voen}")
            return company
        except NoResultFound:
            if self.check_voen(voen):
                raise ValueError(f"VOEN is already linked to {self.db_session.query(Companies).filter_by(voen=voen).one().company_name} company")

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

    def search_query(self) -> list:
        results = self.db_session.query(Companies).join(Contract).filter(or_(
            Companies.company_name.ilike(f"%{self.search}%"),
            Companies.voen.ilike(f"%{self.search}%"),
            Contract.contract_number.ilike(f"%{self.search}%")
        )).all()
        filtered_results = self.filter_results(results)
        print(filtered_results)
        return filtered_results

    def search_voen(self) -> list:
        searched_voen = (self.db_session.query(Companies).join(Contract, Companies.id == Contract.company_id)
                         .filter(Companies.voen == self.search))
        return searched_voen

    def filter_results(self, results: list) -> list:
        filtered_results = []
        for result in results:
            # print(result.company_name, result.voen)
            if (result.voen.find(self.search) != -1) or (result.company_name.find(self.search) != -1):
                filtered_results.append(result)
            else:
                for contract in result.contracts:
                    filtered_results.append(contract) if contract.contract_number.find(self.search) != -1 else None
        # print(filtered_results)
        return filtered_results

    @staticmethod
    def flat_results(results: list) -> list:
        flat_results = []
        for result in results:
            if isinstance(result, Companies):
                for contract in result.contracts:
                    flat_results.append(contract)
            else:
                flat_results.append(result)
        return flat_results

    def search_company(self) -> Contract:
        result = self.db_session.query(Contract).join(Companies).filter(Contract.id == self.search).first()
        return result

    def get_all_results(self, db, page: int, per_page: int) -> dict[str, int | Any]:
        # stmt = self.db_session.query(Companies).join(Contract.company).distinct()
        stmt = self.db_session.query(Contract).join(Contract.company).distinct()
        # results = self.db_session.execute(stmt)
        # companies = results.scalars().all()
        # total_contracts = sum(len(company.contracts) for company in companies)
        # for company in companies:
        total_contracts = stmt.count()
        limited_results = db.paginate(stmt, page=page, per_page=per_page, error_out=False).items
        return {"results_per_page": limited_results,
                "total_contracts": total_contracts
                }
