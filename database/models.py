from sqlalchemy import Column, Integer, CHAR, DATE, ForeignKey, DECIMAL, VARCHAR, BOOLEAN
from database.db_init import Base
from sqlalchemy.orm import relationship


class Companies(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    company_name = Column(VARCHAR(16), nullable=False)
    voen = Column(CHAR(10), nullable=False, unique=True)
    bank_name = Column(VARCHAR())
    m_h = Column(VARCHAR())
    h_h = Column(VARCHAR())
    swift = Column(VARCHAR(11), unique=True)
    email = Column(VARCHAR())
    telephone_number = Column(VARCHAR())
    address = Column(VARCHAR())
    website = Column(VARCHAR())
    contracts = relationship('Contract', back_populates='company', cascade='all, delete, delete-orphan')


class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True)
    contract_number = Column(VARCHAR(16), nullable=False)
    date = Column(DATE, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    company = relationship("Companies", back_populates="contracts")
    adv_payer = Column("adv_payer", BOOLEAN, nullable=False, default=False)
    pdf_file_path = Column(VARCHAR, nullable=False)
    acts = relationship('Acts', back_populates='contract', cascade='all, delete, delete-orphan')


class Acts(Base):
    __tablename__ = 'acts'
    id = Column(Integer, primary_key=True)
    act_number = Column(VARCHAR(16), nullable=False)
    date = Column(DATE, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    contract = relationship("Contract", back_populates="acts")
    pdf_file_path = Column(VARCHAR, nullable=False)