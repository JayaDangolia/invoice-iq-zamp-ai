from decimal import Decimal
from typing import Any, Dict, List, Optional
import pandas as pd
from config.settings import PURCHASE_ORDERS_CSV, PO_LINE_ITEMS_CSV
from core.models import LineItem, POMatchingResult

class POMatchingService:
    def __init__(
        self,
        po_csv_path: Optional[str] = None,
        line_items_csv_path: Optional[str] = None,
        repository: Optional[Any] = None
    ):
        self.po_csv = po_csv_path or str(PURCHASE_ORDERS_CSV)
        self.line_items_csv = line_items_csv_path or str(PO_LINE_ITEMS_CSV)
        self.repository = repository
        self.pos_df = self._load_pos()
        self.lines_df = self._load_lines()

    def _load_pos(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.po_csv)
        except Exception:
            return pd.DataFrame()

    def _load_lines(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.line_items_csv)
        except Exception:
            return pd.DataFrame()

    def match_po(
        self,
        extracted_po_number: Optional[str],
        verified_vendor_id: Optional[str],
        invoice_total: Optional[Decimal] = None,
        line_items: Optional[List[LineItem]] = None,
        currency: str = "INR"
    ) -> POMatchingResult:
        """
        Execute PO matching workflow:
        1. Exact PO Number Match
        2. Dynamic cumulative balance reconciliation (from SQLite repo)
        3. Vendor validation against PO owner
        4. PO status and remaining capacity check
        5. Controlled Fallback / Ambiguity detection when PO is missing
        """
        if self.pos_df.empty:
            return POMatchingResult(
                is_matched=False,
                match_type="NONE",
                notes="Purchase order master database is unavailable or empty."
            )

        # 1. Exact PO Number Check
        if extracted_po_number:
            clean_po = extracted_po_number.strip().upper()
            match_row = self.pos_df[self.pos_df["po_number"].str.upper() == clean_po]
            
            if not match_row.empty:
                row = match_row.iloc[0]
                po_num = str(row["po_number"])
                po_vend = str(row["vendor_id"])
                po_stat = str(row["po_status"]).upper()
                po_tot = Decimal(str(row["po_total"]))
                po_curr = str(row.get("currency", "INR"))

                # Query dynamic cumulative billed amount and accepted invoices from repository
                if self.repository is not None:
                    cum_billed = self.repository.get_cumulative_billed_for_po(po_num)
                    prior_invoices = self.repository.get_accepted_invoices_for_po(po_num)
                    dyn_remaining = max(po_tot - cum_billed, Decimal("0.00"))
                else:
                    cum_billed = Decimal("0.00")
                    prior_invoices = []
                    dyn_remaining = Decimal(str(row["remaining_balance"]))

                # Determine if this constitutes partial invoicing
                is_partial = (
                    (invoice_total is not None and invoice_total < po_tot) or
                    (cum_billed > Decimal("0.00"))
                )

                notes = f"Exact PO reference matched: {po_num}."
                if is_partial:
                    notes += (
                        f" Cumulative tracking: Prior billed ₹{cum_billed:,.2f} "
                        f"across {len(prior_invoices)} accepted invoice(s). "
                        f"Dynamic remaining PO balance: ₹{dyn_remaining:,.2f}."
                    )

                # Verify vendor match
                if verified_vendor_id and po_vend != verified_vendor_id:
                    notes += f" WARNING: PO belongs to {po_vend}, but invoice vendor is {verified_vendor_id}."
                    return POMatchingResult(
                        is_matched=False,
                        po_number=po_num,
                        po_vendor_id=po_vend,
                        po_status=po_stat,
                        po_total=po_tot,
                        initial_po_total=po_tot,
                        cumulative_billed_amount=cum_billed,
                        dynamic_remaining_balance=dyn_remaining,
                        remaining_balance=dyn_remaining,
                        prior_accepted_invoices=prior_invoices,
                        is_partial_invoice=is_partial,
                        currency=po_curr,
                        match_type="VENDOR_MISMATCH",
                        match_confidence=0.0,
                        notes=notes
                    )

                # Line items comparison
                line_matches = self._match_line_items(po_num, line_items or [])

                return POMatchingResult(
                    is_matched=True,
                    po_number=po_num,
                    po_vendor_id=po_vend,
                    po_status=po_stat,
                    po_total=po_tot,
                    initial_po_total=po_tot,
                    cumulative_billed_amount=cum_billed,
                    dynamic_remaining_balance=dyn_remaining,
                    remaining_balance=dyn_remaining,
                    prior_accepted_invoices=prior_invoices,
                    is_partial_invoice=is_partial,
                    currency=po_curr,
                    match_type="EXACT_PO_REF",
                    match_confidence=1.0,
                    notes=notes,
                    line_matches=line_matches
                )

        # 2. Controlled Fallback Matching when PO reference is missing
        if verified_vendor_id:
            vendor_pos = self.pos_df[
                (self.pos_df["vendor_id"] == verified_vendor_id) &
                (self.pos_df["po_status"] == "OPEN")
            ]

            if vendor_pos.empty:
                return POMatchingResult(
                    is_matched=False,
                    match_type="NONE",
                    notes=f"PO reference missing, and no OPEN purchase orders exist for vendor {verified_vendor_id}."
                )

            # Build candidate PO details
            candidate_details = []
            for _, crow in vendor_pos.iterrows():
                c_num = str(crow["po_number"])
                c_tot = Decimal(str(crow["po_total"]))
                c_billed = self.repository.get_cumulative_billed_for_po(c_num) if self.repository else Decimal("0.00")
                c_rem = max(c_tot - c_billed, Decimal("0.00"))
                candidate_details.append({
                    "po_number": c_num,
                    "vendor_id": str(crow["vendor_id"]),
                    "po_date": str(crow.get("po_date", "")),
                    "po_total": float(c_tot),
                    "cumulative_billed": float(c_billed),
                    "remaining_balance": float(c_rem),
                    "currency": str(crow.get("currency", "INR"))
                })

            candidates = [c["po_number"] for c in candidate_details]

            # If exactly 1 open PO exists for this vendor
            if len(candidates) == 1:
                row = vendor_pos.iloc[0]
                po_num = str(row["po_number"])
                po_tot = Decimal(str(row["po_total"]))
                c_billed = self.repository.get_cumulative_billed_for_po(po_num) if self.repository else Decimal("0.00")
                dyn_rem = max(po_tot - c_billed, Decimal("0.00"))
                prior_invoices = self.repository.get_accepted_invoices_for_po(po_num) if self.repository else []
                is_partial = (invoice_total is not None and invoice_total < po_tot) or (c_billed > Decimal("0.00"))

                return POMatchingResult(
                    is_matched=True,
                    po_number=po_num,
                    po_vendor_id=str(row["vendor_id"]),
                    po_status=str(row["po_status"]).upper(),
                    po_total=po_tot,
                    initial_po_total=po_tot,
                    cumulative_billed_amount=c_billed,
                    dynamic_remaining_balance=dyn_rem,
                    remaining_balance=dyn_rem,
                    prior_accepted_invoices=prior_invoices,
                    is_partial_invoice=is_partial,
                    currency=str(row.get("currency", "INR")),
                    match_type="FALLBACK_CANDIDATE",
                    candidate_po_count=1,
                    candidate_pos=[po_num],
                    candidate_po_details=candidate_details,
                    match_confidence=0.85,
                    notes=f"Missing PO inferred: Sole active open PO ({po_num}) for vendor [{verified_vendor_id}].",
                    line_matches=self._match_line_items(po_num, line_items or [])
                )
            else:
                # Multiple candidate POs exist -> AMBIGUOUS MATCH
                return POMatchingResult(
                    is_matched=False,
                    match_type="AMBIGUOUS",
                    candidate_po_count=len(candidates),
                    candidate_pos=candidates,
                    candidate_po_details=candidate_details,
                    match_confidence=0.30,
                    notes=(
                        f"Missing PO reference: Multiple ({len(candidates)}) open POs found for vendor "
                        f"[{verified_vendor_id}]: {', '.join(candidates)}. Human specialist assignment required."
                    )
                )

        return POMatchingResult(
            is_matched=False,
            match_type="NONE",
            notes="Missing PO reference and vendor identity could not be established."
        )

    def _match_line_items(self, po_number: str, invoice_items: List[LineItem]) -> List[Dict[str, Any]]:
        if self.lines_df.empty or not invoice_items:
            return []

        po_items = self.lines_df[self.lines_df["po_number"] == po_number]
        results = []

        for inv_item in invoice_items:
            inv_desc = (inv_item.description or "").lower()
            best_po_item = None
            for _, po_row in po_items.iterrows():
                po_desc = str(po_row["description"]).lower()
                # Partial token overlap matching
                if inv_desc in po_desc or po_desc in inv_desc or any(w in po_desc for w in inv_desc.split() if len(w) > 3):
                    best_po_item = po_row
                    break

            if best_po_item is not None:
                results.append({
                    "invoice_description": inv_item.description,
                    "po_item_id": best_po_item["item_id"],
                    "po_description": best_po_item["description"],
                    "invoice_qty": float(inv_item.quantity or 0),
                    "po_qty": float(best_po_item["quantity"]),
                    "invoice_unit_price": float(inv_item.unit_price or 0),
                    "po_unit_price": float(best_po_item["unit_price"]),
                    "qty_variance": float(inv_item.quantity or 0) - float(best_po_item["quantity"]),
                    "price_variance": float(inv_item.unit_price or 0) - float(best_po_item["unit_price"]),
                })

        return results
