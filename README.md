# 📄 PDF-to-SQL Pipeline

**AI-powered document extraction API that converts unstructured PDFs into structured JSON data.**

Built with **Docling OCR (free, local)** + **Google Gemini Flash-Lite** — extracts bank statements, invoices, and clinical-style notes at **< $0.001 per document**.

> **Privacy note:** This repository does not include any real customer documents, bank statements, invoices, or clinical records. All examples shown are anonymized or synthetic.

---

## 🚀 How It Works

```text
Upload PDF → Docling OCR (Local) → Gemini (Schema Mapping) → Validation → Structured JSON
Pipeline stages
Docling OCR (Local-first)
Extracts text, tables, and layout from PDFs (runs locally on CPU)

Gemini Flash-Lite (Schema mapping)
Maps extracted text into structured JSON using few-shot prompting (~$0.10 / 1M tokens)

Deterministic Validation Engine (Trust layer)
Business rules validate balances, totals, date formats, and field consistency

✨ Key Features
Local-first OCR — Docling runs on CPU. No GPU required. No cloud OCR.

LLM schema mapping — Gemini Flash-Lite converts raw text into typed JSON.

Deterministic validation — balance checks, totals reconciliation, date validation.

Multi-schema support — bank statements, invoices, and clinical-style notes.

FastAPI + Swagger UI — interactive API docs available at /docs.

Cost optimized — < $0.001 per document. Designed for regulated environments.

📊 Benchmarks
Benchmarks were run on real-world document formats across multiple domains.
Sources are intentionally anonymized to avoid exposing private financial information.

Document Type	Source (Anonymized)	Pages	Confidence	Fields Extracted	Cost	Time
Bank Statement	Ghanaian retail bank	3	97%	Account + 9 transactions	$0.0009	12.5s
Account Statement	Ghanaian retail bank	2	98%	Holder + period + balances	$0.0002	12.2s
Billing Statement	US loan servicer	4	99%	Vendor + client + line items	$0.0009	14.1s
Cost comparison
Approach	Cost per Document	Annual (10K docs)
Google Document AI	$0.06 / page	$2,400+
AWS Textract	$0.015 / page	$600+
This Pipeline	$0.0008	$8
⚡ Quick Start
Prerequisites
Python 3.11+

Free Gemini API key from: https://aistudio.google.com/apikey

Setup
# Clone
git clone https://github.com/CrillyPienaah/pdf-to-sql-pipeline.git
cd pdf-to-sql-pipeline

# Create environment
python -m venv venv
source venv/bin/activate          # Mac/Linux
# .\venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GEMINI_API_KEY=your_key_here" > .env
🧠 Extract a Document
CLI
python run_extract.py document.pdf bank_statement
python run_extract.py invoice.pdf invoice
python run_extract.py clinical_note.pdf clinical_note
API Server
uvicorn app.main:app --reload --port 8080
# Open http://localhost:8080/docs
cURL
curl -X POST http://localhost:8080/api/v1/extract \
  -F "file=@statement.pdf" \
  -F "doc_type=bank_statement"
📌 Supported Document Types
🏦 Bank Statement (bank_statement)
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
{
  "patient_id": "PT-00000",
  "encounter_date": "2026-01-15",
  "provider_name": "Dr. Jane Doe, MD",
  "chief_complaint": "Persistent cough for 3 weeks",
  "diagnoses": [
    "Acute bronchitis (J20.9)",
    "Mild asthma exacerbation (J45.20)"
  ],
  "medications": [
    "Albuterol inhaler PRN",
    "Montelukast 10mg daily"
  ],
  "plan": "Start azithromycin, follow up in 2 weeks"
}
🔌 API Endpoints
Method	Endpoint	Description
GET	/health	Health check
GET	/api/v1/schemas	List extraction schemas
POST	/api/v1/extract	Upload PDF and extract structured data
🧱 Project Structure
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
└── .env   # API key (not committed)
🧠 Design Decisions
Decision	Choice	Rationale
Primary OCR	Docling (local) over cloud OCR	Compliance-friendly + low cost
LLM for mapping	Gemini Flash-Lite	Cheapest model that performs well for schema mapping
Validation	Pydantic + business rules	Deterministic checks wrap probabilistic outputs
API framework	FastAPI	OpenAPI docs, async support, type hints
Architecture	Modular pipeline	Each stage is independently swappable and testable
🗺️ Roadmap
 Docling OCR extraction (CPU)

 Gemini Flash-Lite schema mapping

 Business rules validation engine

 FastAPI + Swagger UI

 Bank statement / invoice / clinical-style note support

 Fully local mapping mode (open-weight models / Ollama)

 Document AI fallback for scanned/handwritten documents

 Cloud Run deployment (public API)

 BigQuery integration for persistent storage

 IDP Quality Assurance verification layer (multi-agent)

 React dashboard for extraction results

🧰 Tech Stack
Component	Technology
OCR Engine	Docling (IBM, MIT License)
LLM Mapping	Gemini 2.5 Flash-Lite
API	FastAPI
Validation	Pydantic v2
👤 Author
Christopher Crilly Pienaah
MSc Analytics (Applied Machine Intelligence), Northeastern University
AI/ML Product Strategist

📄 License
MIT License


---

## Why this one looks professional
- clean headings  
- proper code blocks  
- proper tables  
- no messy ASCII diagram  
- privacy disclaimer included  
- examples are safe  

---

If you want, I can also write a **top-tier GitHub “About” description + repo topics** so your project ranks better in search.
