import pytest
from decimal import Decimal
from services.po_matching_service import POMatchingService
from core.models import LineItem

@pytest.fixture
def po_service():
    return POMatchingService()

def test_exact_po_matching(po_service):
    res = po_service.match_po(
        extracted_po_number="PO-2024-001",
        verified_vendor_id="VEND-001",
        invoice_total=Decimal("125000.00"),
        line_items=[
            LineItem(description="Enterprise Cloud Server Hosting Annual Tier-1", quantity=Decimal(1), unit_price=Decimal(100000), line_total=Decimal(100000))
        ]
    )
    assert res.is_matched is True
    assert res.po_number == "PO-2024-001"
    assert res.po_status == "OPEN"
    assert res.po_total == Decimal("125000.00")
    assert len(res.line_matches) > 0

def test_po_vendor_mismatch(po_service):
    # PO-2024-001 belongs to VEND-001, pass VEND-002
    res = po_service.match_po(
        extracted_po_number="PO-2024-001",
        verified_vendor_id="VEND-002"
    )
    assert res.is_matched is False
    assert res.match_type == "VENDOR_MISMATCH"

def test_missing_po_controlled_fallback(po_service):
    # VEND-005 only has PO-2024-005 in OPEN status for ₹62,000
    res = po_service.match_po(
        extracted_po_number=None,
        verified_vendor_id="VEND-005",
        invoice_total=Decimal("62000.00")
    )
    assert res.is_matched is True
    assert res.po_number == "PO-2024-005"
    assert res.match_type == "FALLBACK_CANDIDATE"

def test_ambiguous_po_multiple_candidates(po_service):
    # VEND-001 has multiple OPEN POs (PO-2024-001, PO-2024-004, PO-2024-009)
    # When no PO is provided on the invoice, matching must NOT guess.
    res = po_service.match_po(
        extracted_po_number=None,
        verified_vendor_id="VEND-001",
        invoice_total=Decimal("50000.00")
    )
    assert res.is_matched is False
    assert res.match_type == "AMBIGUOUS"
    assert res.candidate_po_count >= 2
    assert "PO-2024-001" in res.candidate_pos
    assert len(res.candidate_po_details) >= 2

