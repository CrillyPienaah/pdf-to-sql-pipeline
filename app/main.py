import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.models.document import DocType, EXTRACTION_MODELS, ExtractionResponse
from app.pipeline import Pipeline

app = FastAPI(title="PDF-to-SQL Pipeline", version="0.1.0",
    description="Extract structured data from PDFs using Docling OCR + Gemini AI")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
pipeline = Pipeline()

@app.get("/health")
async def health():
    return {"status": "healthy", "gemini": settings.gemini_configured, "model": settings.gemini_model}

@app.get("/api/v1/schemas")
async def schemas():
    return {dt.value: {"fields": list(m.model_fields.keys())} for dt, m in EXTRACTION_MODELS.items()}

@app.post("/api/v1/extract", response_model=ExtractionResponse)
async def extract(file: UploadFile = File(...), doc_type: str = Form(...)):
    if doc_type not in [d.value for d in DocType]:
        raise HTTPException(400, f"Invalid doc_type. Use: {[d.value for d in DocType]}")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files supported")
    content = await file.read()
    if len(content) / 1048576 > settings.max_file_size_mb:
        raise HTTPException(413, "File too large")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    try:
        return pipeline.process(tmp_path, doc_type)
    finally:
        tmp_path.unlink(missing_ok=True)
