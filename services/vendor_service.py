import re
import difflib
import pandas as pd
from typing import List, Optional
from config.settings import VENDORS_CSV
from core.models import VendorRecord, VendorValidationResult

class VendorService:
    def __init__(self, vendors_csv_path: Optional[str] = None):
        self.csv_path = vendors_csv_path or str(VENDORS_CSV)
        self.vendors: List[VendorRecord] = self._load_vendors()

    def _load_vendors(self) -> List[VendorRecord]:
        try:
            df = pd.read_csv(self.csv_path)
            records = []
            for _, row in df.iterrows():
                approved = str(row.get("approved_flag", "false")).strip().lower() in ("true", "1", "yes")
                records.append(VendorRecord(
                    vendor_id=str(row["vendor_id"]).strip(),
                    legal_name=str(row["legal_name"]).strip(),
                    normalized_name=str(row["normalized_name"]).strip().upper(),
                    tax_id=str(row["tax_id"]).strip().upper(),
                    status=str(row["status"]).strip().upper(),
                    approved_flag=approved
                ))
            return records
        except Exception as e:
            return []

    def normalize_vendor_name(self, name: str) -> str:
        """Strip punctuation, legal suffixes, and uppercase for comparison."""
        if not name:
            return ""
        cleaned = name.upper()
        # Remove common legal forms
        cleaned = re.sub(r"\b(PRIVATE|LIMITED|LTD|PVT|LLC|INC|CORP|CORPORATION|SERVICES|SOLUTIONS)\b", "", cleaned)
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def verify_vendor(
        self,
        extracted_name: Optional[str],
        extracted_tax_id: Optional[str] = None
    ) -> VendorValidationResult:
        """
        Verify vendor identity following strict verification hierarchy:
        1. Exact Tax ID (GSTIN)
        2. Exact Normalized Name
        3. Fuzzy Name Matching (> 0.85 similarity)
        """
        warnings = []

        if not extracted_name and not extracted_tax_id:
            return VendorValidationResult(
                is_verified=False,
                match_type="NONE",
                notes="Neither vendor name nor tax ID was extracted from invoice.",
                warnings=["Missing vendor identifier in document"]
            )

        # 1. Exact Tax ID Match
        if extracted_tax_id:
            clean_tax = extracted_tax_id.strip().upper()
            for v in self.vendors:
                if v.tax_id == clean_tax:
                    is_active = (v.status == "ACTIVE")
                    is_approved = v.approved_flag and is_active
                    notes = f"Verified by Tax ID ({clean_tax}). Status: {v.status}, Approved: {v.approved_flag}."
                    if not is_approved:
                        warnings.append(f"Vendor is {v.status} or unapproved in Vendor Master.")
                    return VendorValidationResult(
                        is_verified=True,
                        vendor_id=v.vendor_id,
                        legal_name=v.legal_name,
                        status=v.status,
                        is_approved=is_approved,
                        match_type="EXACT_TAX_ID",
                        match_confidence=1.0,
                        notes=notes,
                        warnings=warnings
                    )

        # 2. Exact Normalized Name Match
        if extracted_name:
            norm_extracted = self.normalize_vendor_name(extracted_name)
            for v in self.vendors:
                norm_master = self.normalize_vendor_name(v.legal_name)
                if norm_extracted and (norm_extracted == norm_master or norm_extracted in norm_master or norm_master in norm_extracted):
                    is_active = (v.status == "ACTIVE")
                    is_approved = v.approved_flag and is_active
                    notes = f"Verified by normalized name match with '{v.legal_name}'."
                    if not is_approved:
                        warnings.append(f"Vendor is {v.status} or unapproved in Vendor Master.")
                    return VendorValidationResult(
                        is_verified=True,
                        vendor_id=v.vendor_id,
                        legal_name=v.legal_name,
                        status=v.status,
                        is_approved=is_approved,
                        match_type="EXACT_NAME",
                        match_confidence=0.95,
                        notes=notes,
                        warnings=warnings
                    )

            # 3. Fuzzy Name Match
            best_match: Optional[VendorRecord] = None
            best_score = 0.0
            for v in self.vendors:
                score = difflib.SequenceMatcher(None, norm_extracted, self.normalize_vendor_name(v.legal_name)).ratio()
                if score > best_score:
                    best_score = score
                    best_match = v

            if best_match and best_score >= 0.80:
                is_active = (best_match.status == "ACTIVE")
                is_approved = best_match.approved_flag and is_active
                notes = f"Fuzzy matched to '{best_match.legal_name}' with {int(best_score*100)}% similarity."
                if best_score < 0.90:
                    warnings.append(f"Fuzzy match similarity is moderate ({int(best_score*100)}%). Verification recommended.")
                return VendorValidationResult(
                    is_verified=True,
                    vendor_id=best_match.vendor_id,
                    legal_name=best_match.legal_name,
                    status=best_match.status,
                    is_approved=is_approved,
                    match_type="FUZZY_NAME",
                    match_confidence=round(best_score, 2),
                    notes=notes,
                    warnings=warnings
                )

        return VendorValidationResult(
            is_verified=False,
            match_type="NONE",
            match_confidence=0.0,
            notes=f"No matching active vendor found in Master Records for '{extracted_name or 'N/A'}'.",
            warnings=["Vendor not found in authorized vendor database"]
        )
