import pytest
from decimal import Decimal
from pathlib import Path
from database.db import init_db, get_db_connection
from database.repository import InvoiceRepository
from core.workflow import WorkflowOrchestrator
from core.models import DecisionOutcome
from config.settings import SAMPLE_INVOICES_DIR

@pytest.fixture(autouse=True)
def clean_test_db():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    # Clean previous split PO test runs
    cursor.execute("DELETE FROM invoice_runs WHERE po_number = 'PO-2024-009'")
    cursor.execute("DELETE FROM invoice_runs WHERE invoice_number LIKE 'INV-SPLIT-%'")
    conn.commit()
    conn.close()
    yield
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoice_runs WHERE po_number = 'PO-2024-009'")
    cursor.execute("DELETE FROM invoice_runs WHERE invoice_number LIKE 'INV-SPLIT-%'")
    conn.commit()
    conn.close()

def test_split_po_cumulative_reconciliation():
    repo = InvoiceRepository()
    orchestrator = WorkflowOrchestrator(repository=repo)

    # 1. Invoice A: Milestone 1 (₹40,000 on ₹1,00,000 PO)
    p1 = SAMPLE_INVOICES_DIR / "invoice_201_techcorp_split_po_part1.pdf"
    assert p1.exists()
    run1 = orchestrator.execute_workflow(p1.read_bytes(), p1.name)
    assert run1["decision"] == DecisionOutcome.APPROVED.value
    assert run1["reason_code"] == "VALIDATION_PASSED_CLEAN"
    assert float(run1["invoice_total"]) == 40000.00
    assert run1["po_result"]["is_partial_invoice"] is True
    assert run1["reconciliation_result"]["is_partial_invoice"] is True
    assert float(run1["reconciliation_result"]["remaining_balance_after"]) == 60000.00

    # Verify SQLite cumulative balance tracking
    cum_billed_1 = repo.get_cumulative_billed_for_po("PO-2024-009")
    assert cum_billed_1 == Decimal("40000.00")

    # 2. Invoice B: Milestone 2 (₹35,000 on remaining ₹60,000)
    p2 = SAMPLE_INVOICES_DIR / "invoice_202_techcorp_split_po_part2.pdf"
    assert p2.exists()
    run2 = orchestrator.execute_workflow(p2.read_bytes(), p2.name)
    assert run2["decision"] == DecisionOutcome.APPROVED.value
    assert run2["reason_code"] == "VALIDATION_PASSED_CLEAN"
    assert float(run2["invoice_total"]) == 35000.00
    assert float(run2["reconciliation_result"]["remaining_balance_before"]) == 60000.00
    assert float(run2["reconciliation_result"]["remaining_balance_after"]) == 25000.00

    cum_billed_2 = repo.get_cumulative_billed_for_po("PO-2024-009")
    assert cum_billed_2 == Decimal("75000.00")

    # 3. Invoice C: Milestone 3 (₹25,000 on remaining ₹25,000)
    p3 = SAMPLE_INVOICES_DIR / "invoice_203_techcorp_split_po_part3.pdf"
    assert p3.exists()
    run3 = orchestrator.execute_workflow(p3.read_bytes(), p3.name)
    assert run3["decision"] == DecisionOutcome.APPROVED.value
    assert float(run3["invoice_total"]) == 25000.00
    assert float(run3["reconciliation_result"]["remaining_balance_before"]) == 25000.00
    assert float(run3["reconciliation_result"]["remaining_balance_after"]) == 0.00

    cum_billed_3 = repo.get_cumulative_billed_for_po("PO-2024-009")
    assert cum_billed_3 == Decimal("100000.00")

    # 4. Invoice D: Exceeds remaining balance (₹15,000 on ₹0.00 remaining balance)
    p4 = SAMPLE_INVOICES_DIR / "invoice_204_techcorp_split_po_exceeded.pdf"
    assert p4.exists()
    run4 = orchestrator.execute_workflow(p4.read_bytes(), p4.name)
    assert run4["decision"] == DecisionOutcome.PENDING_REVIEW.value
    assert run4["reason_code"] == "EXCEEDS_REMAINING_PO_BALANCE"
    assert run4["reconciliation_result"]["exceeds_remaining_balance"] is True
    assert "exceeds the available remaining PO balance" in run4["explanation"]

    # 5. Verify that sharing PO-2024-009 did NOT falsely trigger duplicate detection
    assert run1["duplicate_result"]["is_duplicate"] is False
    assert run2["duplicate_result"]["is_duplicate"] is False
    assert run3["duplicate_result"]["is_duplicate"] is False
    assert run4["duplicate_result"]["is_duplicate"] is False
