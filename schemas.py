from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LoanAnalysisBase(BaseModel):
   monthly_payment: Optional[float] = None
   total_repayment: Optional[float] = None
   penalties: Optional[str] = None
   hidden_fees: Optional[str] = None
   risk_explanation: Optional[str] =None
   risk_level: Optional[str] = None
   interest_year: Optional[float] = None
   risk_score: Optional[int] = None
   bm_summary: Optional[str] = None
   en_summary: Optional[str] = None
   flag_suspicious: Optional[bool] = False

class LoanAnalysisCreate(BaseModel):
    document_id: int

class LoanAnalysis(LoanAnalysisBase):
    id: int
    document_id: int
    created_at: datetime
    analyzed_at: datetime

    class Config:
        from_attributes = True

class LoanDocumentBase(BaseModel):
    filename: str
    file_path: Optional[str] = None
    raw_text:  Optional[str] = None
    
class LoanDocument(LoanDocumentBase):
    id: int
    uploaded_at: datetime
    analysis: Optional[LoanAnalysis] = None 
    class Config:
        from_attributes = True
