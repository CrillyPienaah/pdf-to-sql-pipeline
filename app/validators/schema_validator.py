
import re
from app.models.document import DocType
class SchemaValidator:
    def validate(self, data, doc_type):
        errors = []
        filled = sum(1 for v in data.values() if v and v != [] and v != {} and v != "" and v != 0)
        if filled < 2: errors.append("Extraction mostly empty")
        if doc_type == DocType.BANK_STATEMENT:
            o,c,t = data.get("opening_balance"), data.get("closing_balance"), data.get("transactions",[])
            if o is not None and c is not None and t:
                s = sum(x.get("amount",0) for x in t)
                if abs((o+s)-c) > abs(c)*0.01+0.01: errors.append(f"Balance mismatch")
        if doc_type == DocType.INVOICE:
            s,tx,tot = data.get("subtotal"), data.get("tax_amount"), data.get("total_amount")
            if s is not None and tx is not None and tot is not None:
                if abs((s+tx)-tot)>0.02: errors.append("Total mismatch")
        if doc_type == DocType.CLINICAL_NOTE:
            if not data.get("provider_name"): errors.append("Missing provider")
        return len(errors)==0, errors
