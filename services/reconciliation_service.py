from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional
from config.settings import RULES
from core.models import ExtractedInvoiceData, POMatchingResult, ReconciliationResult

class ReconciliationService:
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or RULES
        tolerances = self.rules.get("tolerances", {})
        self.amount_tol_pct = Decimal(str(tolerances.get("amount_tolerance_percentage", 0.02)))
        self.amount_tol_cap = Decimal(str(tolerances.get("amount_tolerance_cap", 500.0)))
        self.tax_tol_pct = Decimal(str(tolerances.get("tax_tolerance_percentage", 0.01)))
        self.tax_tol_cap = Decimal(str(tolerances.get("tax_tolerance_cap", 100.0)))

    def reconcile(
        self,
        extracted: ExtractedInvoiceData,
        po_match: POMatchingResult
    ) -> ReconciliationResult:
        """
        Perform financial reconciliation between extracted invoice amounts and matched PO.
        Enforces decimal precision, supports partial invoicing against open PO balances,
        and evaluates configurable financial tolerance boundaries.
        """
        inv_total = extracted.invoice_total or Decimal("0.00")
        notes = []

        # 1. Arithmetic Consistency (Embedded vs Separate Tax)
        is_consistent = True
        subtotal = extracted.subtotal or Decimal("0.00")
        tax = extracted.tax or Decimal("0.00")
        is_tax_embedded = getattr(extracted, "is_tax_embedded", False)

        if is_tax_embedded:
            # Embedded tax: base + tax = total
            base = extracted.base_amount or (inv_total - tax)
            summed = base + tax
            diff = abs(summed - inv_total)
            if diff > Decimal("1.00"):
                is_consistent = False
                notes.append(
                    f"Embedded tax discrepancy: Base amount ({base}) + Embedded Tax ({tax}) = "
                    f"{summed}, but declared total is {inv_total} (difference: {diff})."
                )
        else:
            # Separate tax: subtotal + tax = total
            if extracted.subtotal is not None and extracted.tax is not None and extracted.invoice_total is not None:
                summed = subtotal + tax
                diff = abs(summed - inv_total)
                if diff > Decimal("1.00"):
                    is_consistent = False
                    notes.append(
                        f"Arithmetic mismatch: Subtotal ({subtotal}) + Tax ({tax}) = "
                        f"{summed}, but declared total is {inv_total} (difference: {diff})."
                    )

        # 2. PO Financial Comparison
        if not po_match.is_matched or not po_match.po_total:
            return ReconciliationResult(
                invoice_total=inv_total,
                po_applicable_amount=Decimal("0.00"),
                variance_amount=inv_total,
                variance_pct=Decimal("0.00"),
                tolerance_threshold_amount=Decimal("0.00"),
                within_tolerance=False,
                tax_variance=Decimal("0.00"),
                is_partial_invoice=False,
                prior_billed_amount=Decimal("0.00"),
                remaining_balance_before=Decimal("0.00"),
                remaining_balance_after=Decimal("0.00"),
                exceeds_remaining_balance=False,
                is_tax_embedded=is_tax_embedded,
                quantity_discrepancies=[],
                line_item_discrepancies=[],
                calculated_subtotal=subtotal,
                calculated_tax=tax,
                is_arithmetic_consistent=is_consistent,
                notes=" ".join(notes).strip() or "No matched Purchase Order available for financial comparison."
            )

        po_tot = po_match.po_total
        rem_before = po_match.dynamic_remaining_balance if po_match.dynamic_remaining_balance is not None else po_tot
        prior_billed = po_match.cumulative_billed_amount or Decimal("0.00")
        is_partial = po_match.is_partial_invoice or (prior_billed > Decimal("0.00")) or (inv_total < po_tot)

        # Standard tolerance threshold
        computed_tolerance = po_tot * self.amount_tol_pct
        tolerance_threshold = min(computed_tolerance, self.amount_tol_cap).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        exceeds_remaining = False

        if is_partial:
            # Partial Invoice Reconciliation
            if inv_total <= rem_before:
                # Valid partial billing within available balance
                within_tolerance = True
                rem_after = (rem_before - inv_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                variance_amount = (inv_total - rem_before).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                variance_pct = ((inv_total / po_tot) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                notes.append(
                    f"Partial billing verified: Invoice ₹{inv_total:,.2f} is within available PO balance "
                    f"of ₹{rem_before:,.2f} (Cumulative billed: ₹{(prior_billed + inv_total):,.2f} / ₹{po_tot:,.2f}, "
                    f"Remaining balance after voucher posting: ₹{rem_after:,.2f})."
                )
            else:
                # Invoice amount exceeds remaining PO balance
                excess_amount = inv_total - rem_before
                if excess_amount <= tolerance_threshold:
                    within_tolerance = True
                    rem_after = Decimal("0.00")
                    variance_amount = excess_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    variance_pct = ((variance_amount / po_tot) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    notes.append(
                        f"Partial invoice ₹{inv_total:,.2f} slightly exceeds balance ₹{rem_before:,.2f} "
                        f"by ₹{excess_amount:,.2f}, within allowable tolerance threshold of ₹{tolerance_threshold:,.2f}."
                    )
                else:
                    within_tolerance = False
                    exceeds_remaining = True
                    rem_after = rem_before
                    variance_amount = excess_amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    variance_pct = ((variance_amount / po_tot) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    notes.append(
                        f"Invoice total ₹{inv_total:,.2f} exceeds available remaining PO balance of ₹{rem_before:,.2f} "
                        f"(Excess: ₹{excess_amount:,.2f}, allowable tolerance: ₹{tolerance_threshold:,.2f})."
                    )
        else:
            # Full Single PO Reconciliation
            variance_amount = (inv_total - po_tot).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            variance_pct = ((variance_amount / po_tot) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if po_tot > 0 else Decimal("0.00")
            within_tolerance = abs(variance_amount) <= tolerance_threshold
            rem_after = Decimal("0.00") if within_tolerance else rem_before

            if not within_tolerance:
                notes.append(
                    f"Financial variance ₹{abs(variance_amount):,.2f} ({abs(variance_pct)}%) exceeds "
                    f"allowable tolerance limit of ₹{tolerance_threshold:,.2f} on PO [{po_match.po_number}]."
                )
            else:
                notes.append(
                    f"Invoice total ₹{inv_total:,.2f} matches full PO commitment ₹{po_tot:,.2f} "
                    f"within tolerance (Variance: ₹{variance_amount:,.2f})."
                )

        # 3. Line item discrepancies
        qty_discrepancies = []
        for line in po_match.line_matches:
            if line.get("qty_variance", 0) != 0:
                qty_discrepancies.append({
                    "item": line.get("invoice_description"),
                    "invoice_qty": line.get("invoice_qty"),
                    "po_qty": line.get("po_qty"),
                    "diff": line.get("qty_variance")
                })

        return ReconciliationResult(
            invoice_total=inv_total,
            po_applicable_amount=po_tot,
            variance_amount=variance_amount,
            variance_pct=variance_pct,
            tolerance_threshold_amount=tolerance_threshold,
            within_tolerance=within_tolerance,
            tax_variance=Decimal("0.00"),
            is_partial_invoice=is_partial,
            prior_billed_amount=prior_billed,
            remaining_balance_before=rem_before,
            remaining_balance_after=rem_after,
            exceeds_remaining_balance=exceeds_remaining,
            is_tax_embedded=is_tax_embedded,
            quantity_discrepancies=qty_discrepancies,
            line_item_discrepancies=po_match.line_matches,
            calculated_subtotal=subtotal,
            calculated_tax=tax,
            is_arithmetic_consistent=is_consistent,
            notes=" ".join(notes).strip()
        )
