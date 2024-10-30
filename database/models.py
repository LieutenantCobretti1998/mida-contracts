
from sqlalchemy import Column, Integer, CHAR, DATE, ForeignKey, DECIMAL, VARCHAR, BOOLEAN, TEXT
from database.db_init import Base, db
from sqlalchemy.orm import relationship
from flask_login import UserMixin


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(40), nullable=False, unique=True)
    password = Column(CHAR(12), nullable=False, unique=False)
    role = Column(VARCHAR(20), nullable=False, default='user')


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
    end_date = Column(DATE, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship('Category', back_populates='contracts')
    amount = Column(DECIMAL(), nullable=False)
    remained_amount = Column(DECIMAL(), nullable=False)
    company = relationship("Companies", back_populates="contracts")
    adv_payer = Column("adv_payer", BOOLEAN, nullable=False, default=False)
    is_expired = Column("is_expired", BOOLEAN, nullable=False, default=False)
    pdf_file_path = Column(VARCHAR, nullable=False)
    comments = Column(TEXT, nullable=True)
    acts = relationship('Acts', back_populates='contract', cascade='all, delete, delete-orphan')
    additions = relationship('Additions', back_populates='contract', cascade='all, delete, delete-orphan')


class Acts(Base):
    __tablename__ = 'acts'
    id = Column(Integer, primary_key=True)
    act_number = Column(VARCHAR(16), nullable=False)
    date = Column(DATE, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    contract = relationship("Contract", back_populates="acts")
    pdf_file_path = Column(VARCHAR, nullable=False)


class Additions(Base):
    __tablename__ = 'additions'
    id = Column(Integer, primary_key=True)
    addition_number = Column(VARCHAR(16), nullable=False)
    date = Column(DATE, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    amount = Column(DECIMAL(), nullable=False)
    contract = relationship("Contract", back_populates="additions")
    pdf_file_path = Column(VARCHAR, nullable=False)


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    category_name = Column(VARCHAR(), nullable=False)
    contracts = relationship('Contract', back_populates='category')
