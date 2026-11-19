import pytest
from services.vendor_service import VendorService

@pytest.fixture
def vendor_service():
    return VendorService()

def test_verify_vendor_by_tax_id(vendor_service):
    res = vendor_service.verify_vendor(
        extracted_name="Any Name Here",
        extracted_tax_id="27AABCT1234A1Z5"
    )
    assert res.is_verified is True
    assert res.vendor_id == "VEND-001"
    assert res.is_approved is True
    assert res.match_type == "EXACT_TAX_ID"

def test_verify_vendor_by_normalized_name(vendor_service):
    res = vendor_service.verify_vendor(
        extracted_name="Apex Cloud Infrastructure LLC"
    )
    assert res.is_verified is True
    assert res.vendor_id == "VEND-002"
    assert res.is_approved is True
    assert res.match_type in ("EXACT_NAME", "FUZZY_NAME")

def test_unapproved_or_inactive_vendor(vendor_service):
    res = vendor_service.verify_vendor(
        extracted_name="Quantum Office Supplies Private Limited",
        extracted_tax_id="33AAACQ4321D1Z9"
    )
    assert res.is_verified is True
    assert res.vendor_id == "VEND-004"
    assert res.status == "INACTIVE"
    assert res.is_approved is False

def test_unmatched_vendor(vendor_service):
    res = vendor_service.verify_vendor(
        extracted_name="Unknown Freelance Consultant Corp",
        extracted_tax_id="99XXXXX0000X0Z0"
    )
    assert res.is_verified is False
    assert res.vendor_id is None
    assert res.is_approved is False
