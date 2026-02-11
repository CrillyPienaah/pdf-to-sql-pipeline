
import json, time, structlog
from typing import Any
from app.config import settings
from app.models.document import DocType, EXTRACTION_MODELS
logger = structlog.get_logger()
class GeminiMapper:
    def __init__(self):
        self._model = None
    def _get_model(self):
        if self._model is None:
            if not settings.gemini_configured:
                raise RuntimeError("Gemini API key not configured! Edit .env file.")
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel(model_name=settings.gemini_model,
                generation_config={"temperature":0.1,"max_output_tokens":4096,"response_mime_type":"application/json"})
        return self._model
    def map_to_schema(self, raw_text, tables, doc_type, markdown=""):
        schema_model = EXTRACTION_MODELS[doc_type]
        tables_txt = ""
        if tables:
            for i,t in enumerate(tables):
                tables_txt += f"\n--- Table {i+1} ---\n"
                for r in t: tables_txt += " | ".join(str(c) for c in r) + "\n"
        content = markdown if markdown else raw_text
        prompt = f"""Extract structured data from this document. Return valid JSON matching the schema.
Rules: Extract ONLY what is in the document. Use empty string/null/[] for missing fields. Dates as YYYY-MM-DD. Money as numbers. Debits negative, credits positive.
Schema: {json.dumps(schema_model.model_json_schema())}
Document: {content[:12000]}
Tables: {tables_txt[:4000] if tables_txt else "None"}
Return JSON only."""
        try:
            resp = self._get_model().generate_content(prompt)
            txt = resp.text.strip()
            if txt.startswith("```"): txt = txt.split("\n",1)[1]
            if txt.endswith("```"): txt = txt[:-3]
            data = json.loads(txt.strip())
            result = schema_model.model_validate(data).model_dump()
            tokens = (len(prompt)+len(txt))//4
            return result, tokens
        except json.JSONDecodeError:
            return schema_model().model_dump(), 0
