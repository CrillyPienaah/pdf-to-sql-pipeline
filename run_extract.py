
import sys, json
from pathlib import Path
if len(sys.argv)<3:
    print("  Usage: py run_extract.py <pdf> <doc_type>")
    print("  Types: bank_statement, invoice, clinical_note")
    sys.exit(1)
pdf, dtype = Path(sys.argv[1]), sys.argv[2]
if not pdf.exists(): print(f"  File not found: {pdf}"); sys.exit(1)
print(f"\n{'='*60}")
print(f"  PDF-to-SQL Pipeline | {pdf.name} | {dtype}")
print(f"{'='*60}")
from app.pipeline import Pipeline
r = Pipeline().process(pdf, dtype)
print(f"\n  Status: {r.status} | Cost: ${r.metadata.get('cost_usd',0):.6f}")
if r.validation_errors:
    for e in r.validation_errors: print(f"  Warning: {e}")
if r.extracted_data:
    print(f"\n{json.dumps(r.extracted_data, indent=2)}")
print(f"\n{'='*60}\n")
