# Project Name: Loan_analyzer

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-orange)

Upload a loan agreement (PDF/image) or paste loan text, and get an instant AI-powered risk analysis — flagging hidden fees, suspicious terms, and debt traps in both English and Bahasa Melayu.


## Features
- Upload PDF/image or paste raw loan text
- OCR extraction via OCR.space API
- AI analysis using Groq LLaMA 3.3 70B
- Risk scoring engine: SAFE / CAUTION / DANGEROUS
- Detects hidden fees, penalties, suspicious terms
- Bilingual summary (EN + BM)
- All results saved to SQLite database

## Risk Scoring
| Level         | Score|
|---------------|------|
| ✅ SAFE      | < 25  |
| ⚠️ CAUTION   | 25–49 |
| 🚨 DANGEROUS | ≥ 50  |

## Tech Stack
| Layer     | Technology         |
|-----------|-----------         |
| Framework | FastAPI            |
| AI Model  | Groq LLaMA 3.3 70B |
| OCR        | OCR.space API     |
| Database  | SQLite + SQLAlchemy|
| Deploy    | Render (uvicorn)   |

## Setup

1. Clone and install:
```bash
git clone https://github.com/afeeqaimn/loan-analyzer.git
cd loan-analyzer
pip install -r requirements.txt
```

2. Create `.env`:
```bash
GROQ_API_KEY=your_groq_api_key
OCR_API_KEY=your_ocr_space_api_key
DATABASE_URL=sqlite:///./loans.db
```
 
3. Run:
```bash
uvicorn mainProject:app --reload
```

## API Usage

**POST** `/analyze-loan`
```bash
curl -X POST http://localhost:8000/analyze-loan \
  -F "file=@loan_agreement.pdf"
```

## Project Structure
```bash
mainProject.py   # FastAPI routes + analysis logic
models.py        # SQLAlchemy DB models
schemas.py       # Pydantic schemas
database.py      # DB engine + session
.env             # API keys (not committed)
loans.db         # SQLite database (auto-created)
```
## Deployment
uvicorn mainProject:app --host 0.0.0.0 --port $PORT


Built for hackathon. Protect people from predatory loans.
