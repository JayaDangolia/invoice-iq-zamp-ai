import pytest
from decimal import Decimal
from core.models import (
    DecisionOutcome,
    ExtractedInvoiceData,
    VendorValidationResult,
    DuplicateDetectionResult,
    POMatchingResult,
    ReconciliationResult,
)
from services.reconciliation_service import ReconciliationService
from services.decision_engine import DecisionEngine

def test_financial_reconciliation_within_tolerance():
    recon_service = ReconciliationService()
    # Applicable PO = 100,000. 2% tolerance = 2,000, capped at 500. So threshold is 500.
    # Invoice = 100,300 (Variance = 300 <= 500) -> within tolerance
    extracted = ExtractedInvoiceData(invoice_total=Decimal("100300.00"), subtotal=Decimal("100300.00"), tax=Decimal("0.00"))
    po_match = POMatchingResult(is_matched=True, po_number="PO-1", po_total=Decimal("100000.00"), po_status="OPEN")
    
    recon = recon_service.reconcile(extracted, po_match)
    assert recon.within_tolerance is True
    assert recon.variance_amount == Decimal("300.00")
    assert recon.tolerance_threshold_amount == Decimal("500.00")

def test_financial_reconciliation_exceeds_tolerance():
    recon_service = ReconciliationService()
    # Applicable PO = 50,000. 2% = 1,000, capped at 500. So threshold is 500.
    # Invoice = 57,000 (Variance = 7,000 = 14% > 500) -> exceeds tolerance
    extracted = ExtractedInvoiceData(invoice_total=Decimal("57000.00"), subtotal=Decimal("57000.00"), tax=Decimal("0.00"))
    po_match = POMatchingResult(is_matched=True, po_number="PO-2024-002", po_total=Decimal("50000.00"), po_status="OPEN")
    
    recon = recon_service.reconcile(extracted, po_match)
    assert recon.within_tolerance is False
    assert recon.variance_amount == Decimal("7000.00")
    assert recon.variance_pct == Decimal("14.00")

def test_decision_precedence_duplicate_rejection():
    engine = DecisionEngine()
    extracted = ExtractedInvoiceData(invoice_number="INV-1", invoice_date="2024-10-01", vendor_name="TechCorp", invoice_total=Decimal("1000"))
    vendor = VendorValidationResult(is_verified=True, vendor_id="VEND-001", legal_name="TechCorp", is_approved=True, status="ACTIVE")
    duplicate = DuplicateDetectionResult(is_duplicate=True, prior_run_id="RUN-OLD-1", prior_invoice_id="INV-1", prior_submission_date="2024-09-01", notes="Duplicate")
    po_match = POMatchingResult(is_matched=True, po_number="PO-1", po_total=Decimal("1000"), po_status="OPEN")
    recon = ReconciliationResult(invoice_total=Decimal("1000"), po_applicable_amount=Decimal("1000"), within_tolerance=True)

    result = engine.evaluate(extracted, vendor, duplicate, po_match, recon)
    assert result.decision == DecisionOutcome.REJECTED
    assert result.reason_code == "DUPLICATE_INVOICE_SUBMISSION"
    assert "duplicate" in result.explanation.lower()

def test_decision_precedence_unapproved_vendor():
    engine = DecisionEngine()
    extracted = ExtractedInvoiceData(invoice_number="INV-1", invoice_date="2024-10-01", vendor_name="Quantum", invoice_total=Decimal("1000"))
    vendor = VendorValidationResult(is_verified=True, vendor_id="VEND-004", legal_name="Quantum Office", is_approved=False, status="INACTIVE")
    duplicate = DuplicateDetectionResult(is_duplicate=False)
    po_match = POMatchingResult(is_matched=True, po_number="PO-1", po_total=Decimal("1000"), po_status="OPEN")
    recon = ReconciliationResult(invoice_total=Decimal("1000"), po_applicable_amount=Decimal("1000"), within_tolerance=True)

    result = engine.evaluate(extracted, vendor, duplicate, po_match, recon)
    assert result.decision == DecisionOutcome.REJECTED
    assert result.reason_code in ("INACTIVE_VENDOR", "UNAPPROVED_VENDOR")

def test_decision_amount_mismatch_pending_review():
    engine = DecisionEngine()
    extracted = ExtractedInvoiceData(invoice_number="INV-55", invoice_date="2024-10-05", vendor_name="Apex Cloud", invoice_total=Decimal("57000"))
    vendor = VendorValidationResult(is_verified=True, vendor_id="VEND-002", legal_name="Apex Cloud", is_approved=True, status="ACTIVE")
    duplicate = DuplicateDetectionResult(is_duplicate=False)
    po_match = POMatchingResult(is_matched=True, po_number="PO-2024-002", po_total=Decimal("50000"), po_status="OPEN")
    recon = ReconciliationResult(
        invoice_total=Decimal("57000"),
        po_applicable_amount=Decimal("50000"),
        variance_amount=Decimal("7000"),
        variance_pct=Decimal("14.0"),
        tolerance_threshold_amount=Decimal("500"),
        within_tolerance=False
    )

    result = engine.evaluate(extracted, vendor, duplicate, po_match, recon)
    assert result.decision == DecisionOutcome.PENDING_REVIEW
    assert result.reason_code == "FINANCIAL_VARIANCE_EXCEEDS_TOLERANCE"
    assert "7,000" in result.explanation
    assert "14%" in result.explanation
