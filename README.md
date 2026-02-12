# PDF-to-SQL Pipeline

**AI-powered document extraction API that converts unstructured PDFs into structured JSON data.**

Built with Docling OCR (free, local) + Google Gemini Flash-Lite. Extracts bank statements, invoices, and clinical notes at **< $0.001 per document**.

## How It Works
```
Upload PDF --> Docling OCR --> Gemini AI --> Validation --> Structured JSON
               (Free, CPU)    (Schema Map)   (Biz Rules)
```

**Pipeline stages:**
1. **Docling OCR** - Extracts text, tables, and layout from PDFs (free, runs locally on CPU)
2. **Gemini Flash-Lite** - Maps raw text to structured JSON using few-shot prompting ($0.10/1M tokens)
3. **Validation Engine** - Business rules: balance checks, date formats, invoice total matching

## Benchmarks

Tested on real-world financial documents from multiple institutions:

| Document | Source | Pages | Confidence | Cost | Time |
|----------|--------|-------|------------|------|------|
| Bank Statement | ABSA Bank Ghana | 3 | 97% | $0.0009 | 12.5s |
| Account Statement | First National Bank Ghana | 2 | 98% | $0.0002 | 12.2s |
| Billing Statement | Launch Servicing (USA) | 4 | 99% | $0.0009 | 14.1s |

**Cost comparison:**

| Approach | Cost per Document | Annual (10K docs) |
|----------|------------------|-------------------|
| Google Document AI | $0.06/page | $2,400+ |
| AWS Textract | $0.015/page | $600+ |
| **This Pipeline** | **$0.0008** | **$8** |

## Quick Start

### Prerequisites
- Python 3.11+
- Free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Setup
```bash
git clone https://github.com/CrillyPienaah/pdf-to-sql-pipeline.git
cd pdf-to-sql-pipeline
python -m venv venv
source venv/bin/activate          # Mac/Linux
# .\venv\Scripts\activate         # Windows
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env
```

### Extract a Document

**CLI:**
```bash
python run_extract.py document.pdf bank_statement
python run_extract.py invoice.pdf invoice
python run_extract.py note.pdf clinical_note
```

**API Server:**
```bash
uvicorn app.main:app --reload --port 8080
# Open http://localhost:8080/docs for Swagger UI
```

**cURL:**
```bash
curl -X POST http://localhost:8080/api/v1/extract \
  -F "file=@statement.pdf" \
  -F "doc_type=bank_statement"
```

## Supported Document Types

### Bank Statement (`bank_statement`)
```json
{
  "account_number": "XXXX-XXXX",
  "account_holder": "SAMPLE ACCOUNT HOLDER",
  "bank_name": "SAMPLE BANK",
  "currency": "GHS",
  "statement_period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "opening_balance": 915.36,
  "closing_balance": 511.36,
  "transactions": [
    {
      "date": "2025-01-13",
      "description": "ATM WITHDRAWAL",
      "amount": -50.0,
      "balance": 865.36,
      "transaction_type": "DEBIT"
    },
    {
      "date": "2025-01-17",
      "description": "MOBILE MONEY TRANSFER",
      "amount": -354.0,
      "balance": 511.36,
      "transaction_type": "DEBIT"
    }
  ]
}
```

### Invoice (`invoice`)
```json
{
  "vendor_name": "SAMPLE SERVICER LLC",
  "client_name": "SAMPLE CUSTOMER",
  "invoice_date": "2026-01-07",
  "due_date": "2026-01-27",
  "total_amount": 378.49,
  "currency": "USD",
  "line_items": [
    { "description": "Applied to Principal", "total": 4.85 },
    { "description": "Applied to Interest", "total": 373.64 }
  ]
}
```

### Clinical Note (`clinical_note`)
```json
{
  "patient_id": "PT-00000",
  "provider_name": "Dr. Jane Doe, MD",
  "diagnoses": ["Acute bronchitis (J20.9)", "Mild asthma (J45.20)"],
  "medications": ["Albuterol PRN", "Montelukast 10mg"],
  "plan": "Start azithromycin, follow up in 2 weeks"
}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/schemas` | List extraction schemas |
| POST | `/api/v1/extract` | Upload PDF and extract |

## Project Structure
```
pdf-to-sql-pipeline/
+-- app/
¦   +-- main.py                    # FastAPI application
¦   +-- pipeline.py                # Core pipeline orchestration
¦   +-- config.py                  # Environment configuration
¦   +-- extractors/
¦   ¦   +-- docling_extractor.py   # Docling OCR (free, CPU-based)
¦   +-- mappers/
¦   ¦   +-- gemini_mapper.py       # Gemini Flash-Lite schema mapping
¦   +-- validators/
¦   ¦   +-- schema_validator.py    # Business rules validation
¦   +-- models/
¦       +-- document.py            # Pydantic schemas
+-- run_extract.py                 # CLI tool
+-- requirements.txt
+-- .env                           # API key (not committed)
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary OCR | Docling (free) over Document AI ($0.06/pg) | 85-90% cost savings, 97%+ accuracy on digital PDFs |
| LLM | Gemini Flash-Lite ($0.10/1M tokens) | Cheapest model with sufficient extraction accuracy |
| Validation | Pydantic + custom rules | Type safety + domain checks (balance matching, dates) |
| Framework | FastAPI | Auto OpenAPI docs, async, type hints |
| Architecture | Modular pipeline | Each stage independently testable and swappable |

## Roadmap

- [x] Docling OCR extraction with confidence scoring
- [x] Gemini Flash-Lite schema mapping with few-shot prompts
- [x] Business rules validation engine
- [x] FastAPI with Swagger UI
- [x] Bank statement, invoice, clinical note support
- [ ] Document AI fallback for scanned/handwritten docs
- [ ] Cloud Run deployment (public API)
- [ ] BigQuery integration for persistent storage
- [ ] IDP Quality Assurance verification layer (multi-agent)
- [ ] React dashboard for extraction results

## Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| OCR | [Docling](https://github.com/DS4SD/docling) (IBM, MIT) | Free |
| LLM | [Gemini 2.5 Flash-Lite](https://aistudio.google.com) | Free tier |
| API | [FastAPI](https://fastapi.tiangolo.com) | Free |
| Validation | [Pydantic v2](https://docs.pydantic.dev) | Free |

## Author

**Christopher Crilly Pienaah**
- MSc Analytics (Applied Machine Intelligence), Northeastern University
- AI/ML Product Strategist

## License

MIT
