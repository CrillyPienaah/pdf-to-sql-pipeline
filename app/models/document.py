
from enum import Enum
from typing import Any
from pydantic import BaseModel
class DocType(str, Enum):
    BANK_STATEMENT = "bank_statement"
    INVOICE = "invoice"
    CLINICAL_NOTE = "clinical_note"
class BankTransaction(BaseModel):
    date: str | None = ""
    description: str | None = ""
    amount: float = 0.0
    balance: float | None = None
    transaction_type: str | None = ""
class BankStatementExtraction(BaseModel):
    account_number: str | None = ""
    account_holder: str | None = ""
    bank_name: str | None = ""
    statement_period_start: str | None = ""
    statement_period_end: str | None = ""
    opening_balance: float | None = None
    closing_balance: float | None = None
    currency: str = "USD"
    transactions: list[BankTransaction] = []
class InvoiceLineItem(BaseModel):
    description: str | None = ""
    quantity: float = 1.0
    unit_price: float = 0.0
    total: float = 0.0
class InvoiceExtraction(BaseModel):
    invoice_number: str | None = ""
    vendor_name: str | None = ""
    vendor_address: str | None = ""
    client_name: str | None = ""
    invoice_date: str | None = ""
    due_date: str | None = ""
    subtotal: float | None = None
    tax_amount: float | None = None
    total_amount: float | None = None
    currency: str = "USD"
    line_items: list[InvoiceLineItem] = []
class ClinicalNoteExtraction(BaseModel):
    patient_id: str | None = ""
    encounter_date: str | None = ""
    provider_name: str | None = ""
    chief_complaint: str | None = ""
    diagnoses: list[str] = []
    medications: list[str] = []
    procedures: list[str] = []
    assessment: str | None = ""
    plan: str | None = ""
EXTRACTION_MODELS: dict[DocType, type[BaseModel]] = {DocType.BANK_STATEMENT: BankStatementExtraction, DocType.INVOICE: InvoiceExtraction, DocType.CLINICAL_NOTE: ClinicalNoteExtraction}
class ExtractionResponse(BaseModel):
    job_id: str
    status: str
    doc_type: str
    extracted_data: dict[str, Any] | None = None
    validation_errors: list[str] = []
    metadata: dict[str, Any] = {}
