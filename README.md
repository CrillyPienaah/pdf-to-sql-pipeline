📄 PDF-to-SQL Pipeline

AI-powered document extraction API that converts unstructured PDFs into structured JSON data.

Built with Docling OCR (free, local) + Google Gemini Flash-Lite — extracts bank statements, invoices, and clinical-style notes at < $0.001 per document.

Privacy note: This repository does not include any real customer documents, bank statements, invoices, or clinical records. All examples shown are anonymized or synthetic.








How It Works
┌──────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Upload  │────▶│  Docling OCR    │────▶│  Gemini AI      │────▶│  Structured  │
│  PDF     │     │  (Free, Local)  │     │  Schema Mapping │     │  JSON Output │
└──────────┘     │                 │     │                 │     └──────────────┘
                 │  • Text extract │     │  • Few-shot     │              │
                 │  • Table detect │     │  • Field mapping│              ▼
                 │  • Layout parse │     │  • Type coerce  │     ┌──────────────┐
                 │  • 97–99% conf. │     │  • ~$0.0002/doc │     │  Validation  │
                 └─────────────────┘     └─────────────────┘     │  Engine      │
                                                                  │              │
                                                                  │  • Balance   │
                                                                  │    checks    │
                                                                  │  • Date fmt  │
                                                                  │  • Totals    │
                                                                  └──────────────┘

Key Features

Hybrid OCR Architecture — Docling (free, CPU-based) as primary extractor. No GPU required.

Gemini Flash-Lite Mapping — Converts raw text + tables into structured JSON via few-shot prompting. Costs ~$0.0002 per document.

Business Rules Validation — Balance consistency checks, date format validation, invoice total matching.

Three Document Types — Bank statements, invoices, and clinical-style notes with domain-specific extraction schemas.

FastAPI with Swagger UI — REST API with interactive documentation at /docs.

Cost Optimized — Entire pipeline runs for < $0.001 per document. ~300x cheaper than enterprise alternatives.

Benchmarks

Benchmarks were run on real-world document formats across multiple domains.
Sources are intentionally anonymized to avoid exposing private financial information.

Document	Source (Anonymized)	Pages	Confidence	Fields Extracted	Cost	Time
Bank Statement	Ghanaian retail bank	3	97%	Account, 9 transactions	$0.0009	12.5s
Account Statement	Ghanaian retail bank	2	98%	Holder, period, balances	$0.0002	12.2s
Billing Statement	US loan servicer	4	99%	Vendor, client, line items	$0.0009	14.1s

Cost comparison:

Approach	Cost per Document	Annual (10K docs)
Google Document AI	$0.06/page	$2,400+
AWS Textract	$0.015/page	$600+
This Pipeline	$0.0008	$8
Quick Start
Prerequisites

Python 3.11+

Free Gemini API key from aistudio.google.com/apikey

Setup (5 minutes)
# Clone
git clone https://github.com/CrillyPienaah/pdf-to-sql-pipeline.git
cd pdf-to-sql-pipeline

# Environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# .\venv\Scripts\activate       # Windows

# Install
pip install -r requirements.txt

# Configure (paste your free Gemini API key)
echo "GEMINI_API_KEY=your_key_here" > .env

Extract a Document

CLI:

python run_extract.py document.pdf bank_statement
python run_extract.py invoice.pdf invoice
python run_extract.py clinical_note.pdf clinical_note


API Server:

uvicorn app.main:app --reload --port 8080
# Open http://localhost:8080/docs for Swagger UI


cURL:

curl -X POST http://localhost:8080/api/v1/extract \
  -F "file=@statement.pdf" \
  -F "doc_type=bank_statement"

Supported Document Types
🏦 Bank Statement (bank_statement)

Extracts account details and transaction history.

{
  "account_number": "XXXX-XXXX",
  "account_holder": "SAMPLE ACCOUNT HOLDER",
  "bank_name": "SAMPLE BANK",
  "statement_period_start": "2025-01-01",
  "statement_period_end": "2025-01-31",
  "opening_balance": 915.36,
  "closing_balance": 511.36,
  "currency": "GHS",
  "transactions": [
    {
      "date": "2025-01-13",
      "description": "ATM WITHDRAWAL",
      "amount": -50.0,
      "balance": 865.36,
      "transaction_type": "DEBIT"
    }
  ]
}

🧾 Invoice (invoice)

Extracts vendor info, line items, and totals.

{
  "vendor_name": "SAMPLE SERVICER LLC",
  "client_name": "SAMPLE CUSTOMER",
  "invoice_date": "2026-01-07",
  "due_date": "2026-01-27",
  "subtotal": 378.49,
  "total_amount": 378.49,
  "currency": "USD",
  "line_items": [
    {
      "description": "Applied to Principal",
      "quantity": 1.0,
      "unit_price": 4.85,
      "total": 4.85
    },
    {
      "description": "Applied to Interest",
      "quantity": 1.0,
      "unit_price": 373.64,
      "total": 373.64
    }
  ]
}

🏥 Clinical Note (clinical_note)

Extracts patient info, diagnoses, medications, and care plan.

{
  "patient_id": "PT-00000",
  "encounter_date": "2026-01-15",
  "provider_name": "Dr. Jane Doe, MD",
  "chief_complaint": "Persistent cough for 3 weeks",
  "diagnoses": ["Acute bronchitis (J20.9)", "Mild asthma exacerbation (J45.20)"],
  "medications": ["Albuterol inhaler PRN", "Montelukast 10mg daily"],
  "plan": "Start azithromycin, follow up in 2 weeks"
}

API Endpoints
Method	Endpoint	Description
GET	/health	Health check and configuration status
GET	/api/v1/schemas	List available extraction schemas
POST	/api/v1/extract	Upload PDF and extract structured data
Project Structure
pdf-to-sql-pipeline/
├── app/
│   ├── main.py
│   ├── pipeline.py
│   ├── config.py
│   ├── extractors/
│   │   └── docling_extractor.py
│   ├── mappers/
│   │   └── gemini_mapper.py
│   ├── validators/
│   │   └── schema_validator.py
│   └── models/
│       └── document.py
├── run_extract.py
├── outputs/
├── requirements.txt
└── .env  # API key (not committed)

Design Decisions
Decision	Choice	Rationale
Primary OCR	Docling (free) over Document AI ($0.06/pg)	85–90% cost savings, 97%+ accuracy on digital PDFs
LLM for mapping	Gemini Flash-Lite ($0.10/1M tokens)	Cheapest model with sufficient accuracy for structured extraction
Schema validation	Pydantic + custom business rules	Type safety + domain-specific checks (balance matching, date formats)
API framework	FastAPI	Auto-generated OpenAPI docs, async support, type hints
Architecture	Modular pipeline	Each stage is independently testable and swappable
Roadmap

 Docling OCR extraction with confidence scoring

 Gemini Flash-Lite schema mapping with few-shot prompts

 Business rules validation engine

 FastAPI with Swagger UI

 Bank statement, invoice, clinical note support

 Fully local mapping mode (open-weight models / Ollama)

 Document AI fallback for scanned/handwritten documents

 Cloud Run deployment (public API)

 BigQuery integration for persistent storage

 IDP Quality Assurance verification layer (multi-agent)

 React dashboard for extraction results

Tech Stack
Component	Technology	Cost
OCR Engine	Docling
	Free
LLM Mapping	Gemini 2.5 Flash-Lite
	Free tier
API Framework	FastAPI
	Free
Validation	Pydantic v2
	Free
Total		$0 for development
Author

Christopher Crilly Pienaah
MSc Analytics (Applied Machine Intelligence), Northeastern University
AI/ML Product Strategist | LinkedIn

License

MIT License
