
import json, sqlite3
from pathlib import Path
from app.config import settings
from app.models.document import DocType

SCHEMA = """
CREATE TABLE IF NOT EXISTS extraction_jobs (
    job_id TEXT PRIMARY KEY,
    doc_type TEXT NOT NULL,
    status TEXT NOT NULL,
    source_file TEXT,
    confidence REAL,
    tokens INTEGER,
    cost_usd REAL,
    time_ms INTEGER,
    validation_errors TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS bank_statements (
    job_id TEXT PRIMARY KEY REFERENCES extraction_jobs(job_id) ON DELETE CASCADE,
    account_number TEXT, account_holder TEXT, bank_name TEXT,
    statement_period_start TEXT, statement_period_end TEXT,
    opening_balance REAL, closing_balance REAL, currency TEXT
);
CREATE TABLE IF NOT EXISTS bank_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES bank_statements(job_id) ON DELETE CASCADE,
    date TEXT, description TEXT, amount REAL, balance REAL, transaction_type TEXT
);
CREATE TABLE IF NOT EXISTS invoices (
    job_id TEXT PRIMARY KEY REFERENCES extraction_jobs(job_id) ON DELETE CASCADE,
    invoice_number TEXT, vendor_name TEXT, vendor_address TEXT, client_name TEXT,
    invoice_date TEXT, due_date TEXT, subtotal REAL, tax_amount REAL, total_amount REAL, currency TEXT
);
CREATE TABLE IF NOT EXISTS invoice_line_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL REFERENCES invoices(job_id) ON DELETE CASCADE,
    description TEXT, quantity REAL, unit_price REAL, total REAL
);
CREATE TABLE IF NOT EXISTS clinical_notes (
    job_id TEXT PRIMARY KEY REFERENCES extraction_jobs(job_id) ON DELETE CASCADE,
    patient_id TEXT, encounter_date TEXT, provider_name TEXT, chief_complaint TEXT,
    diagnoses TEXT, medications TEXT, procedures TEXT, assessment TEXT, plan TEXT
);
"""

class SQLiteLoader:
    """Loads validated extractions into a relational SQLite database (the SQL in pdf-to-sql)."""
    def __init__(self, db_path=None):
        self.db_path = Path(db_path or settings.db_path)

    def _connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA)
        return conn

    def load(self, job_id, doc_type, data, status, errors, meta):
        conn = self._connect()
        try:
            with conn:
                conn.execute(
                    "INSERT OR REPLACE INTO extraction_jobs (job_id,doc_type,status,source_file,confidence,tokens,cost_usd,time_ms,validation_errors) VALUES (?,?,?,?,?,?,?,?,?)",
                    (job_id, doc_type.value, status, meta.get("source_file"), meta.get("confidence"),
                     meta.get("tokens"), meta.get("cost_usd"), meta.get("time_ms"), json.dumps(errors)))
                if doc_type == DocType.BANK_STATEMENT:
                    conn.execute(
                        "INSERT OR REPLACE INTO bank_statements (job_id,account_number,account_holder,bank_name,statement_period_start,statement_period_end,opening_balance,closing_balance,currency) VALUES (?,?,?,?,?,?,?,?,?)",
                        (job_id, data.get("account_number"), data.get("account_holder"), data.get("bank_name"),
                         data.get("statement_period_start"), data.get("statement_period_end"),
                         data.get("opening_balance"), data.get("closing_balance"), data.get("currency")))
                    conn.execute("DELETE FROM bank_transactions WHERE job_id=?", (job_id,))
                    conn.executemany(
                        "INSERT INTO bank_transactions (job_id,date,description,amount,balance,transaction_type) VALUES (?,?,?,?,?,?)",
                        [(job_id, t.get("date"), t.get("description"), t.get("amount"), t.get("balance"), t.get("transaction_type"))
                         for t in data.get("transactions") or []])
                elif doc_type == DocType.INVOICE:
                    conn.execute(
                        "INSERT OR REPLACE INTO invoices (job_id,invoice_number,vendor_name,vendor_address,client_name,invoice_date,due_date,subtotal,tax_amount,total_amount,currency) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        (job_id, data.get("invoice_number"), data.get("vendor_name"), data.get("vendor_address"),
                         data.get("client_name"), data.get("invoice_date"), data.get("due_date"),
                         data.get("subtotal"), data.get("tax_amount"), data.get("total_amount"), data.get("currency")))
                    conn.execute("DELETE FROM invoice_line_items WHERE job_id=?", (job_id,))
                    conn.executemany(
                        "INSERT INTO invoice_line_items (job_id,description,quantity,unit_price,total) VALUES (?,?,?,?,?)",
                        [(job_id, li.get("description"), li.get("quantity"), li.get("unit_price"), li.get("total"))
                         for li in data.get("line_items") or []])
                elif doc_type == DocType.CLINICAL_NOTE:
                    conn.execute(
                        "INSERT OR REPLACE INTO clinical_notes (job_id,patient_id,encounter_date,provider_name,chief_complaint,diagnoses,medications,procedures,assessment,plan) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (job_id, data.get("patient_id"), data.get("encounter_date"), data.get("provider_name"),
                         data.get("chief_complaint"), json.dumps(data.get("diagnoses") or []),
                         json.dumps(data.get("medications") or []), json.dumps(data.get("procedures") or []),
                         data.get("assessment"), data.get("plan")))
        finally:
            conn.close()

    def list_jobs(self, limit=20):
        conn = self._connect()
        try:
            rows = conn.execute(
                "SELECT * FROM extraction_jobs ORDER BY created_at DESC, job_id LIMIT ?", (limit,)).fetchall()
            return [self._job_row(r) for r in rows]
        finally:
            conn.close()

    def get_job(self, job_id):
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM extraction_jobs WHERE job_id=?", (job_id,)).fetchone()
            if not row: return None
            job = self._job_row(row)
            dt = job["doc_type"]
            if dt == DocType.BANK_STATEMENT.value:
                s = conn.execute("SELECT * FROM bank_statements WHERE job_id=?", (job_id,)).fetchone()
                if s:
                    data = {k: s[k] for k in s.keys() if k != "job_id"}
                    data["transactions"] = [dict(t) for t in conn.execute(
                        "SELECT date,description,amount,balance,transaction_type FROM bank_transactions WHERE job_id=? ORDER BY id", (job_id,))]
                    job["extracted_data"] = data
            elif dt == DocType.INVOICE.value:
                s = conn.execute("SELECT * FROM invoices WHERE job_id=?", (job_id,)).fetchone()
                if s:
                    data = {k: s[k] for k in s.keys() if k != "job_id"}
                    data["line_items"] = [dict(li) for li in conn.execute(
                        "SELECT description,quantity,unit_price,total FROM invoice_line_items WHERE job_id=? ORDER BY id", (job_id,))]
                    job["extracted_data"] = data
            elif dt == DocType.CLINICAL_NOTE.value:
                s = conn.execute("SELECT * FROM clinical_notes WHERE job_id=?", (job_id,)).fetchone()
                if s:
                    data = {k: s[k] for k in s.keys() if k != "job_id"}
                    for k in ("diagnoses", "medications", "procedures"):
                        data[k] = json.loads(data[k] or "[]")
                    job["extracted_data"] = data
            return job
        finally:
            conn.close()

    @staticmethod
    def _job_row(row):
        job = dict(row)
        job["validation_errors"] = json.loads(job.get("validation_errors") or "[]")
        return job
