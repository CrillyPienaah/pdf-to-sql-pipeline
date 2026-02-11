# PDF-to-SQL Pipeline API

**Hybrid OCR + LLM extraction pipeline that converts unstructured PDFs into queryable SQL data.**

Built on GCP with a cost-optimized architecture: open-source OCR (Docling) as primary extractor, Google Document AI as premium fallback, and Gemini 2.5 Flash-Lite for intelligent schema mapping.

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌───────────────────┐     ┌──────────────┐
│  Client      │────▶│  Cloud Run   │────▶│  Extraction Layer │────▶│  BigQuery /  │
│  (Upload PDF)│     │  (FastAPI)   │     │                   │     │  Cloud SQL   │
└─────────────┘     └──────────────┘     │  ┌─────────────┐  │     └──────────────┘
                                          │  │ Docling      │  │
                                          │  │ (Primary,    │  │
                                          │  │  Free, CPU)  │  │
                                          │  └──────┬───────┘  │
                                          │         │          │
                                          │    Low confidence? │
                                          │         │          │
                                          │  ┌──────▼───────┐  │
                                          │  │ Document AI   │  │
                                          │  │ (Fallback,    │  │
                                          │  │  $0.06/page)  │  │
                                          │  └──────┬───────┘  │
                                          │         │          │
                                          │  ┌──────▼───────┐  │
                                          │  │ Gemini Flash  │  │
                                          │  │ Lite (Schema  │  │
                                          │  │  Mapping)     │  │
                                          │  └───────────────┘  │
                                          └───────────────────┘
```

## Cost Comparison

| Approach | Dev (500 pages/mo) | Production (10K pages/mo) |
|----------|-------------------|--------------------------|
| Full GCP Managed | ~$37/mo | ~$640/mo |
| **This Hybrid Approach** | **~$10-15/mo** | **~$80-120/mo** |

## Project Structure

```
pdf-to-sql-pipeline/
├── services/pdf-pipeline/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry
│   │   ├── config.py               # Environment & GCP config
│   │   ├── routers/
│   │   │   ├── upload.py           # PDF upload endpoints
│   │   │   ├── extract.py          # Extraction status & results
│   │   │   └── health.py           # Health check
│   │   ├── extractors/
│   │   │   ├── base.py             # Abstract extractor interface
│   │   │   ├── docling_extractor.py    # Primary: Docling (free)
│   │   │   ├── documentai_extractor.py # Fallback: Document AI
│   │   │   └── hybrid_orchestrator.py  # Routes to best extractor
│   │   ├── mappers/
│   │   │   ├── schema_mapper.py    # Gemini Flash-Lite mapping
│   │   │   └── prompts.py          # Domain-specific prompts
│   │   ├── validators/
│   │   │   ├── schema_validator.py # SQL schema validation
│   │   │   └── rules.py           # Business rules per doc type
│   │   ├── models/
│   │   │   ├── document.py         # Pydantic models
│   │   │   └── extraction.py       # Extraction result models
│   │   └── utils/
│   │       ├── gcs.py              # Cloud Storage helpers
│   │       ├── bigquery.py         # BigQuery write helpers
│   │       └── monitoring.py       # Metrics & logging
│   ├── tests/
│   │   ├── test_extractors.py
│   │   ├── test_mapper.py
│   │   ├── test_validators.py
│   │   └── conftest.py
│   ├── configs/
│   │   ├── schemas/                # Target SQL schemas per doc type
│   │   │   ├── bank_statement.json
│   │   │   ├── invoice.json
│   │   │   └── clinical_note.json
│   │   └── prompts/                # Few-shot prompt templates
│   │       ├── financial.yaml
│   │       ├── healthcare.yaml
│   │       └── legal.yaml
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── infra/terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── scripts/
│   ├── deploy.sh
│   └── test_local.sh
├── docs/
│   └── api_spec.md
├── .gitignore
├── .gcloudignore
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Google Cloud SDK (`gcloud`)
- Docker
- VS Code with extensions: Google Cloud Code, Python, Docker, REST Client

### Local Development

```bash
# 1. Clone and setup
cd pdf-to-sql-pipeline
python -m venv venv
source venv/bin/activate
pip install -r services/pdf-pipeline/requirements.txt

# 2. Configure environment
cp services/pdf-pipeline/.env.example services/pdf-pipeline/.env
# Edit .env with your GCP project ID and credentials

# 3. Run locally
cd services/pdf-pipeline
uvicorn app.main:app --reload --port 8080

# 4. Test with a sample PDF
curl -X POST http://localhost:8080/api/v1/extract \
  -F "file=@sample.pdf" \
  -F "doc_type=bank_statement"
```

### Deploy to Cloud Run

```bash
./scripts/deploy.sh
```

## Supported Document Types

| Document Type | Primary Extractor | Fields Extracted |
|--------------|-------------------|-----------------|
| Bank Statement | Docling | account_number, transactions[], balance, date_range |
| Invoice | Docling | vendor, amount, line_items[], due_date, tax |
| Clinical Note | Docling + Fallback | patient_id, diagnosis[], medications[], provider |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/extract` | Upload PDF and extract to structured data |
| GET | `/api/v1/extract/{job_id}` | Get extraction result by job ID |
| GET | `/api/v1/schemas` | List available target schemas |
| GET | `/health` | Health check |

## License

MIT
