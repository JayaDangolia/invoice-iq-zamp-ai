import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ensure using main invoiceiq.db
os.environ.pop("INVOICEIQ_DB_PATH", None)

from config.settings import DB_PATH, SAMPLE_INVOICES_DIR
from database.db import init_db, get_db_connection
from database.repository import InvoiceRepository
from core.workflow import WorkflowOrchestrator

def seed():
    print(f"Connecting to database at {DB_PATH}")
    init_db()
    conn = get_db_connection()
    conn.execute("DELETE FROM audit_events")
    conn.execute("DELETE FROM invoice_runs")
    conn.commit()
    conn.close()

    repo = InvoiceRepository()
    orch = WorkflowOrchestrator(repository=repo)

    files_sequence = [
        "invoice_101_techcorp_happy_path.pdf",
        "invoice_102_greenlogistics_original.pdf",
        "invoice_106_synergy_consulting.pdf",
        "invoice_201_techcorp_split_po_part1.pdf",
        "invoice_202_techcorp_split_po_part2.pdf",
        "invoice_203_techcorp_split_po_part3.pdf",
        "invoice_102_greenlogistics_duplicate_renamed.pdf",
        "invoice_107_quantum_unapproved_vendor.pdf",
        "invoice_103_apex_amount_mismatch.pdf",
        "invoice_104_techcorp_missing_po.pdf",
        "invoice_105_bharat_scanned.pdf",
        "invoice_204_techcorp_split_po_exceeded.pdf",
        "invoice_205_techcorp_ambiguous_po.pdf",
    ]

    print("Executing 13 sample invoices through WorkflowOrchestrator...")
    for idx, fname in enumerate(files_sequence, 1):
        fpath = SAMPLE_INVOICES_DIR / fname
        if not fpath.exists():
            print(f"WARNING: File {fname} not found!")
            continue
        run = orch.execute_workflow(
            file_bytes=fpath.read_bytes(),
            filename=fname
        )
        print(f"[{idx:02d}/14] Processed {fname:<45} -> {run['decision']:<15} ({run.get('reason_code', 'OK')})")

    # Process 14th run: duplicate of invoice_101 to get exactly 3 REJECTED and 2 DUPLICATES
    fpath = SAMPLE_INVOICES_DIR / "invoice_101_techcorp_happy_path.pdf"
    run14 = orch.execute_workflow(
        file_bytes=fpath.read_bytes(),
        filename="invoice_101_techcorp_duplicate_resubmission.pdf"
    )
    print(f"[14/14] Processed duplicate resubmission -> {run14['decision']:<15} ({run14.get('reason_code', 'OK')})")

    # Mark invoice 103 as manually reviewed in the Review Queue audit trail (from previous human review)
    # to demonstrate audit trail & reviewer resolution
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT run_id FROM invoice_runs WHERE filename = 'invoice_103_apex_amount_mismatch.pdf' ORDER BY created_at DESC LIMIT 1")
    row = c.fetchone()
    if row:
        run_103_id = row[0]
        repo.update_reviewer_action(
            run_id=run_103_id,
            reviewer_decision="MANUALLY_APPROVED",
            reviewer_notes="Verified physical PO variance with purchasing manager. Approved under change order.",
            corrected_fields={"approved_amount": 57000.0}
        )
        print(f"Applied human review record to {run_103_id}")

    # Verify final KPIs
    kpis = repo.get_kpis()
    print("\nFINAL DATABASE KPIS:")
    print(kpis)

if __name__ == "__main__":
    seed()
