import sqlite3
from pathlib import Path
from config.settings import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database schema with all required tables and indexes."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_runs (
        run_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_hash TEXT NOT NULL,
        file_size_bytes INTEGER NOT NULL,
        page_count INTEGER NOT NULL,
        invoice_number TEXT,
        invoice_date TEXT,
        vendor_id TEXT,
        vendor_name TEXT,
        po_number TEXT,
        invoice_total REAL,
        currency TEXT DEFAULT 'INR',
        extraction_mode TEXT,
        decision TEXT NOT NULL,
        reason_code TEXT,
        explanation TEXT,
        recommended_action TEXT,
        stages_log_json TEXT,
        extracted_data_json TEXT,
        vendor_result_json TEXT,
        duplicate_result_json TEXT,
        po_result_json TEXT,
        reconciliation_result_json TEXT,
        decision_result_json TEXT,
        created_at TEXT NOT NULL,
        duration_ms REAL DEFAULT 0.0,
        status TEXT DEFAULT 'COMPLETED',
        reviewer_decision TEXT,
        reviewer_notes TEXT,
        reviewed_at TEXT,
        corrected_fields_json TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
        event_id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        event_type TEXT NOT NULL,
        actor TEXT NOT NULL,
        details_json TEXT,
        FOREIGN KEY (run_id) REFERENCES invoice_runs(run_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS seller_responses (
        response_id TEXT PRIMARY KEY,
        run_id TEXT,
        vendor_id TEXT,
        vendor_name TEXT NOT NULL,
        invoice_number TEXT NOT NULL,
        po_number TEXT,
        discrepancy_type TEXT NOT NULL,
        disputed_amount REAL NOT NULL,
        vendor_explanation TEXT NOT NULL,
        evidence_file TEXT,
        status TEXT DEFAULT 'PENDING_BUYER_ACTION',
        buyer_action TEXT,
        buyer_notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disputes (
        dispute_id TEXT PRIMARY KEY,
        run_id TEXT,
        vendor_name TEXT NOT NULL,
        invoice_number TEXT NOT NULL,
        po_number TEXT,
        dispute_category TEXT NOT NULL,
        disputed_amount REAL NOT NULL,
        status TEXT DEFAULT 'OPEN',
        resolution_summary TEXT,
        created_at TEXT NOT NULL,
        resolved_at TEXT
    );
    """)

    # Create indexes for fast lookup and duplicate detection
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_file_hash ON invoice_runs(file_hash);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_vendor_invoice ON invoice_runs(vendor_id, invoice_number);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_decision ON invoice_runs(decision);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_runs_created_at ON invoice_runs(created_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_run_id ON audit_events(run_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seller_resp_status ON seller_responses(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_disputes_status ON disputes(status);")

    # Seed initial seller responses if table is empty
    cursor.execute("SELECT COUNT(*) FROM seller_responses;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO seller_responses (
            response_id, run_id, vendor_id, vendor_name, invoice_number, po_number,
            discrepancy_type, disputed_amount, vendor_explanation, evidence_file,
            status, created_at
        ) VALUES 
        (
            'RESP-2024-001', 'RUN-103', 'VEND-002', 'Apex Cloud Infrastructure LLC', 'INV-2024-003', 'PO-2024-002',
            'PO_AMOUNT_MISMATCH (+14.0% Unit Price Variance)', 7000.00,
            'The invoice reflects an authorized unit rate revision from ₹50,000 to ₹57,000 due to expedited provisioning and memory expansion approved via Change Order CO-882 by Engineering Lead.',
            'Change_Order_CO-882_Signoff.pdf',
            'PENDING_BUYER_ACTION', '2024-11-10 14:32:00'
        ),
        (
            'RESP-2024-002', 'RUN-104', 'VEND-001', 'TechCorp Solutions Private Limited', 'INV-2024-004', 'PO-2024-004',
            'PO_NOT_FOUND (Missing PO Reference on Invoice)', 45000.00,
            'Original invoice omitted purchase order number due to an automated ERP billing batch error. This billing corresponds to approved PO-2024-004 (Consulting Sprint). Attached is the signed purchase order confirmation.',
            'PO-2024-004_Signed_PO.pdf',
            'PENDING_BUYER_ACTION', '2024-11-12 09:15:00'
        );
        """)

    # Seed initial disputes if table is empty
    cursor.execute("SELECT COUNT(*) FROM disputes;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO disputes (
            dispute_id, run_id, vendor_name, invoice_number, po_number,
            dispute_category, disputed_amount, status, resolution_summary,
            created_at, resolved_at
        ) VALUES
        (
            'DSP-101', 'RUN-103', 'Apex Cloud Infrastructure LLC', 'INV-2024-003', 'PO-2024-002',
            'Unit Price Variance', 7000.00, 'OPEN', 'Awaiting buyer sign-off on change order CO-882.',
            '2024-11-10 14:35:00', NULL
        ),
        (
            'DSP-102', 'RUN-104', 'TechCorp Solutions Private Limited', 'INV-2024-004', 'PO-2024-004',
            'Missing Procurement Reference', 45000.00, 'OPEN', 'Vendor submitted PO documentation for reconciliation.',
            '2024-11-12 09:20:00', NULL
        ),
        (
            'DSP-103', 'RUN-102', 'GreenLogistics Global Services Inc', 'INV-2024-002', 'PO-2024-003',
            'Duplicate Invoice Collision', 84000.00, 'RESOLVED', 'Duplicate invoice rejected per policy; credit memo confirmed.',
            '2024-11-08 11:00:00', '2024-11-09 16:30:00'
        ),
        (
            'DSP-104', 'RUN-105', 'Bharat Security Systems & Automation', 'INV-2024-005', 'PO-2024-005',
            'Tax Calculation Variance', 1240.00, 'RESOLVED', 'Tax variance reconciled within statutory rounding tolerance.',
            '2024-11-05 10:15:00', '2024-11-06 14:00:00'
        );
        """)

    conn.commit()
    conn.close()
