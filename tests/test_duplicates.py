import pytest
import uuid
from services.duplicate_service import DuplicateDetectionService
from database.repository import InvoiceRepository
from database.db import init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_duplicate_detection_hash_and_invoice_number():
    repo = InvoiceRepository()
    dup_service = DuplicateDetectionService(repo)

    unique_hash = uuid.uuid4().hex
    unique_inv = f"INV-TEST-{uuid.uuid4().hex[:6].upper()}"
    vendor_id = "VEND-001"
    run_id_1 = f"RUN-{uuid.uuid4().hex[:8].upper()}"

    # First check: should be clean
    res1 = dup_service.check_duplicate(
        file_hash=unique_hash,
        vendor_id=vendor_id,
        invoice_number=unique_inv
    )
    assert res1.is_duplicate is False

    # Simulate saving first run
    repo.save_run({
        "run_id": run_id_1,
        "filename": "invoice_original.pdf",
        "file_hash": unique_hash,
        "invoice_number": unique_inv,
        "vendor_id": vendor_id,
        "vendor_name": "TechCorp Solutions",
        "invoice_total": 50000.0,
        "decision": "APPROVED",
        "status": "COMPLETED"
    })

    # Second check with identical hash (even with different filename)
    res2 = dup_service.check_duplicate(
        file_hash=unique_hash,
        vendor_id=vendor_id,
        invoice_number=unique_inv
    )
    assert res2.is_duplicate is True
    assert res2.match_type == "HASH_MATCH"
    assert res2.prior_run_id == run_id_1

    # Third check with different hash but same vendor + invoice_number (renamed duplicate)
    different_hash = uuid.uuid4().hex
    res3 = dup_service.check_duplicate(
        file_hash=different_hash,
        vendor_id=vendor_id,
        invoice_number=unique_inv
    )
    assert res3.is_duplicate is True
    assert res3.match_type == "EXACT_MATCH"
    assert res3.prior_run_id == run_id_1
