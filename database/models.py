from sqlalchemy import Column, Integer, CHAR, DATE, ForeignKey, DECIMAL, VARCHAR
from database.db_init import Base
from sqlalchemy.orm import relationship


class Companies(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    company_name = Column(CHAR(16), nullable=False)
    voen = Column(CHAR(20), nullable=False, unique=True)
    contracts = relationship('Contract', back_populates='company', cascade='all, delete, delete-orphan')


class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)
    contract_number = Column(CHAR(16), nullable=False)
    date = Column(DATE, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    company = relationship("Companies", back_populates="contracts")