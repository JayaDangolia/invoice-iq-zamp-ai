from typing import Optional
from core.models import DuplicateDetectionResult
from database.repository import InvoiceRepository

class DuplicateDetectionService:
    def __init__(self, repository: Optional[InvoiceRepository] = None):
        self.repository = repository or InvoiceRepository()

    def check_duplicate(
        self,
        file_hash: str,
        vendor_id: Optional[str],
        invoice_number: Optional[str],
        current_run_id: Optional[str] = None
    ) -> DuplicateDetectionResult:
        """
        Check whether an invoice is a duplicate of a previously recorded run.
        Detects both identical file hashes (content-level match) and
        Vendor ID + Normalized Invoice Number matches (business-level match, e.g. renamed files).
        """
        candidate = self.repository.find_duplicate_candidate(
            file_hash=file_hash,
            vendor_id=vendor_id,
            invoice_number=invoice_number
        )

        if not candidate:
            return DuplicateDetectionResult(
                is_duplicate=False,
                is_uncertain=False,
                match_type="NONE",
                notes="No prior matching invoice found in history."
            )

        # Ensure we are not matching the same active run_id if re-evaluating
        if current_run_id and candidate.get("run_id") == current_run_id:
            return DuplicateDetectionResult(
                is_duplicate=False,
                is_uncertain=False,
                match_type="NONE",
                notes="Self-reference ignored."
            )

        match_reason = candidate.get("_duplicate_match_reason", "")
        prior_run_id = candidate.get("run_id")
        prior_inv_num = candidate.get("invoice_number")
        prior_date = candidate.get("created_at")

        if match_reason == "EXACT_FILE_HASH":
            return DuplicateDetectionResult(
                is_duplicate=True,
                is_uncertain=False,
                match_type="HASH_MATCH",
                prior_invoice_id=prior_inv_num,
                prior_run_id=prior_run_id,
                prior_submission_date=prior_date,
                confidence=1.0,
                notes=(
                    f"Identical PDF file content previously processed in Run [{prior_run_id}] "
                    f"(Invoice #{prior_inv_num}) on {prior_date}."
                )
            )

        if match_reason == "VENDOR_AND_INVOICE_NUMBER":
            return DuplicateDetectionResult(
                is_duplicate=True,
                is_uncertain=False,
                match_type="EXACT_MATCH",
                prior_invoice_id=prior_inv_num,
                prior_run_id=prior_run_id,
                prior_submission_date=prior_date,
                confidence=1.0,
                notes=(
                    f"Invoice #{prior_inv_num} for Vendor [{vendor_id}] was previously processed "
                    f"in Run [{prior_run_id}] on {prior_date}. Duplicate submission detected."
                )
            )

        return DuplicateDetectionResult(
            is_duplicate=False,
            is_uncertain=False,
            match_type="NONE",
            notes="No duplicate found."
        )
