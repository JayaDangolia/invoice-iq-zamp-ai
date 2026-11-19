from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from config.settings import RULES
from core.models import (
    DecisionOutcome,
    DecisionResult,
    ExtractedInvoiceData,
    VendorValidationResult,
    DuplicateDetectionResult,
    POMatchingResult,
    ReconciliationResult,
)
from services.explanation_service import ExplanationService

class DecisionEngine:
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or RULES
        self.mandatory_fields = self.rules.get("mandatory_fields", [
            "invoice_number", "invoice_date", "vendor_name", "invoice_total"
        ])

    def evaluate(
        self,
        extracted: ExtractedInvoiceData,
        vendor: VendorValidationResult,
        duplicate: DuplicateDetectionResult,
        po_match: POMatchingResult,
        recon: ReconciliationResult
    ) -> DecisionResult:
        """
        Evaluate full invoice reconciliation and generate deterministic decision
        adhering strictly to AP precedence rules.
        """
        passed_checks: List[str] = []
        failed_checks: List[str] = []
        warnings: List[str] = []

        now_iso = datetime.now(timezone.utc).isoformat()

        # -------------------------------------------------------------
        # PRECEDENCE 1: DUPLICATE DETECTION (Hard rejection)
        # -------------------------------------------------------------
        if duplicate.is_duplicate:
            failed_checks.append(f"Duplicate Detection: {duplicate.notes}")
            reason_code = "DUPLICATE_INVOICE_SUBMISSION"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.REJECTED, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.REJECTED,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Reject invoice submission and notify vendor of duplicate entry.",
                decision_timestamp=now_iso
            )
        else:
            passed_checks.append("Duplicate Check: No duplicate found in system records.")

        # -------------------------------------------------------------
        # PRECEDENCE 2: VENDOR VALIDATION
        # -------------------------------------------------------------
        if not vendor.is_verified:
            failed_checks.append(f"Vendor Verification: {vendor.notes}")
            reason_code = "VENDOR_NOT_FOUND"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Verify vendor onboarding status or request W-9 / GST registration.",
                decision_timestamp=now_iso
            )
        elif not vendor.is_approved:
            # Confirmed unapproved / inactive vendor is REJECTED
            failed_checks.append(f"Vendor Approval: Vendor [{vendor.vendor_id}] is {vendor.status} (Unapproved)")
            reason_code = "INACTIVE_VENDOR" if vendor.status == "INACTIVE" else "UNAPPROVED_VENDOR"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.REJECTED, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.REJECTED,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Reject invoice. Inform procurement that vendor is inactive/unapproved.",
                decision_timestamp=now_iso
            )
        else:
            passed_checks.append(f"Vendor Verification: Approved active vendor [{vendor.vendor_id} - {vendor.legal_name}] confirmed.")

        # -------------------------------------------------------------
        # PRECEDENCE 3: MANDATORY FIELD PRESENCE
        # -------------------------------------------------------------
        missing_fields = []
        if not extracted.invoice_number:
            missing_fields.append("invoice_number")
        if not extracted.invoice_date:
            missing_fields.append("invoice_date")
        if not extracted.vendor_name:
            missing_fields.append("vendor_name")
        if extracted.invoice_total is None:
            missing_fields.append("invoice_total")

        if missing_fields:
            failed_checks.append(f"Mandatory Fields: Missing {', '.join(missing_fields)}")
            reason_code = "MISSING_MANDATORY_FIELDS"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Review physical document to manually record missing required fields.",
                decision_timestamp=now_iso
            )
        else:
            passed_checks.append("Mandatory Fields: All required metadata fields are populated.")

        # -------------------------------------------------------------
        # PRECEDENCE 4: OCR CONFIDENCE & QUALITY
        # -------------------------------------------------------------
        if extracted.ocr_applied:
            # Check if critical fields had degraded confidence
            has_low_conf = False
            for k, ev in extracted.extraction_evidence.items():
                if isinstance(ev, dict) and ev.get("confidence", 1.0) < 0.70:
                    has_low_conf = True
                    break
            if has_low_conf:
                warnings.append("Document was scanned; low OCR confidence detected on critical fields.")
                failed_checks.append("OCR Confidence: Degraded character recognition on scanned document.")
                reason_code = "OCR_LOW_CONFIDENCE"
                explanation = ExplanationService.generate_explanation(
                    DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
                )
                return DecisionResult(
                    decision=DecisionOutcome.PENDING_REVIEW,
                    reason_code=reason_code,
                    explanation=explanation,
                    passed_checks=passed_checks,
                    failed_checks=failed_checks,
                    warnings=warnings,
                    recommended_action="Visually inspect scanned invoice image to confirm figures.",
                    decision_timestamp=now_iso
                )
            else:
                passed_checks.append("OCR Extraction: Character recognition completed with acceptable confidence.")

        # -------------------------------------------------------------
        # PRECEDENCE 5: PO MATCHING & STATUS
        # -------------------------------------------------------------
        if not po_match.is_matched:
            failed_checks.append(f"PO Matching: {po_match.notes}")
            reason_code = "PO_AMBIGUOUS_OR_MISSING"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Assign valid Purchase Order reference or route to purchasing manager.",
                decision_timestamp=now_iso
            )
        else:
            if po_match.match_type == "FALLBACK_CANDIDATE":
                warnings.append(f"PO inferred via fallback: {po_match.po_number}")
            passed_checks.append(f"PO Matching: Matched Purchase Order [{po_match.po_number}].")

        # PO Status check
        if po_match.po_status in ("CLOSED", "CANCELLED"):
            failed_checks.append(f"PO Status: Matched PO is {po_match.po_status}")
            reason_code = "PO_CLOSED_OR_EXHAUSTED"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Obtain PO change order or reopen PO before releasing payment.",
                decision_timestamp=now_iso
            )
        else:
            passed_checks.append(f"PO Status: Active and open ({po_match.po_status}).")

        # -------------------------------------------------------------
        # PRECEDENCE 6: FINANCIAL RECONCILIATION & TOLERANCES
        # -------------------------------------------------------------
        if not recon.is_arithmetic_consistent:
            failed_checks.append(f"Arithmetic Verification: {recon.notes}")
            reason_code = "ARITHMETIC_INCONSISTENCY"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Check tax and subtotal arithmetic with vendor.",
                decision_timestamp=now_iso
            )
        else:
            passed_checks.append("Arithmetic Verification: Subtotal, tax, and total are mathematically consistent.")

        if recon.exceeds_remaining_balance:
            failed_checks.append(
                f"PO Balance: Invoice amount ₹{recon.invoice_total:,.2f} exceeds available remaining PO balance "
                f"of ₹{recon.remaining_balance_before:,.2f} on PO [{po_match.po_number}]."
            )
            reason_code = "EXCEEDS_REMAINING_PO_BALANCE"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Request PO balance increase / change order from procurement or partial credit memo from vendor.",
                decision_timestamp=now_iso
            )

        if not recon.within_tolerance:
            failed_checks.append(
                f"Financial Reconciliation: Variance ₹{abs(recon.variance_amount):,.2f} "
                f"({abs(recon.variance_pct)}%) exceeds allowable tolerance of ₹{recon.tolerance_threshold_amount:,.2f}."
            )
            reason_code = "FINANCIAL_VARIANCE_EXCEEDS_TOLERANCE"
            explanation = ExplanationService.generate_explanation(
                DecisionOutcome.PENDING_REVIEW, reason_code, extracted, vendor, duplicate, po_match, recon
            )
            return DecisionResult(
                decision=DecisionOutcome.PENDING_REVIEW,
                reason_code=reason_code,
                explanation=explanation,
                passed_checks=passed_checks,
                failed_checks=failed_checks,
                warnings=warnings,
                recommended_action="Review price variance with procurement and request vendor credit note if required.",
                decision_timestamp=now_iso
            )
        else:
            if recon.is_partial_invoice:
                passed_checks.append(
                    f"Partial PO Billing: Invoice ₹{recon.invoice_total:,.2f} is within available PO balance "
                    f"of ₹{recon.remaining_balance_before:,.2f} (Projected remaining balance: ₹{recon.remaining_balance_after:,.2f})."
                )
            else:
                passed_checks.append(
                    f"Financial Reconciliation: Invoice total (₹{recon.invoice_total:,.2f}) matches PO "
                    f"within allowed tolerance (Variance: ₹{recon.variance_amount:,.2f})."
                )

        # -------------------------------------------------------------
        # PRECEDENCE 7: ALL CHECKS PASSED -> APPROVED
        # -------------------------------------------------------------
        reason_code = "VALIDATION_PASSED_CLEAN"
        explanation = ExplanationService.generate_explanation(
            DecisionOutcome.APPROVED, reason_code, extracted, vendor, duplicate, po_match, recon
        )
        return DecisionResult(
            decision=DecisionOutcome.APPROVED,
            reason_code=reason_code,
            explanation=explanation,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            recommended_action="Invoice ready for automated voucher posting and scheduled payment release.",
            decision_timestamp=now_iso
        )
