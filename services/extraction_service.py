import json
import re
from decimal import Decimal
from typing import Any, Dict, List, Optional
from config.settings import GEMINI_API_KEY, OPENAI_API_KEY, AI_PROVIDER
from core.models import ExtractedInvoiceData, LineItem
from core.exceptions import ExtractionError

class ExtractionService:
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.preferred_provider = AI_PROVIDER

    def extract(self, text: str, is_ocr: bool = False, ocr_confidence: float = 1.0) -> ExtractedInvoiceData:
        """
        Extract structured invoice data from text using LLM if configured and available,
        otherwise fall back gracefully to the deterministic extraction engine.
        """
        if not text or not text.strip():
            return ExtractedInvoiceData(
                extraction_mode="empty_text",
                ocr_applied=is_ocr,
                extraction_evidence={"error": "No text provided for extraction"}
            )

        # 1. Attempt LLM extraction if an API key is available
        if (self.gemini_key or self.openai_key) and self.preferred_provider != "deterministic":
            try:
                if self.gemini_key and (self.preferred_provider in ("gemini", "auto")):
                    return self._extract_with_gemini(text, is_ocr, ocr_confidence)
                elif self.openai_key and (self.preferred_provider in ("openai", "auto")):
                    return self._extract_with_openai(text, is_ocr, ocr_confidence)
            except Exception as e:
                # Log LLM extraction failure and proceed with deterministic fallback
                pass

        # 2. Deterministic Extraction Engine
        return self._extract_deterministic(text, is_ocr, ocr_confidence)

    def _extract_with_gemini(self, text: str, is_ocr: bool, ocr_confidence: float) -> ExtractedInvoiceData:
        from google import genai
        client = genai.Client(api_key=self.gemini_key)
        
        prompt = f"""
You are an expert Accounts Payable AI extractor.
Extract invoice data from the following document text into strict JSON.

Rules:
- Never hallucinate or guess missing fields.
- If a field is not present or cannot be determined with certainty, output null.
- Separate subtotal, tax, and invoice total.
- Extract individual line items with description, quantity, unit_price, line_total, tax_rate.

Required JSON structure:
{{
  "vendor_name": null,
  "vendor_tax_id": null,
  "invoice_number": null,
  "invoice_date": null,
  "po_number": null,
  "currency": null,
  "line_items": [
    {{
      "description": null,
      "quantity": null,
      "unit_price": null,
      "line_total": null,
      "tax_rate": null
    }}
  ],
  "subtotal": null,
  "tax": null,
  "invoice_total": null
}}

DOCUMENT TEXT:
{text}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        return self._parse_json_to_extracted_data(data, mode="gemini_llm", is_ocr=is_ocr, raw_text=text)

    def _extract_with_openai(self, text: str, is_ocr: bool, ocr_confidence: float) -> ExtractedInvoiceData:
        # Generic provider placeholder for OpenAI if key is configured
        return self._extract_deterministic(text, is_ocr, ocr_confidence)

    def _extract_deterministic(self, text: str, is_ocr: bool, ocr_confidence: float) -> ExtractedInvoiceData:
        evidence: Dict[str, Any] = {}
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # 1. Tax ID (GSTIN: 15 chars alphanumeric)
        tax_id = None
        tax_match = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1})\b", text)
        if tax_match:
            tax_id = tax_match.group(1)
            evidence["tax_id"] = {"raw": tax_id, "confidence": 0.98}

        # 2. Vendor Name
        vendor_name = None
        # Check first non-title line
        vendor_keywords = [
            "ltd", "limited", "corp", "inc", "llc", "systems", "services",
            "consulting", "solutions", "logistics", "labs", "enterprises", "technologies"
        ]
        for line in lines[:8]:
            line_clean = line.strip()
            if line_clean.upper() in ("TAX INVOICE", "INVOICE", "BILL OF SUPPLY", "RECEIPT"):
                continue
            if any(term in line_clean.lower() for term in vendor_keywords):
                clean_name = re.sub(r"^(vendor|from|billed by|seller)[:\s-]*", "", line_clean, flags=re.IGNORECASE).strip()
                if clean_name and len(clean_name) > 3:
                    vendor_name = clean_name
                    evidence["vendor_name"] = {"raw": vendor_name, "confidence": 0.94}
                    break
        
        # Fallback: take first non-title, non-tax line if still None
        if not vendor_name and lines:
            for line in lines[:4]:
                line_clean = line.strip()
                if (
                    line_clean.upper() not in ("TAX INVOICE", "INVOICE", "BILL OF SUPPLY", "RECEIPT")
                    and not re.search(r"Tax\s*ID|GSTIN|Invoice\s*No", line_clean, re.IGNORECASE)
                    and len(line_clean) > 3
                ):
                    vendor_name = line_clean
                    evidence["vendor_name"] = {"raw": vendor_name, "confidence": 0.85}
                    break

        # 3. Invoice Number
        invoice_number = None
        inv_match = re.search(r"(?:Invoice\s*(?:No|Number|#)|Inv\s*#)[:.\s]*([A-Z0-9\-_/]+)", text, re.IGNORECASE)
        if inv_match:
            invoice_number = inv_match.group(1).strip()
            evidence["invoice_number"] = {"raw": invoice_number, "confidence": 0.95}

        # 4. Invoice Date
        invoice_date = None
        date_match = re.search(r"(?:Invoice\s*Date|Date)[:.\s]*([0-9]{4}[-/][0-9]{2}[-/][0-9]{2}|[0-9]{2}[-/][0-9]{2}[-/][0-9]{4}|[0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4})", text, re.IGNORECASE)
        if date_match:
            invoice_date = date_match.group(1).strip()
            evidence["invoice_date"] = {"raw": invoice_date, "confidence": 0.95}

        # 5. PO Number
        po_number = None
        po_match = re.search(r"(?:PO\s*(?:No|Number|#)?|P\.O\.|Purchase\s*Order\s*(?:No|Number|#)?)[:.\s]*([A-Z0-9\-_/]+)", text, re.IGNORECASE)
        if po_match:
            candidate_po = po_match.group(1).strip()
            if candidate_po.upper() not in ("DATE", "TOTAL", "AMOUNT", "DETAILS"):
                po_number = candidate_po
                evidence["po_number"] = {"raw": po_number, "confidence": 0.95}

        # 6. Currency
        currency = "INR"
        if re.search(r"(\$|USD)", text):
            currency = "USD"
        elif re.search(r"(€|EUR)", text):
            currency = "EUR"
        elif re.search(r"(₹|INR|Rs\.?)", text):
            currency = "INR"
        evidence["currency"] = {"raw": currency, "confidence": 0.90}

        # 7. Financial Totals (Subtotal, Tax, Total, Embedded Tax Check)
        is_tax_embedded = bool(re.search(
            r"(?:inclusive\s*of\s*all\s*taxes|incl\.\s*all\s*taxes|inclusive\s*of\s*gst|tax\s*included|mrp\s*incl|embedded\s*tax)",
            text, re.IGNORECASE
        ))
        is_bundled = bool(re.search(
            r"(?:bundled|lump\s*sum|milestone\s*fee|consolidated\s*service|retainer|package\s*fee)",
            text, re.IGNORECASE
        ))

        subtotal = None
        subtotal_match = re.search(r"(?:Subtotal|Sub-Total|Net\s*Amount)[:.\s]*(?:INR|Rs\.?|USD|EUR|[₹$€])?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        if subtotal_match:
            try:
                subtotal = Decimal(subtotal_match.group(1).replace(",", ""))
                evidence["subtotal"] = {"raw": str(subtotal), "confidence": 0.95}
            except Exception:
                pass

        tax = None
        tax_match_val = re.search(r"(?:Total\s*Tax(?:\s*\(GST\))?|Tax\s*(?:\([0-9%]+\))?|GST|VAT|CGST\s*\+\s*SGST)[:.\s]*(?:INR|Rs\.?|USD|EUR|[₹$€])?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        if tax_match_val:
            try:
                tax = Decimal(tax_match_val.group(1).replace(",", ""))
                evidence["tax"] = {"raw": str(tax), "confidence": 0.92}
            except Exception:
                pass

        invoice_total = None
        # Primary search for explicit Grand Total / Total Amount / Invoice Total
        total_match = re.search(r"(?:Grand\s*Total|Total\s*Amount|Invoice\s*Total|Amount\s*Payable|Net\s*Payable)[:.\s]*(?:INR|Rs\.?|USD|EUR|[₹$€])?\s*([0-9,]+(?:\.[0-9]{2})?)", text, re.IGNORECASE)
        if total_match:
            try:
                invoice_total = Decimal(total_match.group(1).replace(",", ""))
                evidence["invoice_total"] = {"raw": str(invoice_total), "confidence": 0.98}
            except Exception:
                pass
        
        # Secondary fallback: search from bottom up for standalone 'Total:'
        if invoice_total is None:
            for line in reversed(lines):
                line_s = line.strip()
                if re.search(r"Line\s*Total|Total\s*Tax|Subtotal", line_s, re.IGNORECASE):
                    continue
                generic_total = re.search(r"\bTotal[:.\s]*(?:INR|Rs\.?|USD|EUR|[₹$€])?\s*([0-9,]+(?:\.[0-9]{2})?)", line_s, re.IGNORECASE)
                if generic_total:
                    try:
                        invoice_total = Decimal(generic_total.group(1).replace(",", ""))
                        evidence["invoice_total"] = {"raw": str(invoice_total), "confidence": 0.90}
                        break
                    except Exception:
                        pass

        # Deduce base amount and adjust subtotal if tax is embedded
        base_amount = subtotal
        if is_tax_embedded and invoice_total is not None and tax is not None:
            base_amount = invoice_total - tax
            if subtotal is None or subtotal == invoice_total:
                subtotal = base_amount

        # 8. Line Items
        line_items: List[LineItem] = []
        for line in lines:
            # Match line items of format: Description | Qty | Rate | Total or table columns
            table_row_match = re.search(
                r"^(.+?)\s+(\d+)\s+([0-9,]+(?:\.[0-9]{2})?)\s+([0-9,]+(?:\.[0-9]{2})?)$",
                line
            )
            if table_row_match:
                desc = table_row_match.group(1).strip()
                if not any(hdr in desc.lower() for hdr in ["description", "item", "total", "subtotal", "tax"]):
                    try:
                        q = Decimal(table_row_match.group(2))
                        p = Decimal(table_row_match.group(3).replace(",", ""))
                        lt = Decimal(table_row_match.group(4).replace(",", ""))
                        line_items.append(LineItem(
                            description=desc,
                            quantity=q,
                            unit_price=p,
                            line_total=lt,
                            confidence=0.90
                        ))
                    except Exception:
                        pass
            else:
                # Match line items with pipe separators (e.g., Description | Qty: 2 | Rate: 25000 | Total: 50000)
                pipe_match = re.search(r"^(?:Description:\s*)?(.+?)\s*\|\s*(?:Qty|Quantity):\s*(\d+)\s*\|\s*(?:Rate|Price):\s*([0-9,]+(?:\.[0-9]{2})?)\s*\|\s*(?:Total):\s*([0-9,]+(?:\.[0-9]{2})?)", line, re.IGNORECASE)
                if pipe_match:
                    try:
                        line_items.append(LineItem(
                            description=pipe_match.group(1).strip(),
                            quantity=Decimal(pipe_match.group(2)),
                            unit_price=Decimal(pipe_match.group(3).replace(",", "")),
                            line_total=Decimal(pipe_match.group(4).replace(",", "")),
                            confidence=0.92
                        ))
                    except Exception:
                        pass

        mode = "ocr_fallback" if is_ocr else "deterministic"
        if is_ocr:
            for k in evidence:
                evidence[k]["confidence"] = round(evidence[k].get("confidence", 0.9) * ocr_confidence, 2)

        return ExtractedInvoiceData(
            vendor_name=vendor_name,
            vendor_tax_id=tax_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            po_number=po_number,
            currency=currency,
            line_items=line_items,
            subtotal=subtotal,
            tax=tax,
            invoice_total=invoice_total,
            base_amount=base_amount,
            is_tax_embedded=is_tax_embedded,
            is_tax_separate=not is_tax_embedded,
            is_bundled_line_items=is_bundled or (len(line_items) == 1 and line_items[0].quantity == 1),
            extraction_evidence=evidence,
            extraction_mode=mode,
            ocr_applied=is_ocr,
            raw_text_snippet=text[:500] if text else None
        )

    def _parse_json_to_extracted_data(self, data: Dict[str, Any], mode: str, is_ocr: bool, raw_text: str) -> ExtractedInvoiceData:
        line_items = []
        for li in data.get("line_items", []):
            try:
                line_items.append(LineItem(
                    description=li.get("description"),
                    quantity=Decimal(str(li["quantity"])) if li.get("quantity") is not None else None,
                    unit_price=Decimal(str(li["unit_price"])) if li.get("unit_price") is not None else None,
                    line_total=Decimal(str(li["line_total"])) if li.get("line_total") is not None else None,
                    tax_rate=Decimal(str(li["tax_rate"])) if li.get("tax_rate") is not None else None,
                    confidence=0.95
                ))
            except Exception:
                pass

        def _to_dec(val: Any) -> Optional[Decimal]:
            if val is None or val == "":
                return None
            try:
                return Decimal(str(val).replace(",", "").replace("₹", "").replace("$", ""))
            except Exception:
                return None

        return ExtractedInvoiceData(
            vendor_name=data.get("vendor_name"),
            vendor_tax_id=data.get("vendor_tax_id"),
            invoice_number=data.get("invoice_number"),
            invoice_date=data.get("invoice_date"),
            po_number=data.get("po_number"),
            currency=data.get("currency") or "INR",
            line_items=line_items,
            subtotal=_to_dec(data.get("subtotal")),
            tax=_to_dec(data.get("tax")),
            invoice_total=_to_dec(data.get("invoice_total")),
            extraction_evidence={"source": "llm_structured_output"},
            extraction_mode=mode,
            ocr_applied=is_ocr,
            raw_text_snippet=raw_text[:500] if raw_text else None
        )
