# InvoiceIQ Synthetic Test Dataset

This directory contains synthetic enterprise master datasets and realistic test invoice PDF documents designed to evaluate the InvoiceIQ AP Decision Automation platform against real-world Accounts Payable scenarios.

All data, vendor identities, tax IDs, and transaction amounts are entirely synthetic.

---

## 1. Master Datasets

### A. Vendor Master (`data/vendors.csv`)
- **VEND-001**: TechCorp Solutions Private Limited (GSTIN: `27AABCT1234A1Z5`) — Status: `ACTIVE`, Approved: `True`
- **VEND-002**: Apex Cloud Infrastructure LLC (GSTIN: `29AAACA5678B2Z1`) — Status: `ACTIVE`, Approved: `True`
- **VEND-003**: GreenLogistics Global Services Inc (GSTIN: `07AAACG9876C1Z3`) — Status: `ACTIVE`, Approved: `True`
- **VEND-004**: Quantum Office Supplies Private Limited (GSTIN: `33AAACQ4321D1Z9`) — Status: `INACTIVE`, Approved: `False` (Unapproved / Inactive vendor)
- **VEND-005**: Bharat Security Systems & Automation (GSTIN: `06AAACB1122E1Z4`) — Status: `ACTIVE`, Approved: `True`
- **VEND-006**: Synergy Digital Consulting Labs (GSTIN: `24AAACS9988F1Z8`) — Status: `ACTIVE`, Approved: `True`

### B. Purchase Orders Master (`data/purchase_orders.csv`)
- **PO-2024-001**: VEND-001 | INR 125,000.00 | Status: `OPEN` (Cloud Server Hosting & Firewall)
- **PO-2024-002**: VEND-002 | INR 50,000.00 | Status: `OPEN` (High-Performance Compute Cluster)
- **PO-2024-003**: VEND-003 | INR 84,000.00 | Status: `OPEN` (Cold Chain Freight)
- **PO-2024-004**: VEND-001 | INR 45,000.00 | Status: `OPEN` (Software Architecture Sprint)
- **PO-2024-005**: VEND-005 | INR 62,000.00 | Status: `OPEN` (Biometric Terminals & Installation)
- **PO-2024-006**: VEND-006 | INR 110,000.00 | Status: `OPEN` (Fullstack Engineering + Security Audit)
- **PO-2024-007**: VEND-004 | INR 30,000.00 | Status: `CLOSED` (Office Furniture - Inactive Vendor)
- **PO-2024-008**: VEND-002 | INR 20,000.00 | Status: `CLOSED` (Exhausted balance: INR 0.00)

---

## 2. Sample Invoices (`data/sample_invoices/`)

| File Name | Vendor | PO Reference | Invoice Amount | Expected Outcome | Rationale & Policy Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `invoice_101_techcorp_happy_path.pdf` | TechCorp Solutions | `PO-2024-001` | ₹125,000.00 | **APPROVED** | Clean 3-way match. Active approved vendor, exact PO match, 0 variance, line items reconciled. |
| `invoice_102_greenlogistics_original.pdf` | GreenLogistics Global | `PO-2024-003` | ₹84,000.00 | **APPROVED** | First submission of logistics freight invoice. Commits record to database. |
| `invoice_102_greenlogistics_duplicate_renamed.pdf` | GreenLogistics Global | `PO-2024-003` | ₹84,000.00 | **REJECTED** | **Edge Case 1 (Duplicate)**: Same invoice submitted under a renamed filename. Matches vendor + invoice number and content hash. |
| `invoice_103_apex_amount_mismatch.pdf` | Apex Cloud | `PO-2024-002` | ₹57,000.00 | **PENDING REVIEW** | **Edge Case 2 (Amount Mismatch)**: PO commitment is ₹50,000; invoice is ₹57,000. Variance = ₹7,000 (14%), exceeding tolerance (2% capped at ₹500). |
| `invoice_104_techcorp_missing_po.pdf` | TechCorp Solutions | *[Missing]* | ₹45,000.00 | **PENDING REVIEW** | **Edge Case 3 (Missing Information)**: PO reference omitted from invoice. Controlled fallback identifies candidate PO-2024-004; routed to AP reviewer for verification. |
| `invoice_105_bharat_scanned.pdf` | Bharat Security Systems | `PO-2024-005` | ₹62,000.00 | **PENDING REVIEW** | **Edge Case 4 (Scanned Document)**: Degraded raster scan. Triggers OCR fallback engine. Flagged for review due to scan degradation and manual verification requirement. |
| `invoice_106_synergy_consulting.pdf` | Synergy Digital Labs | `PO-2024-006` | ₹110,000.00 | **APPROVED** | Multi-line IT consulting services (80 hrs engineering @ ₹1,000 + Security Audit ₹30,000). Clean match. |
| `invoice_107_quantum_unapproved_vendor.pdf` | Quantum Office Supplies | `PO-2024-007` | ₹30,000.00 | **REJECTED** | Vendor is marked `INACTIVE` with `approved_flag=False` in Vendor Master. Hard policy rejection. |

---

## 3. Re-generating Sample Files

To regenerate all PDF invoices with fresh timestamps or styles, run:
```bash
python data/generate_sample_invoices.py
```
