import sys
from pathlib import Path

# Add project root to sys.path and configure stdout encoding
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database.db import init_db, get_db_connection
from database.repository import InvoiceRepository
from core.workflow import WorkflowOrchestrator
from config.settings import SAMPLE_INVOICES_DIR

def run_isolated_verification():
    # 1. Start with clean database
    init_db()
    conn = get_db_connection()
    conn.execute("DELETE FROM audit_events")
    conn.execute("DELETE FROM invoice_runs")
    conn.commit()
    conn.close()

    orch = WorkflowOrchestrator()

    print("\n" + "=" * 70)
    print("INVOICEIQ END-TO-END PIPELINE VERIFICATION RUN")
    print("=" * 70)

    # 1. HAPPY PATH
    f_happy = SAMPLE_INVOICES_DIR / "invoice_101_techcorp_happy_path.pdf"
    res_happy = orch.execute_workflow(f_happy.read_bytes(), f_happy.name)
    print(f"\n[1] HAPPY PATH: {f_happy.name}")
    print(f"    Decision:       {res_happy['decision']}")
    print(f"    Reason Code:    {res_happy['reason_code']}")
    print(f"    Vendor:         {res_happy['vendor_name']} ({res_happy['vendor_id']})")
    print(f"    Matched PO:     {res_happy['po_number']}")
    print(f"    Invoice Total:  ₹{res_happy['invoice_total']:,.2f}")
    print(f"    Variance:       ₹{res_happy['reconciliation_result']['variance_amount']:,.2f}")
    print(f"    Explanation:    {res_happy['explanation']}")
    print(f"    Duration:       {res_happy['duration_ms']:.2f} ms")

    # 2. EDGE CASE 1: ORIGINAL SUBMISSION THEN RENAMED DUPLICATE
    f_orig = SAMPLE_INVOICES_DIR / "invoice_102_greenlogistics_original.pdf"
    res_orig = orch.execute_workflow(f_orig.read_bytes(), f_orig.name)
    print(f"\n[2A] EDGE CASE 1 (Original Submission): {f_orig.name}")
    print(f"    Decision:       {res_orig['decision']}")
    print(f"    Run ID:         {res_orig['run_id']}")

    f_dupe = SAMPLE_INVOICES_DIR / "invoice_102_greenlogistics_duplicate_renamed.pdf"
    res_dupe = orch.execute_workflow(f_dupe.read_bytes(), f_dupe.name)
    print(f"\n[2B] EDGE CASE 1 (Renamed Duplicate Submission): {f_dupe.name}")
    print(f"    Decision:       {res_dupe['decision']}")
    print(f"    Reason Code:    {res_dupe['reason_code']}")
    print(f"    Prior Run ID:   {res_dupe['duplicate_result']['prior_run_id']}")
    print(f"    Explanation:    {res_dupe['explanation']}")

    # 3. EDGE CASE 2: AMOUNT MISMATCH
    f_mismatch = SAMPLE_INVOICES_DIR / "invoice_103_apex_amount_mismatch.pdf"
    res_mismatch = orch.execute_workflow(f_mismatch.read_bytes(), f_mismatch.name)
    print(f"\n[3] EDGE CASE 2 (Amount Mismatch): {f_mismatch.name}")
    print(f"    Decision:       {res_mismatch['decision']}")
    print(f"    Reason Code:    {res_mismatch['reason_code']}")
    print(f"    Invoice Total:  ₹{res_mismatch['invoice_total']:,.2f}")
    print(f"    PO Applicable:  ₹{res_mismatch['reconciliation_result']['po_applicable_amount']:,.2f}")
    print(f"    Variance:       ₹{res_mismatch['reconciliation_result']['variance_amount']:,.2f} ({res_mismatch['reconciliation_result']['variance_pct']}%)")
    print(f"    Tolerance Cap:  ₹{res_mismatch['reconciliation_result']['tolerance_threshold_amount']:,.2f}")
    print(f"    Explanation:    {res_mismatch['explanation']}")

    # 4. EDGE CASE 3: MISSING INFORMATION
    f_missing = SAMPLE_INVOICES_DIR / "invoice_104_techcorp_missing_po.pdf"
    res_missing = orch.execute_workflow(f_missing.read_bytes(), f_missing.name)
    print(f"\n[4] EDGE CASE 3 (Missing Information): {f_missing.name}")
    print(f"    Decision:       {res_missing['decision']}")
    print(f"    Reason Code:    {res_missing['reason_code']}")
    print(f"    PO Matched:     {res_missing['po_number']} (Type: {res_missing['po_result']['match_type']})")
    print(f"    Explanation:    {res_missing['explanation']}")

    # 5. EDGE CASE 4: SCANNED / LOW-QUALITY OCR
    f_scanned = SAMPLE_INVOICES_DIR / "invoice_105_bharat_scanned.pdf"
    res_scanned = orch.execute_workflow(f_scanned.read_bytes(), f_scanned.name)
    print(f"\n[5] EDGE CASE 4 (Scanned / OCR Fallback): {f_scanned.name}")
    print(f"    Decision:       {res_scanned['decision']}")
    print(f"    Reason Code:    {res_scanned['reason_code']}")
    print(f"    Extraction Mode:{res_scanned['extraction_mode']}")
    print(f"    OCR Applied:    {res_scanned['extracted_data']['ocr_applied']}")
    print(f"    Explanation:    {res_scanned['explanation']}")

    # 6. VERIFY PERSISTENCE & DASHBOARD AGGREGATIONS
    repo = InvoiceRepository()
    kpis = repo.get_kpis()
    print("\n" + "=" * 70)
    print("SQLITE DATABASE PERSISTENCE & KPI AGGREGATION CHECK")
    print("=" * 70)
    print(f"Total Processed: {kpis['total_processed']}")
    print(f"Approved:        {kpis['approved']}")
    print(f"Pending Review:  {kpis['pending_review']}")
    print(f"Rejected:        {kpis['rejected']}")
    print(f"Avg Duration:    {kpis['avg_duration_ms']:.2f} ms")
    print(f"Recent Runs in DB: {len(repo.list_runs())}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    run_isolated_verification()
