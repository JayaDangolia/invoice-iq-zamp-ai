import pytest
from pathlib import Path
from core.workflow import WorkflowOrchestrator
from database.repository import InvoiceRepository
from database.db import init_db, get_db_connection
from config.settings import SAMPLE_INVOICES_DIR

@pytest.fixture(autouse=True)
def clean_test_db():
    init_db()
    conn = get_db_connection()
    conn.execute("DELETE FROM audit_events")
    conn.execute("DELETE FROM invoice_runs")
    conn.commit()
    conn.close()

def test_happy_path_workflow():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_101_techcorp_happy_path.pdf"
    assert pdf_path.exists()
    
    orchestrator = WorkflowOrchestrator()
    run = orchestrator.execute_workflow(
        file_bytes=pdf_path.read_bytes(),
        filename=pdf_path.name
    )

    assert run["decision"] == "APPROVED"
    assert run["status"] == "COMPLETED"
    assert run["vendor_id"] == "VEND-001"
    assert run["po_number"] == "PO-2024-001"
    assert run["invoice_total"] == 125000.0
    assert len(run["stages_log"]) == 11
    # All stages completed successfully
    for s in run["stages_log"]:
        assert s["status"] in ("SUCCESS", "WARNING")

def test_edge_case_1_duplicate_workflow():
    pdf_orig = SAMPLE_INVOICES_DIR / "invoice_102_greenlogistics_original.pdf"
    pdf_dupe = SAMPLE_INVOICES_DIR / "invoice_102_greenlogistics_duplicate_renamed.pdf"
    
    orchestrator = WorkflowOrchestrator()
    
    # Process original submission
    run1 = orchestrator.execute_workflow(
        file_bytes=pdf_orig.read_bytes(),
        filename=pdf_orig.name
    )
    assert run1["decision"] in ("APPROVED", "PENDING REVIEW")

    # Process renamed duplicate file
    run2 = orchestrator.execute_workflow(
        file_bytes=pdf_dupe.read_bytes(),
        filename=pdf_dupe.name
    )
    assert run2["decision"] == "REJECTED"
    assert run2["reason_code"] == "DUPLICATE_INVOICE_SUBMISSION"
    assert "duplicate" in run2["explanation"].lower()

def test_edge_case_2_amount_mismatch_workflow():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_103_apex_amount_mismatch.pdf"
    orchestrator = WorkflowOrchestrator()
    
    run = orchestrator.execute_workflow(
        file_bytes=pdf_path.read_bytes(),
        filename=pdf_path.name
    )

    assert run["decision"] == "PENDING REVIEW"
    assert run["reason_code"] == "FINANCIAL_VARIANCE_EXCEEDS_TOLERANCE"
    assert "7,000" in run["explanation"]
    assert "14%" in run["explanation"]

def test_edge_case_3_missing_po_workflow():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_104_techcorp_missing_po.pdf"
    orchestrator = WorkflowOrchestrator()
    
    run = orchestrator.execute_workflow(
        file_bytes=pdf_path.read_bytes(),
        filename=pdf_path.name
    )

    # PO reference is missing from PDF; verified vendor has PO-2024-004
    assert run["status"] == "COMPLETED"
    assert run["decision"] in ("PENDING REVIEW", "APPROVED")

def test_edge_case_4_scanned_pdf_workflow():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_105_bharat_scanned.pdf"
    orchestrator = WorkflowOrchestrator()
    
    run = orchestrator.execute_workflow(
        file_bytes=pdf_path.read_bytes(),
        filename=pdf_path.name
    )

    assert run["status"] == "COMPLETED"
    assert run["extracted_data"]["ocr_applied"] is True
    # Stage 3 should show OCR execution
    stage3 = run["stages_log"][2]
    assert stage3["status"] == "SUCCESS"
    assert "ocr" in stage3["message"].lower()

def test_ambiguous_po_workflow():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_205_techcorp_ambiguous_po.pdf"
    orchestrator = WorkflowOrchestrator()
    run = orchestrator.execute_workflow(pdf_path.read_bytes(), pdf_path.name)
    assert run["status"] == "COMPLETED"
    assert run["decision"] == "PENDING REVIEW"
    assert run["po_result"]["match_type"] == "AMBIGUOUS"
    assert run["po_result"]["candidate_po_count"] >= 2
    assert len(run["po_result"]["candidate_pos"]) >= 2

def test_reviewer_manual_action():
    # Process an amount mismatch to generate a pending review record
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_103_apex_amount_mismatch.pdf"
    orchestrator = WorkflowOrchestrator()
    run = orchestrator.execute_workflow(pdf_path.read_bytes(), pdf_path.name)
    
    repo = InvoiceRepository()
    run_id = run["run_id"]
    repo.update_reviewer_action(
        run_id=run_id,
        reviewer_decision="MANUALLY_APPROVED",
        reviewer_notes="Verified physical PO variance with purchasing manager.",
        corrected_fields={"invoice_total": 57000.0}
    )

    updated = repo.get_run(run_id)
    assert updated["reviewer_decision"] == "MANUALLY_APPROVED"
    assert "Verified" in updated["reviewer_notes"]
    assert updated["decision"] == "PENDING REVIEW"  # Original automated decision remains preserved!
