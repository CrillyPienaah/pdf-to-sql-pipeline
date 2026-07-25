
import time, json, uuid
from pathlib import Path
from app.extractors.docling_extractor import DoclingExtractor
from app.mappers.gemini_mapper import GeminiMapper
from app.validators.schema_validator import SchemaValidator
from app.loaders.sqlite_loader import SQLiteLoader
from app.models.document import DocType, ExtractionResponse
from app.config import settings
class Pipeline:
    def __init__(self):
        self.extractor = DoclingExtractor()
        self.mapper = GeminiMapper()
        self.validator = SchemaValidator()
        self.loader = SQLiteLoader()
    def process(self, file_path, doc_type):
        start = time.time()
        file_path = Path(file_path)
        try: dt = DocType(doc_type)
        except ValueError:
            return ExtractionResponse(job_id="err",status="failed",doc_type=doc_type,validation_errors=["Invalid doc_type"])
        jid = str(uuid.uuid4())[:8]
        print(f"  [{jid}] Extracting with Docling...")
        ext = self.extractor.extract(file_path)
        print(f"  [{jid}] OCR done: {ext.num_pages} pages, confidence={ext.confidence:.2f}, {len(ext.tables)} tables")
        if ext.confidence < settings.docling_confidence_threshold:
            return ExtractionResponse(job_id=jid,status="failed",doc_type=doc_type,
                validation_errors=[f"OCR confidence too low ({ext.confidence:.2f})"],metadata={"confidence":ext.confidence})
        if not settings.gemini_configured:
            return ExtractionResponse(job_id=jid,status="needs_review",doc_type=doc_type,
                extracted_data={"_raw_text":ext.raw_text[:2000]},validation_errors=["Set GEMINI_API_KEY in .env"])
        print(f"  [{jid}] Mapping with Gemini...")
        try:
            data, tokens, map_error = self.mapper.map_to_schema(ext.raw_text, ext.tables, dt, ext.markdown)
        except Exception as e:
            return ExtractionResponse(job_id=jid,status="failed",doc_type=doc_type,
                validation_errors=[f"Gemini mapping failed: {e}"],metadata={"confidence":ext.confidence})
        valid, errors = self.validator.validate(data, dt)
        if map_error:
            errors.insert(0, map_error)
            valid = False
        status = "completed" if valid else "needs_review"
        cost = tokens * 0.0000002
        ms = int((time.time()-start)*1000)
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        out = settings.output_dir / f"{jid}_{file_path.stem}.json"
        with open(out,"w",encoding="utf-8") as f: json.dump({"job_id":jid,"status":status,"data":data,"errors":errors},f,indent=2,ensure_ascii=False)
        db = str(settings.db_path)
        try:
            self.loader.load(jid, dt, data, status, errors,
                {"source_file":file_path.name,"confidence":ext.confidence,"tokens":tokens,"cost_usd":cost,"time_ms":ms})
        except Exception as e:
            errors.append(f"SQL load failed: {e}")
            db = None
        print(f"  [{jid}] Done! Status={status}, cost=${cost:.6f}, time={ms}ms")
        return ExtractionResponse(job_id=jid,status=status,doc_type=doc_type,extracted_data=data,
            validation_errors=errors,metadata={"confidence":ext.confidence,"tokens":tokens,"cost_usd":cost,"time_ms":ms,"saved":str(out),"db":db})
