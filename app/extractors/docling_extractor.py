
import time, structlog
from pathlib import Path
from dataclasses import dataclass, field
logger = structlog.get_logger()
@dataclass
class ExtractionResult:
    raw_text: str = ""
    markdown: str = ""
    tables: list = field(default_factory=list)
    num_pages: int = 0
    confidence: float = 0.0
    processing_time_ms: int = 0
class DoclingExtractor:
    def __init__(self):
        self._converter = None
    def _get_converter(self):
        if self._converter is None:
            print("  Loading Docling (first time takes 10-30s)...")
            from docling.document_converter import DocumentConverter
            self._converter = DocumentConverter()
            print("  Docling ready!")
        return self._converter
    def extract(self, file_path):
        file_path = Path(file_path)
        start = time.time()
        try:
            conv = self._get_converter()
            result = conv.convert(str(file_path))
            doc = result.document
            md = doc.export_to_markdown()
            texts, tables, pages = [], [], 0
            for item, _ in doc.iterate_items():
                if hasattr(item, "prov") and item.prov:
                    pages = max(pages, (item.prov[0].page_no if item.prov else 0) + 1)
                if hasattr(item, "text") and item.text:
                    texts.append(item.text)
                if "table" in type(item).__name__.lower() and hasattr(item, "export_to_dataframe"):
                    try:
                        df = item.export_to_dataframe()
                        t = [df.columns.tolist()] + [[str(c) for c in r] for r in df.values.tolist()]
                        tables.append(t)
                    except: pass
            raw = chr(10).join(texts)
            words = raw.split()
            conf = 0.1 if len(words) < 5 else round(min(max(sum(1 for w in words if sum(c.isalnum() for c in w)/max(len(w),1)>0.6)/len(words)*0.7+min(len(raw)/500,1)*0.3,0),1),3)
            ms = int((time.time()-start)*1000)
            return ExtractionResult(raw, md, tables, max(pages,1), conf, ms)
        except Exception as e:
            print(f"  OCR Error: {e}")
            return ExtractionResult(processing_time_ms=int((time.time()-start)*1000))
