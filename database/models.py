from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, CHAR, DATE, ForeignKey, DECIMAL, VARCHAR, BOOLEAN, DateTime
from database.db_init import Base
from sqlalchemy.orm import relationship
from flask_login import UserMixin


class User(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(20), nullable=False, unique=True)
    password = Column(VARCHAR(), nullable=False)
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
    pdf_file_path = Column(VARCHAR, nullable=False)
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


class ContractUpdateToken(Base):
    __tablename__ = 'contract_update_token'
    id = Column(Integer, primary_key=True)
    token = Column(CHAR(36), unique=True, nullable=False)
    contract_id = Column(Integer, nullable=True)
    company_id = Column(Integer, nullable=True)
    addition_id = Column(Integer, nullable=True)
    act_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=False)
    edited_user_id = Column(Integer, nullable=True)
    category_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now())

    def is_expired(self):
        return datetime.now() > self.created_at + timedelta(minutes=2)

