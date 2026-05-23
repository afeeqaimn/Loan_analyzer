import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class LoanDocument(Base):
    __tablename__ = "loan_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    analysis = relationship("LoanAnalysis", back_populates="document", uselist=False, cascade="all, delete-orphan")


class LoanAnalysis(Base):
    __tablename__ = "loan_analyses"

    id = Column(Integer, primary_key=True, index=True)
    
    document_id = Column(Integer, ForeignKey("loan_documents.id"), unique=True, nullable=False)
    
    monthly_payment = Column(Float, nullable=True)
    total_repayment = Column(Float, nullable=True)
    penalties = Column(Text, nullable=True)
    hidden_fees = Column(Text, nullable=True)
    risk_explanation = Column(Text, nullable=True)
    risk_level = Column(String, nullable=True)
    interest_year = Column(Float, nullable=True)
    risk_score = Column(Integer, nullable=True)
    flag_suspicious = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    bm_summary = Column(Text, nullable=True)
    en_summary = Column(Text, nullable=True)
    
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)

    document = relationship("LoanDocument", back_populates="analysis")
