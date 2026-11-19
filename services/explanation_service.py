from decimal import Decimal
from typing import List
from core.models import (
    DecisionOutcome,
    ExtractedInvoiceData,
    VendorValidationResult,
    DuplicateDetectionResult,
    POMatchingResult,
    ReconciliationResult
)

class ExplanationService:
    @staticmethod
    def generate_explanation(
        decision: DecisionOutcome,
        reason_code: str,
        extracted: ExtractedInvoiceData,
        vendor: VendorValidationResult,
        duplicate: DuplicateDetectionResult,
        po_match: POMatchingResult,
        recon: ReconciliationResult
    ) -> str:
        """
        Generate human-readable, factual explanation directly from validation results.
        Never contradicts actual rule evaluations.
        """
        if decision == DecisionOutcome.REJECTED:
            if reason_code == "DUPLICATE_INVOICE_SUBMISSION":
                return (
                    f"The invoice has been REJECTED because it is a confirmed duplicate of prior "
                    f"Run [{duplicate.prior_run_id}] (Invoice #{duplicate.prior_invoice_id}) submitted on "
                    f"{duplicate.prior_submission_date}. Reason: {duplicate.notes}"
                )
            elif reason_code in ("UNAPPROVED_VENDOR", "INACTIVE_VENDOR"):
                return (
                    f"The invoice has been REJECTED because the identified vendor '{vendor.legal_name or 'N/A'}' "
                    f"has an authorization status of '{vendor.status}' with approved_flag=False in the Vendor Master. "
                    f"AP policy prohibits processing invoices from unapproved or inactive vendors."
                )
            else:
                return f"The invoice has been REJECTED in accordance with AP policy. Reason: {reason_code}."

        elif decision == DecisionOutcome.PENDING_REVIEW:
            reasons = []
            if reason_code == "FINANCIAL_VARIANCE_EXCEEDS_TOLERANCE":
                var_amt = abs(recon.variance_amount)
                var_pct = abs(recon.variance_pct)
                tol_amt = recon.tolerance_threshold_amount
                pct_str = f"{int(var_pct)}%" if var_pct == int(var_pct) else f"{var_pct}%"
                return (
                    f"The invoice has been placed under review because its total (₹{recon.invoice_total:,.2f}) "
                    f"exceeds the applicable PO amount (₹{recon.po_applicable_amount:,.2f}) by ₹{var_amt:,.2f} ({pct_str}). "
                    f"This exceeds the configured tolerance threshold of ₹{tol_amt:,.2f} (2% capped at ₹500). "
                    f"Vendor verification and duplicate checks passed. AP reviewer approval is required before further processing."
                )
            if reason_code == "MISSING_MANDATORY_FIELDS":
                missing = []
                if not extracted.invoice_number:
                    missing.append("Invoice Number")
                if not extracted.invoice_date:
                    missing.append("Invoice Date")
                if not extracted.vendor_name:
                    missing.append("Vendor Name")
                if not extracted.invoice_total:
                    missing.append("Invoice Total")
                return (
                    f"The invoice has been placed under review due to missing mandatory field(s): {', '.join(missing)}. "
                    f"Automated approval cannot proceed without complete invoice metadata. Reviewer verification required."
                )
            if reason_code == "OCR_LOW_CONFIDENCE":
                return (
                    f"The invoice was processed via OCR fallback with low extraction confidence. "
                    f"Document text contains scan noise or degraded characters. Manual inspection of the original document "
                    f"is required to confirm extracted amounts and line items."
                )
            if reason_code == "PO_AMBIGUOUS_OR_MISSING":
                if po_match.match_type == "AMBIGUOUS":
                    return (
                        f"The invoice is missing a PO reference. Controlled fallback matching identified "
                        f"{po_match.candidate_po_count} potential open purchase orders ({', '.join(po_match.candidate_pos)}). "
                        f"Human reviewer assignment to a specific PO is required."
                    )
                return (
                    f"The invoice could not be matched to an active purchase order. "
                    f"No matching PO reference was found for vendor '{vendor.legal_name or 'N/A'}'. AP review required."
                )
            if reason_code == "PO_CLOSED_OR_EXHAUSTED":
                return (
                    f"Matched purchase order [{po_match.po_number}] is {po_match.po_status} with a remaining "
                    f"balance of ₹{po_match.remaining_balance or Decimal(0):,.2f}. Reviewer authorization required."
                )
            if reason_code == "EXCEEDS_REMAINING_PO_BALANCE":
                return (
                    f"The invoice has been placed under review because its total (₹{recon.invoice_total:,.2f}) "
                    f"exceeds the available remaining PO balance (₹{recon.remaining_balance_before:,.2f}) "
                    f"on PO [{po_match.po_number}]. Prior accepted invoices have consumed ₹{recon.prior_billed_amount:,.2f} "
                    f"of the initial ₹{po_match.po_total:,.2f} commitment. Procurement authorization or PO balance supplement required."
                )
            if reason_code == "ARITHMETIC_INCONSISTENCY":
                return (
                    f"The invoice exhibits an internal arithmetic inconsistency: Subtotal ({extracted.subtotal}) + "
                    f"Tax ({extracted.tax}) does not equal the stated Invoice Total ({extracted.invoice_total}). "
                    f"AP verification required."
                )
            return f"The invoice has been flagged for human review. Reason: {reason_code}."

        else:  # APPROVED
            if recon.is_partial_invoice:
                return (
                    f"The invoice passed all automated verification and partial PO reconciliation checks cleanly. "
                    f"Vendor '{vendor.legal_name}' is verified and active. No duplicate was detected. "
                    f"Partial billing of ₹{recon.invoice_total:,.2f} is within available PO balance "
                    f"of ₹{recon.remaining_balance_before:,.2f} on PO [{po_match.po_number}]. "
                    f"Remaining balance after voucher posting: ₹{recon.remaining_balance_after:,.2f}."
                )
            return (
                f"The invoice passed all automated verification and financial reconciliation checks cleanly. "
                f"Vendor '{vendor.legal_name}' is verified and active. No duplicate was detected. "
                f"Matched PO [{po_match.po_number}] is OPEN with sufficient remaining balance. "
                f"Invoice total of ₹{recon.invoice_total:,.2f} is within configured financial tolerance."
            )
