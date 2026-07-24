import json, time, structlog
from typing import Any
from pydantic import ValidationError
from app.config import settings
from app.models.document import DocType, EXTRACTION_MODELS
logger = structlog.get_logger()
class GeminiMapper:
    def __init__(self):
        self._client = None
    def _get_client(self):
        if self._client is None:
            if not settings.gemini_configured:
                raise RuntimeError("Gemini API key not configured! Edit .env file.")
            from google import genai
            self._client = genai.Client(api_key=settings.gemini_api_key)
            logger.info("gemini.ready", model=settings.gemini_model)
        return self._client
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
            client = self._get_client()
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config={"temperature": settings.gemini_temperature, "max_output_tokens": settings.gemini_max_output_tokens, "response_mime_type": "application/json"},
            )
            txt = (response.text or "").strip()
            if txt.startswith("```"): txt = txt.split("\n",1)[1] if "\n" in txt else ""
            if txt.endswith("```"): txt = txt[:-3]
            data = json.loads(txt.strip())
            result = schema_model.model_validate(data).model_dump()
            tokens = (len(prompt)+len(txt))//4
            return result, tokens, None
        except (json.JSONDecodeError, ValidationError) as e:
            err = f"Gemini response could not be parsed ({type(e).__name__}): {str(e)[:200]}"
            logger.warning("gemini.parse_failed", error=err)
            return schema_model().model_dump(), 0, err
