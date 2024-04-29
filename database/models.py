from sqlalchemy import Column, Integer, CHAR, DATE, ForeignKey, DECIMAL, VARCHAR
from database.db_init import Base
from sqlalchemy.orm import relationship


class Companies(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    company_name = Column(VARCHAR(16), nullable=False)
    voens = relationship("VOEN", back_populates="company")


class VOEN(Base):
    __tablename__ = 'voens'
    id = Column(Integer, primary_key=True, unique=True)
    voen = Column(CHAR(12), nullable=False, unique=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    company = relationship("Companies", back_populates="voens")
    contracts = relationship("Contract", back_populates="voen")


class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)
    contract_number = Column(CHAR(16), nullable=False)
    date = Column(DATE, nullable=False)
    voen_id = Column(Integer, ForeignKey('voens.id'), nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    voen = relationship("VOEN", back_populates="contracts")