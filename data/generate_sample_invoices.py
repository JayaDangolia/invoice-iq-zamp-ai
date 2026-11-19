import io
import os
from pathlib import Path
from decimal import Decimal
from PIL import Image, ImageFilter, ImageEnhance
import pymupdf
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = Path(__file__).resolve().parent / "sample_invoices"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_invoice_pdf(
    filename: str,
    vendor_name: str,
    vendor_tax_id: str,
    vendor_address: str,
    invoice_number: str,
    invoice_date: str,
    po_number: str,
    items: list,
    subtotal: float,
    tax: float,
    total: float,
    currency: str = "INR",
    is_scanned: bool = False
) -> Path:
    pdf_path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'VendorHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=2,  # Right
        textColor=colors.HexColor('#1E293B')
    )

    elements = []

    # Header Row: Vendor details on left, Invoice title & metadata on right
    vendor_details = f"""
    <b>{vendor_name}</b><br/>
    Tax ID / GSTIN: {vendor_tax_id}<br/>
    {vendor_address}
    """
    
    inv_meta = f"""
    <b>TAX INVOICE</b><br/>
    <b>Invoice No:</b> {invoice_number if invoice_number else 'N/A'}<br/>
    <b>Invoice Date:</b> {invoice_date if invoice_date else 'N/A'}<br/>
    <b>PO Number:</b> {po_number if po_number else 'N/A'}<br/>
    <b>Currency:</b> {currency}
    """

    header_table = Table([
        [Paragraph(vendor_details, meta_style), Paragraph(inv_meta, meta_style)]
    ], colWidths=[3.5 * inch, 3.5 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=15))

    # Bill To
    bill_to_text = """
    <b>BILLED TO:</b><br/>
    Acme Global Enterprises India Pvt Ltd<br/>
    Tower 4, Cyber City, Phase III, Gurugram, Haryana - 122002<br/>
    GSTIN: 07AABCA9999Z1Z8
    """
    elements.append(Paragraph(bill_to_text, meta_style))
    elements.append(Spacer(1, 15))

    # Line Items Table
    table_data = [["Item Description", "Qty", "Unit Price (INR)", "Line Total (INR)"]]
    for item in items:
        table_data.append([
            item["desc"],
            str(item["qty"]),
            f"{item['price']:,.2f}",
            f"{item['total']:,.2f}"
        ])

    table = Table(table_data, colWidths=[3.5 * inch, 0.8 * inch, 1.4 * inch, 1.3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 15))

    # Totals Summary Table
    totals_data = [
        ["Subtotal:", f"INR {subtotal:,.2f}"],
        ["Total Tax (GST):", f"INR {tax:,.2f}"],
        ["Total Amount:", f"INR {total:,.2f}"]
    ]
    totals_table = Table(totals_data, colWidths=[5.5 * inch, 1.5 * inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 1), 'Helvetica'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 2), 10),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.HexColor('#0F172A')),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#CBD5E1')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 25))

    # Notes & Payment Details
    footer_text = """
    <b>Payment Terms:</b> Net 30 Days. Please remit payment via NEFT/RTGS to HDFC Bank A/C 50200012345678 (IFSC: HDFC0000123).<br/>
    <i>This is a computer-generated tax invoice.</i>
    """
    elements.append(Paragraph(footer_text, meta_style))

    doc.build(elements)

    # If is_scanned is True, convert the generated PDF into an image-only degraded scanned PDF
    if is_scanned:
        _convert_to_scanned_pdf(pdf_path)

    return pdf_path

def _convert_to_scanned_pdf(pdf_path: Path):
    doc = pymupdf.open(str(pdf_path))
    page = doc[0]
    pix = page.get_pixmap(dpi=150)
    img_data = pix.tobytes("png")
    doc.close()

    # Apply degradation using Pillow
    img = Image.open(io.BytesIO(img_data)).convert("L")  # Grayscale
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Save as new single-page image-only PDF
    scanned_doc = pymupdf.open()
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format="JPEG", quality=45)
    img_bytes = img_bytes_io.getvalue()

    rect = pymupdf.Rect(0, 0, pix.width * 72 / 150, pix.height * 72 / 150)
    scanned_page = scanned_doc.new_page(width=rect.width, height=rect.height)
    scanned_page.insert_image(rect, stream=img_bytes)
    scanned_doc.save(str(pdf_path))
    scanned_doc.close()

def generate_all_samples():
    print("Generating synthetic sample invoices...")

    # 1. Clean Happy-Path Invoice
    create_invoice_pdf(
        filename="invoice_101_techcorp_happy_path.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-2024-001",
        invoice_date="2024-10-02",
        po_number="PO-2024-001",
        items=[
            {"desc": "Enterprise Cloud Server Hosting Annual Tier-1", "qty": 1, "price": 100000.00, "total": 100000.00},
            {"desc": "Managed Firewall & DDoS Shield Protection", "qty": 1, "price": 25000.00, "total": 25000.00}
        ],
        subtotal=125000.00,
        tax=0.00,
        total=125000.00
    )

    # 2. Duplicate Invoices (Edge Case 1)
    # Submission A: Original
    create_invoice_pdf(
        filename="invoice_102_greenlogistics_original.pdf",
        vendor_name="GreenLogistics Global Services Inc",
        vendor_tax_id="07AAACG9876C1Z3",
        vendor_address="Cargo Complex, IGI Airport Terminal 2, New Delhi - 110037",
        invoice_number="INV-2024-GL08",
        invoice_date="2024-10-11",
        po_number="PO-2024-003",
        items=[
            {"desc": "Cold Chain Freight & Logistics Services", "qty": 2, "price": 35000.00, "total": 70000.00}
        ],
        subtotal=70000.00,
        tax=14000.00,
        total=84000.00
    )
    # Submission B: Renamed duplicate file with identical content & invoice identity
    create_invoice_pdf(
        filename="invoice_102_greenlogistics_duplicate_renamed.pdf",
        vendor_name="GreenLogistics Global Services Inc",
        vendor_tax_id="07AAACG9876C1Z3",
        vendor_address="Cargo Complex, IGI Airport Terminal 2, New Delhi - 110037",
        invoice_number="INV-2024-GL08",
        invoice_date="2024-10-11",
        po_number="PO-2024-003",
        items=[
            {"desc": "Cold Chain Freight & Logistics Services", "qty": 2, "price": 35000.00, "total": 70000.00}
        ],
        subtotal=70000.00,
        tax=14000.00,
        total=84000.00
    )

    # 3. Amount Mismatch Invoice (Edge Case 2)
    # PO is ₹50,000, invoice is ₹57,000 (Variance ₹7,000 = 14%)
    create_invoice_pdf(
        filename="invoice_103_apex_amount_mismatch.pdf",
        vendor_name="Apex Cloud Infrastructure LLC",
        vendor_tax_id="29AAACA5678B2Z1",
        vendor_address="Plot 12, Electronic City Phase 1, Bengaluru, Karnataka - 560100",
        invoice_number="INV-2024-AC55",
        invoice_date="2024-10-06",
        po_number="PO-2024-002",
        items=[
            {"desc": "High-Performance Compute Cluster - Tier B", "qty": 1, "price": 57000.00, "total": 57000.00}
        ],
        subtotal=57000.00,
        tax=0.00,
        total=57000.00
    )

    # 4. Missing Information Invoice (Edge Case 3)
    # Missing PO reference
    create_invoice_pdf(
        filename="invoice_104_techcorp_missing_po.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-2024-004",
        invoice_date="2024-10-13",
        po_number="",  # Intentionally missing PO reference
        items=[
            {"desc": "Software Architecture Consulting Sprint", "qty": 1, "price": 45000.00, "total": 45000.00}
        ],
        subtotal=45000.00,
        tax=0.00,
        total=45000.00
    )

    # 5. Scanned / Low-Quality Invoice (Edge Case 4)
    # Pure bitmap image with degraded contrast and character artifacts
    create_invoice_pdf(
        filename="invoice_105_bharat_scanned.pdf",
        vendor_name="Bharat Security Systems & Automation",
        vendor_tax_id="06AAACB1122E1Z4",
        vendor_address="Industrial Area Phase 2, Manesar, Gurugram, Haryana - 122051",
        invoice_number="INV-2024-SC99",
        invoice_date="2024-10-16",
        po_number="PO-2024-005",
        items=[
            {"desc": "Biometric Access Terminals & Installation", "qty": 2, "price": 25000.00, "total": 50000.00}
        ],
        subtotal=50000.00,
        tax=12000.00,
        total=62000.00,
        is_scanned=True
    )

    # 6. Additional Realistic Multi-Line IT Consulting Invoice
    create_invoice_pdf(
        filename="invoice_106_synergy_consulting.pdf",
        vendor_name="Synergy Digital Consulting Labs",
        vendor_tax_id="24AAACS9988F1Z8",
        vendor_address="Infocity Tower B, Gandhinagar, Gujarat - 382007",
        invoice_number="INV-2024-SYN88",
        invoice_date="2024-10-19",
        po_number="PO-2024-006",
        items=[
            {"desc": "Fullstack Engineering Support - 80 Hours", "qty": 80, "price": 1000.00, "total": 80000.00},
            {"desc": "Cloud Security Audit & Review Report", "qty": 1, "price": 30000.00, "total": 30000.00}
        ],
        subtotal=110000.00,
        tax=0.00,
        total=110000.00
    )

    # 7. Unapproved / Inactive Vendor Invoice (Tests strict policy rejection)
    create_invoice_pdf(
        filename="invoice_107_quantum_unapproved_vendor.pdf",
        vendor_name="Quantum Office Supplies Private Limited",
        vendor_tax_id="33AAACQ4321D1Z9",
        vendor_address="Guindy Industrial Estate, Chennai, Tamil Nadu - 600032",
        invoice_number="INV-2024-QNT10",
        invoice_date="2024-09-02",
        po_number="PO-2024-007",
        items=[
            {"desc": "Ergonomic Executive Office Chairs", "qty": 10, "price": 3000.00, "total": 30000.00}
        ],
        subtotal=30000.00,
        tax=0.00,
        total=30000.00
    )

    # -------------------------------------------------------------
    # EDGE CASE 2: PARTIAL / SPLIT PO BILLING (PS-1 Requirement)
    # Master PO is PO-2024-009 (₹1,00,000.00 total)
    # -------------------------------------------------------------
    # 8. Split PO Part 1: ₹40,000 (Milestone 1)
    create_invoice_pdf(
        filename="invoice_201_techcorp_split_po_part1.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-SPLIT-001",
        invoice_date="2024-10-21",
        po_number="PO-2024-009",
        items=[
            {"desc": "Milestone 1 — Cloud Architecture Design", "qty": 1, "price": 40000.00, "total": 40000.00}
        ],
        subtotal=40000.00,
        tax=0.00,
        total=40000.00
    )

    # 9. Split PO Part 2: ₹35,000 (Milestone 2)
    create_invoice_pdf(
        filename="invoice_202_techcorp_split_po_part2.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-SPLIT-002",
        invoice_date="2024-10-25",
        po_number="PO-2024-009",
        items=[
            {"desc": "Milestone 2 — Infrastructure Implementation", "qty": 1, "price": 35000.00, "total": 35000.00}
        ],
        subtotal=35000.00,
        tax=0.00,
        total=35000.00
    )

    # 10. Split PO Part 3: ₹25,000 (Milestone 3, exhausting PO-2024-009)
    create_invoice_pdf(
        filename="invoice_203_techcorp_split_po_part3.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-SPLIT-003",
        invoice_date="2024-10-28",
        po_number="PO-2024-009",
        items=[
            {"desc": "Milestone 3 — UAT & System Handover", "qty": 1, "price": 25000.00, "total": 25000.00}
        ],
        subtotal=25000.00,
        tax=0.00,
        total=25000.00
    )

    # 11. Split PO Part 4: ₹15,000 (Exceeds remaining PO balance of ₹0.00)
    create_invoice_pdf(
        filename="invoice_204_techcorp_split_po_exceeded.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-SPLIT-004",
        invoice_date="2024-11-01",
        po_number="PO-2024-009",
        items=[
            {"desc": "Additional Post-Handover Engineering Support Sprint", "qty": 1, "price": 15000.00, "total": 15000.00}
        ],
        subtotal=15000.00,
        tax=0.00,
        total=15000.00
    )

    # 12. Ambiguous PO Reference Invoice (Edge Case 3)
    create_invoice_pdf(
        filename="invoice_205_techcorp_ambiguous_po.pdf",
        vendor_name="TechCorp Solutions Private Limited",
        vendor_tax_id="27AABCT1234A1Z5",
        vendor_address="Level 5, Tech Park, Andheri East, Mumbai, Maharashtra - 400069",
        invoice_number="INV-2024-AMB01",
        invoice_date="2024-10-30",
        po_number="",  # Omitted PO reference
        items=[
            {"desc": "Cloud Migration Technical Support Services", "qty": 1, "price": 50000.00, "total": 50000.00}
        ],
        subtotal=50000.00,
        tax=0.00,
        total=50000.00
    )

    print("All sample invoices generated successfully in data/sample_invoices/")

if __name__ == "__main__":
    generate_all_samples()
