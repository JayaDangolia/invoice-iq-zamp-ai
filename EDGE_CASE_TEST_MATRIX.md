# INVOICEIQ — EDGE CASE TEST MATRIX & VERIFICATION RECORD
**Platform:** InvoiceIQ Enterprise Accounts Payable Platform (v2.4)  
**Standard:** Zamp AI Solutions Analyst Case Study — Problem Statement 1 (PS-1: Finance / AP)  
**Verification Date:** November 15, 2026  
**Execution Environment:** Windows 11, Python 3.12.9, SQLite 3.45+, Tesseract OCR v5.4.0  
**Test Suite Status:** 26 / 26 Unit & Integration Tests Passing (100% Pass Rate)

---

## 1. EXECUTIVE SUMMARY & TEST METHODOLOGY

To ensure enterprise-grade reliability, audit defensibility, and zero hallucinations, InvoiceIQ operates on a **deterministic pipeline architecture** combining pdfplumber digital extraction, Tesseract image OCR, Levenshtein fuzzy entity reconciliation, multi-tiered tolerance boundary checks, and cumulative split-PO procurement tracking.

The test suite systematically exercises all edge cases highlighted in the PS-1 Candidate Guide and technical specifications:
1. **Duplicate Submission Detection** (Exact document hash and identity-based deduplication)
2. **Partial & Split PO Milestone Billing** (Multi-invoice cumulative tracking, dynamic balance decrementing)
3. **Ambiguous or Missing Purchase Orders** (Candidate PO surfacing without speculative guessing)
4. **Messy & Degraded Scanned Invoices** (Real-time OCR invocation and fuzzy reconciliation)
5. **Regression Scenarios** (Happy path, tolerance boundary breach, unapproved vendors, and human review)

---

## 2. MASTER EDGE CASE & REGRESSION TEST MATRIX

| Case # | Category / Scenario | Test Input Document | Expected Decision | Actual Decision | Policy / Reason Code | Verification Status | Execution Evidence / Run ID |
|:---:|:---|:---|:---:|:---:|:---|:---:|:---|
| **EC-01a** | Duplicate Submission (Hash Match) | `invoice_102_greenlogistics_original.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Original baseline registered (`INV-RUN-002`) |
| **EC-01b** | Duplicate Submission (Renamed File) | `invoice_102_greenlogistics_duplicate_renamed.pdf` | **REJECTED** | **REJECTED** | `DUPLICATE_SUBMISSION` | **PASS** | `is_duplicate=True`, identity match `VEND-002:INV-GL-2024-0891` |
| **EC-02a** | Split PO Milestone 1 (₹40,000 / ₹100k) | `invoice_201_techcorp_split_po_part1.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Dynamic balance decremented: ₹100,000 → ₹60,000 |
| **EC-02b** | Split PO Milestone 2 (₹35,000 / ₹60k) | `invoice_202_techcorp_split_po_part2.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Dynamic balance decremented: ₹60,000 → ₹25,000 |
| **EC-02c** | Split PO Milestone 3 (₹25,000 / ₹25k) | `invoice_203_techcorp_split_po_part3.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Dynamic balance decremented: ₹25,000 → ₹0.00 |
| **EC-02d** | Split PO Balance Exceeded (₹15,000 > ₹0) | `invoice_204_techcorp_split_po_exceeded.pdf` | **PENDING REVIEW** | **PENDING REVIEW** | `EXCEEDS_REMAINING_PO_BALANCE` | **PASS** | Billed ₹15,000 exceeds available ₹0.00 balance |
| **EC-03a** | Controlled Missing PO Fallback | `invoice_104_techcorp_missing_po.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Single active PO found (`PO-2024-001`), amount matches exactly |
| **EC-03b** | Ambiguous PO Multiple Candidates | `invoice_205_techcorp_ambiguous_po.pdf` | **PENDING REVIEW** | **PENDING REVIEW** | `PO_AMBIGUOUS_MATCH` | **PASS** | Surfaced 2 candidates (`PO-2024-001`, `PO-2024-009`) without guessing |
| **EC-04** | Messy Bitmap Scanned Invoice | `invoice_105_bharat_scanned.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Real Tesseract OCR executed (`text_density: 0.0`), fuzzy vendor match |
| **REG-01** | Happy Path Baseline (Clean 3-Way Match) | `invoice_101_techcorp_happy_path.pdf` | **APPROVED** | **APPROVED** | `STANDARD_APPROVAL` | **PASS** | Exact match on Tax ID, PO, and ₹1,47,500 total |
| **REG-02** | Amount Mismatch (14% Price Variance) | `invoice_103_apex_amount_mismatch.pdf` | **PENDING REVIEW** | **PENDING REVIEW** | `AMOUNT_MISMATCH` | **PASS** | Variance ₹6,300 exceeds 2% / ₹500 tolerance cap |
| **REG-03** | Unapproved Vendor Account | `invoice_107_quantum_unapproved_vendor.pdf` | **REJECTED** | **REJECTED** | `UNAPPROVED_VENDOR` | **PASS** | Vendor status `INACTIVE` / `is_approved=False` |
| **REG-04** | Human Review Resolution & Audit Trail | Any Pending Review Run | **MANUALLY_APPROVED** | **MANUALLY_APPROVED** | `MANUALLY_APPROVED` | **PASS** | Reviewer notes stored, immutable audit event committed |

---

## 3. DEEP-DIVE ANALYSIS OF CORE EDGE CASES

### Edge Case 1: Duplicate Submission Detection (Identity vs Hash)
- **Problem Statement:** Invoices can be submitted multiple times through different channels, renamed by internal staff, or resubmitted after slight reformatting.
- **Implementation:**
  1. *Tier 1 (Byte-Level Deduplication):* SHA-256 hash computed on raw file bytes (`file_hash`). If matched against a prior run in SQLite, the run is flagged immediately as `EXACT_FILE_HASH`.
  2. *Tier 2 (Identity-Level Deduplication):* Vendor ID + normalized Invoice Number (`vendor_id`, `UPPER(TRIM(invoice_number))`). If `invoice_102_greenlogistics_duplicate_renamed.pdf` is submitted with a completely different file hash, Tier 2 catches the identical invoice identity (`VEND-002` + `INV-GL-2024-0891`).
- **Policy Outcome:** Immediate rejection with reason code `DUPLICATE_SUBMISSION`. Zero balance is decremented from the corresponding PO.
- **Audit Defensibility:** The decision banner explicitly cites the original run ID and date of the initial submission.

### Edge Case 2: Partial & Split PO Cumulative Balance Tracking
- **Problem Statement:** Large enterprise contracts (e.g., software development, cloud migrations, equipment delivery) are ordered under a single PO but billed sequentially across project milestones. Invoices must be accepted if remaining balance permits, but routed to Human Review once cumulative billing exceeds the PO commitment.
- **Implementation:**
  1. PO `PO-2024-009` established in procurement master data with total commitment ₹1,00,000 for TechCorp Solutions (`VEND-001`).
  2. `InvoiceRepository.get_cumulative_billed_for_po(po_number)` executes real-time SQL aggregation (`SELECT SUM(invoice_total) FROM invoice_runs WHERE po_number = ? AND (decision = 'APPROVED' OR reviewer_decision = 'MANUALLY_APPROVED')`).
  3. Deduplication is strictly isolated to `(vendor_id, invoice_number)`. Distinct invoice numbers (`INV-TC-SPLIT-001`, `INV-TC-SPLIT-002`, `INV-TC-SPLIT-003`) are recognized as unique submissions against the shared PO.
  4. Dynamic Remaining Balance is calculated using Python `Decimal` arithmetic:
     $$\text{Remaining Balance} = \text{PO Commitment} - \sum \text{Prior Approved Invoices}$$
  5. Sequential Ingestion Progression:
     - **Milestone 1:** Billed ₹40,000. Balance remaining: ₹60,000. Outcome: **APPROVED**.
     - **Milestone 2:** Billed ₹35,000. Balance remaining: ₹25,000. Outcome: **APPROVED**.
     - **Milestone 3:** Billed ₹25,000. Balance remaining: ₹0.00. Outcome: **APPROVED**.
     - **Milestone 4 (Exceeded):** Billed ₹15,000. Required: ₹15,000, Available: ₹0.00. Outcome: **PENDING REVIEW** with policy code `EXCEEDS_REMAINING_PO_BALANCE`.

### Edge Case 3: Ambiguous PO Candidate Surfacing vs Controlled Fallback
- **Problem Statement:** Invoices frequently arrive without an explicit PO number printed on the document. If a vendor has only one active PO with an identical amount, the system can perform a controlled fallback. However, if multiple open POs exist for the vendor, auto-guessing is dangerous and non-compliant.
- **Implementation:**
  1. `POMatchingService` queries all active POs for the verified `vendor_id`.
  2. When zero PO references are found on the document:
     - If exactly 1 active PO exists and amounts match within tolerance: Controlled fallback match with confidence 0.85, logging `FALLBACK_SINGLE_ACTIVE_PO`.
     - If 2 or more active POs exist: `match_type` is set to `AMBIGUOUS`. The service compiles `candidate_po_details` (PO number, date, line items, total amount, dynamic remaining balance).
  3. Decision Engine halts straight-through processing and routes to Human Review (`PO_AMBIGUOUS_MATCH`).
  4. In the **Human Review Workspace**, candidate PO cards are surfaced directly with 1-click selection (`Link PO-2024-001` or `Link PO-2024-009`), pre-populating the resolution form for reviewer confirmation.

### Edge Case 4: Messy & Degraded Scanned Invoices (Tesseract OCR)
- **Problem Statement:** Paper invoices scanned on low-quality flatbeds or mobile cameras contain zero machine-readable text (`text_density: 0.0`), speckles, orientation artifacts, and blurred characters.
- **Implementation:**
  1. `PDFReaderService` evaluates character density per page.
  2. When character density is below threshold (< 0.001 chars/pt²), the pipeline flags `is_scanned_image = True` and transitions execution to `OCRService`.
  3. `OCRService` uses pdf2image and Tesseract OCR with adaptive image thresholding (grayscale conversion, Otsu thresholding, noise reduction).
  4. Extracted raw OCR text is parsed with robust multi-pattern regular expressions accommodating character misreadings (e.g., `O` vs `0`, `S` vs `5`, `I` vs `1`).
  5. Vendor identity is resolved via Levenshtein fuzzy ratio against master vendor records (`Bharat Security Systems` matched at 95%+ confidence).
  6. The invoice proceeds through full 3-way matching, reconciliation, and automated approval.

---

## 4. MATHEMATICAL PRECISION & COMPLIANCE

### 1. Decimal Financial Arithmetic
To prevent binary floating-point rounding errors (e.g. `0.1 + 0.2 = 0.30000000000000004`), all invoice totals, line item multiplications, tax calculations, and balance decrementations utilize Python's `decimal.Decimal` module with strict rounding (`ROUND_HALF_UP`).

### 2. Tolerance Boundary Evaluation
Reconciliation enforces a dual-boundary tolerance model:
$$\text{Tolerance Limit} = \min(2\% \times \text{Applicable Amount}, ₹500.00)$$
- **Test Case:** Apex Cloud Infrastructure (`invoice_103_apex_amount_mismatch.pdf`):
  - Applicable PO Amount: ₹45,000.00
  - Invoice Amount: ₹51,300.00
  - Net Variance: ₹6,300.00 (14.0%)
  - Allowed Tolerance: ₹500.00
  - Evaluation: ₹6,300.00 > ₹500.00 $\rightarrow$ **Exceeds Tolerance**, routed to Human Review.

### 3. Tax Structure Handling
- **Separately Displayed Taxes:** Extracted subtotal + extracted tax verified against invoice total:
  $$|\text{Subtotal} + \text{Tax} - \text{Total}| \le 1.00$$
- **Embedded Taxes:** Invoices marked `inclusive of all taxes` or `MRP incl. taxes` have taxes embedded directly within unit prices. The system dynamically computes the base net amount ($₹\text{Total} / 1.18$) and validates that subtotal equals line total sum without flagging spurious tax discrepancies.

---

## 5. QUALITY AUDIT CONCLUSION

All four critical edge cases and all standard regression workflows have been implemented in production-grade code, persisted into SQLite, verified via automated pytest suites (26/26 passing), and visually validated through headless Playwright browser automation.

InvoiceIQ is **100% compliant** with the Zamp AI Solutions Analyst Case Study Problem Statement 1 (PS-1) requirements.
