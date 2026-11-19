# InvoiceIQ: Premium AI-Powered Invoice Processing & Decision Automation Platform

> **Intelligent Invoice Processing. Explainable Decisions.**
> 
> Core Deliverable for Zamp AI Solutions Analyst Case Study — Problem Statement 1 (PS-1: Finance / AP — Invoice Processing).

---

## 1. Executive Summary & Product Vision

Mid-sized enterprises receive hundreds of vendor invoices monthly as PDFs. Accounts Payable (AP) specialists spend countless hours manually parsing document headers, cross-referencing Purchase Orders (POs), checking vendor tax IDs, detecting duplicates, and calculating tolerance variances.

**InvoiceIQ** is an enterprise SaaS platform built with the design principles of **Linear, Stripe Dashboard, and Ramp**. It transforms AP operations from manual data entry to straight-through automated decisioning with complete explainability, 3-way matching, and an immutable audit trail.

### End-to-End Processing Loop:
$$\text{Upload PDF} \longrightarrow \text{Text / OCR Ingestion} \longrightarrow \text{Structured Extraction} \longrightarrow \text{Vendor Validation} \longrightarrow \text{Duplicate Detection} \longrightarrow \text{PO Matching} \longrightarrow \text{Financial Reconciliation} \longrightarrow \text{Deterministic Decision} \longrightarrow \text{Audit Persistence}$$

---

## 2. Core Capabilities & Architectural Pillars

| Capability | Implementation & Business Rule |
| :--- | :--- |
| **PDF Ingestion & Dual OCR** | Native text extraction via **PyMuPDF** (`pymupdf`). Scanned or degraded bitmaps automatically trigger dual-layer OCR fallback with character confidence metrics. |
| **Structured AI Extraction** | Provider-independent extraction interface supporting **Google Gemini API** (`gemini-2.5-flash`), with a deterministic rule/regex fallback when no API key is supplied. Never hallucinates missing data; outputs nulls faithfully. |
| **Vendor Master Verification** | Matches against master records by **Exact GSTIN / Tax ID** $\to$ **Normalized Legal Name** $\to$ **Fuzzy Similarity (>80%)**. Confirmed inactive or unapproved vendors are automatically rejected. |
| **Duplicate Prevention** | Primary matching on **Vendor ID + Normalized Invoice #** alongside **SHA-256 File Hash**. Detects renamed files with identical invoice content and preserves prior run references. |
| **3-Way PO Matching** | Exact PO verification, vendor ownership validation, and remaining balance checks. Supports controlled fallback matching for missing PO numbers. |
| **Financial Reconciliation** | High-precision arithmetic using Python `Decimal`. Configurable prototype tolerance: **2% of applicable PO amount, capped at ₹500** (`config/rules.yaml`). |
| **Deterministic Decision Engine** | Explicit precedence rules producing **APPROVED**, **PENDING REVIEW**, or **REJECTED** with human-readable, mathematically grounded explanations. |
| **Human-in-the-Loop Review** | Dedicated review queue where AP specialists inspect document previews, correct fields, record notes, and manually resolve discrepancies while preserving original automated decisions. |
| **Audit Persistence** | Persistent **SQLite** storage (`invoiceiq.db`) tracking every run, execution duration, and immutable timeline event. |

---

## 3. Project Architecture & Folder Structure

```
invoiceiq/
├── app.py                     # Streamlit application entrypoint & routing
├── requirements.txt           # Production dependencies
├── README.md                  # Complete product & run documentation
├── .env.example               # Environment template (optional AI keys)
├── config/
│   ├── __init__.py
│   ├── settings.py            # Central settings, paths, environment loader
│   └── rules.yaml             # Configurable AP tolerances & policy rules
├── core/
│   ├── __init__.py
│   ├── models.py              # Pydantic V2 data schemas & domain models
│   ├── workflow.py            # 11-stage pipeline orchestrator with live callbacks
│   └── exceptions.py          # Domain-specific exception hierarchy
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLite schema initialization & connection pool
│   └── repository.py          # Data access layer, KPI queries, duplicate search
├── services/
│   ├── __init__.py
│   ├── pdf_reader.py          # PyMuPDF text & page layout extractor
│   ├── ocr_service.py         # Dual OCR fallback engine with confidence scoring
│   ├── extraction_service.py  # LLM (Gemini) & deterministic structured extractor
│   ├── vendor_service.py      # Vendor master matching (Tax ID, Name, Fuzzy)
│   ├── duplicate_service.py   # Content hash & business identity duplicate detector
│   ├── po_matching_service.py # 3-way PO & line item matcher with fallback
│   ├── reconciliation_service.py # Decimal variance & tolerance calculations
│   ├── decision_engine.py     # Deterministic policy precedence evaluator
│   ├── explanation_service.py # Natural language factual rationale generator
│   ├── audit_service.py       # Immutable audit event logger
│   └── reporting_service.py   # Downloadable CSV decision report generator
├── ui/
│   ├── __init__.py
│   ├── styles.py              # Custom CSS design system (Linear / Stripe inspired)
│   ├── components.py          # Reusable KPI cards, badges, banners, empty states
│   ├── dashboard.py           # Page 1: Executive AP Operations Dashboard
│   ├── upload.py              # Page 2: Drag-and-drop ingestion & demo selector
│   ├── live_run.py            # Page 2/3: Live stage execution & Decision Report
│   ├── review.py              # Page 4: Human Review Queue with manual resolution
│   └── history.py             # Page 5: Searchable history & immutable audit trail
├── data/
│   ├── README.md              # Documentation for synthetic datasets
│   ├── vendors.csv            # Vendor Master dataset (6 realistic vendors)
│   ├── purchase_orders.csv    # PO Master dataset (8 realistic POs)
│   ├── po_line_items.csv      # Itemized line item master records
│   ├── generate_sample_invoices.py # Synthetic PDF invoice generator
│   └── sample_invoices/       # Generated PDF invoice documents
└── tests/
    ├── __init__.py
    ├── test_extraction.py     # PDF reading, OCR, and extraction tests
    ├── test_vendor.py         # Tax ID, normalized name, fuzzy matching tests
    ├── test_duplicates.py     # Hash & business duplicate detection tests
    ├── test_po_matching.py    # PO match, status, vendor mismatch tests
    ├── test_decisions.py      # Reconciliation tolerances & decision precedence tests
    └── test_workflow.py       # Full end-to-end workflow & edge cases tests
```

---

## 4. Installation & Environment Setup

### Prerequisites
- Python 3.11 or Python 3.12 (Tested on Python 3.12.9)
- Windows, macOS, or Linux

### Step 1: Clone & Navigate
```bash
git clone <repo-url>
cd zamp.ai
```

### Step 2: Set Up Virtual Environment
```bash
# Windows
py -3.12 -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Variables (Optional)
InvoiceIQ works out of the box in **deterministic extraction mode** without any API keys. If you want to enable Gemini LLM extraction:
```bash
copy .env.example .env
# Edit .env and supply GEMINI_API_KEY=your_key_here
```

---

## 5. Running the Application

Launch the platform with a single command:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

The SQLite database (`invoiceiq.db`) will automatically initialize on the first run with all tables, indexes, and constraints.

---

## 6. Running the Automated Test Suite

All tests can be executed with Pytest:
```bash
pytest tests/ -v
```

All 23 unit and integration tests execute in **under 3 seconds**, validating:
- PDF extraction and OCR fallback
- Schema validation
- Vendor verification (Tax ID, Name, Fuzzy)
- Duplicate detection (File hash & renamed files)
- PO matching & fallback resolution
- Financial reconciliation & tolerance math (Decimal precision)
- Decision policy precedence
- All 4 required demonstration edge cases
- Reviewer manual actions and persistence

---

## 7. Demonstration Guide: Happy Path & 4 Required Edge Cases

For the interview presentation, all test documents are located in `data/sample_invoices/`. You can either drag-and-drop them or select them directly from the **Quick Demonstration Presets** dropdown in the **Process Invoice** tab.

### Scenario 1: Clean Happy-Path (Auto-Approved)
- **Document:** `data/sample_invoices/invoice_101_techcorp_happy_path.pdf`
- **Context:** TechCorp Solutions submitting invoice `INV-2024-001` against open `PO-2024-001`. Total: ₹125,000.00.
- **Expected Outcome:** `APPROVED`
- **What to Observe:**
  - 11 stages execute sequentially with green checkmarks.
  - Active approved vendor verified via GSTIN `27AABCT1234A1Z5`.
  - Matched PO `PO-2024-001` with ₹0 variance.
  - Explanation confirms clean pass and readiness for automated voucher posting.

---

### Scenario 2: Edge Case 1 — Duplicate Invoice Submission (Auto-Rejected)
- **Document A:** `data/sample_invoices/invoice_102_greenlogistics_original.pdf`
- **Document B:** `data/sample_invoices/invoice_102_greenlogistics_duplicate_renamed.pdf`
- **Context:** GreenLogistics invoice `INV-2024-GL08` is processed first. Then, a renamed file containing the same invoice identity is uploaded.
- **Expected Outcome:** `REJECTED` (Reason: `DUPLICATE_INVOICE_SUBMISSION`)
- **What to Observe:**
  - Stage 7 (Duplicate Detection) flags the prior submission.
  - Hard rejection banner citing the previous Run ID and submission timestamp.
  - Demonstrates that renaming a file does not fool the business-identity matching engine.

---

### Scenario 3: Edge Case 2 — Amount Mismatch Exceeding Tolerance (Pending Review)
- **Document:** `data/sample_invoices/invoice_103_apex_amount_mismatch.pdf`
- **Context:** Apex Cloud invoice for ₹57,000 against `PO-2024-002` (authorized for ₹50,000).
- **Expected Outcome:** `PENDING REVIEW` (Reason: `FINANCIAL_VARIANCE_EXCEEDS_TOLERANCE`)
- **What to Observe:**
  - System calculates variance: ₹7,000 (14.0%).
  - Configured tolerance limit is evaluated: 2% capped at ₹500.
  - Explanation explicitly states: *"The invoice has been placed under review because its total (₹57,000.00) exceeds the applicable PO amount (₹50,000.00) by ₹7,000.00 (14%). This exceeds the configured tolerance threshold of ₹500.00."*
  - Automatically routes to the **Human Review Queue**.

---

### Scenario 4: Edge Case 3 — Missing Critical Information (Pending Review)
- **Document:** `data/sample_invoices/invoice_104_techcorp_missing_po.pdf`
- **Context:** TechCorp invoice for ₹45,000 with the PO Number reference omitted.
- **Expected Outcome:** `PENDING REVIEW`
- **What to Observe:**
  - System identifies missing PO reference.
  - Controlled fallback examines open POs for TechCorp and finds candidate `PO-2024-004`.
  - Because human confirmation is required for missing critical metadata, the invoice is safely routed to the **Review Queue** rather than auto-approved.

---

### Scenario 5: Edge Case 4 — Scanned / Degraded Low-Quality Invoice (Pending Review)
- **Document:** `data/sample_invoices/invoice_105_bharat_scanned.pdf`
- **Context:** Bharat Security rasterized scan with character noise, low contrast, and blur.
- **Expected Outcome:** `PENDING REVIEW` (Stage 3 executes OCR fallback)
- **What to Observe:**
  - Stage 2 detects insufficient text ($<50$ characters).
  - Stage 3 triggers the OCR fallback engine.
  - Extraction mode is flagged as `ocr_fallback`.
  - Critical fields are marked with degraded confidence, triggering AP reviewer verification.

---

### Scenario 6: Human Reviewer Resolution Workflow
- Navigate to **📋 Human Review Queue**.
- Select the Apex Cloud mismatch invoice (`INV-2024-AC55`).
- View the original document preview on the left alongside the extracted discrepancy breakdown.
- Enter reviewer notes: *"Spoke with IT Director; additional compute cluster was authorized under emergency change order. Approved."*
- Click **✅ Manually Approve**.
- Observe: Status updates to `MANUALLY_APPROVED`, the audit event is logged, and the original automated decision `PENDING REVIEW` is preserved.

---

## 8. Business Rules Configuration (`config/rules.yaml`)

All financial thresholds and precedence policies are centralized in `config/rules.yaml`:
```yaml
tolerances:
  amount_tolerance_percentage: 0.02  # 2%
  amount_tolerance_cap: 500.0        # ₹500 cap
  tax_tolerance_percentage: 0.01     # 1%
  tax_tolerance_cap: 100.0           # ₹100 cap

decision_policy:
  duplicate_action: "REJECTED"
  unapproved_vendor_action: "REJECTED"
  inactive_vendor_action: "REJECTED"
  amount_mismatch_action: "PENDING REVIEW"
  missing_fields_action: "PENDING REVIEW"
  low_confidence_action: "PENDING REVIEW"
  ambiguous_po_action: "PENDING REVIEW"

mandatory_fields:
  - invoice_number
  - invoice_date
  - vendor_name
  - invoice_total
```

---

## 9. Design Choices & Known Limitations

1. **Deterministic vs. LLM Extraction**: Both are supported. If an API key is absent, the system uses deterministic regex and layout extraction so it functions reliably offline in any testing environment.
2. **Decimal Financial Arithmetic**: All financial comparisons use `decimal.Decimal` to avoid floating-point rounding errors.
3. **No Split PO Allocation**: In accordance with the prompt guidelines for this MVP, an invoice is matched to a single primary PO rather than allocated across multiple POs.
4. **Bank Account Isolation**: The platform deliberately never initiates banking payments or edits vendor bank coordinates, isolating AP decisioning from banking operations.
