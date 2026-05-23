from dotenv import load_dotenv
load_dotenv() #Read the .env file
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware 
from groq import Groq
import json
import requests
import os
from sqlalchemy.orm import Session
from fastapi import Depends
import models
import schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY") #Access the groq apikey
)

app = FastAPI()

app.add_middleware( #Allow frontend to communicate w backend
    CORSMiddleware, 
    allow_origins=["*"], #Allow access from any website
    allow_methods=["*"], #Allow all types of request (POST, ,GET, PUT, DELETE)
    allow_headers=["*"] #Allow frontend to send any extra (API keys, content)
)

def read_content(fileContent, title): #fileContent reads the content, title read title
    response = requests.post( #POST
        "https://api.ocr.space/parse/image",
        files = {"file": (title, fileContent)}, #upload pdf/image #read title then the content
        data = { "apikey": os.getenv("OCR_API_KEY"),
                "language" : "eng"
                }
    )
    result = response.json() #OCR to python
    
    if result["IsErroredOnProcessing"]:
        raise HTTPException(status_code=400, detail="pdf/png is not clear")

    parsedResult = result.get("ParsedResults")
    if not parsedResult:
        raise HTTPException(status_code=400, detail="pdf/png is not clear")
    
    return parsedResult[0]["ParsedText"] 

@app.post("/analyze-loan")
def get_loan(file: UploadFile = File(None), text: str = Form(None), db: Session = Depends(get_db)): #None= User can leave empty
    if not file and not text: 
        raise HTTPException(status_code=400, detail="File not supported")
    if text:
        read_text = text
    elif file:
        read_file = file.file.read()

        read_text = read_content(read_file, file.filename)
    
    prompt = f"""
    Required fields:
    - interest_year
    - monthly_payment
    - total_repayment
    - penalties
    - hidden_fees
    - warning_alert
    - flag_suspicious
    - safer_alternative
    - bm_summary
    - en_summary

    Rules:
    - Acts as early warning system that detects when someone is heading into a debt trap
    - Identify and flag suspicious terms.
    - Generate the summaries yourself using simple plain language.

    Loan text:
    {read_text}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content" : "You are a loan analysis assistant. Analyze this loan agreement, return only valid raw JSON"},
            {"role": "user","content": prompt}
        ]
    )
    
    result = response.choices[0].message.content

    result1 = result.replace("```json","")
    result2 = result1.replace("```","")
    try:
        result3 = json.loads(result2)
    except ValueError:
        raise HTTPException(status_code=500, detail="File is failed to read")
    
    try:
        interestStr = str(result3.get("interest_year", 0))
        interest = float(interestStr)
    except (ValueError, KeyError):
        raise HTTPException(status_code=500, detail="interest_year is invalid")

    risk_score = 0
    if interest <= 9:
        risk_score += 0
    elif interest <= 17:
        risk_score += 25
    else:
        risk_score = 40

    flag_suspicious = result3.get("flag_suspicious")
    if result3.get("penalties"): 
        risk_score += 15
    if  result3.get("hidden_fees"): 
        risk_score += 15
    if result3.get("warning_alert"): 
        risk_score += 10
    if flag_suspicious == True: 
        risk_score += 20

    if risk_score >= 50:
        risk_level = "DANGEROUS"
    elif risk_score >= 25:
        risk_level = "CAUTION"
    else:
        risk_level = "SAFE"

    # Save to database
    db_document = models.LoanDocument(
        filename=file.filename if file else "pasted_text.txt",
        raw_text=read_text
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    db_analysis = models.LoanAnalysis(
        document_id=db_document.id,
        monthly_payment=result3.get("monthly_payment"),
        total_repayment=result3.get("total_repayment"),
        penalties=str(result3.get("penalties", "")),
        hidden_fees=str(result3.get("hidden_fees", "")),
        risk_level=risk_level,
        interest_year=interest,
        risk_score=risk_score,
        flag_suspicious=bool(flag_suspicious),
        bm_summary=result3.get("bm_summary", ""),
        en_summary=result3.get("en_summary", "")
    )
    db.add(db_analysis)
    db.commit()
    
    return {
        "risk_level": risk_level,
        "result": result3,
        "text":read_text
    }