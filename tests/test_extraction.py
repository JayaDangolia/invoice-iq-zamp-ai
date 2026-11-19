import pytest
from pathlib import Path
from decimal import Decimal
from services.pdf_reader import PDFReaderService
from services.ocr_service import OCRService
from services.extraction_service import ExtractionService
from config.settings import SAMPLE_INVOICES_DIR

def test_pdf_reader_text_and_hash():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_101_techcorp_happy_path.pdf"
    assert pdf_path.exists(), "Sample invoice must exist"

    file_bytes = pdf_path.read_bytes()
    reader = PDFReaderService()
    
    file_hash = reader.calculate_file_hash(file_bytes)
    assert len(file_hash) == 64
    
    res = reader.inspect_and_extract_text(file_bytes)
    assert res["page_count"] == 1
    assert "TechCorp Solutions" in res["full_text"]
    assert res["needs_ocr"] is False
    assert res["char_count"] > 100

def test_ocr_service_scanned_pdf():
    pdf_path = SAMPLE_INVOICES_DIR / "invoice_105_bharat_scanned.pdf"
    assert pdf_path.exists()

    file_bytes = pdf_path.read_bytes()
    reader = PDFReaderService(min_text_threshold=100)
    res = reader.inspect_and_extract_text(file_bytes)
    assert res["needs_ocr"] is True

    ocr = OCRService()
    ocr_res = ocr.process_scanned_pdf(file_bytes)
    assert "ocr_text" in ocr_res
    assert len(ocr_res["ocr_text"]) > 20
    assert ocr_res["confidence"] > 0.50
    assert "Bharat" in ocr_res["ocr_text"]

def test_deterministic_extraction():
    extractor = ExtractionService()
    sample_text = """
    TAX INVOICE
    TechCorp Solutions Private Limited
    Tax ID / GSTIN: 27AABCT1234A1Z5
    Invoice No: INV-2024-998
    Invoice Date: 2024-10-15
    PO Number: PO-2024-001
    
    Item Description Qty Unit Price (INR) Line Total (INR)
    Cloud Hosting 1 100000.00 100000.00
    
    Subtotal: INR 100,000.00
    Total Tax (GST): INR 18,000.00
    Total Amount: INR 118,000.00
    """
    data = extractor.extract(sample_text)
    assert data.vendor_name is not None
    assert "TechCorp" in data.vendor_name
    assert data.vendor_tax_id == "27AABCT1234A1Z5"
    assert data.invoice_number == "INV-2024-998"
    assert data.invoice_date == "2024-10-15"
    assert data.po_number == "PO-2024-001"
    assert data.invoice_total == Decimal("118000.00")
    assert data.extraction_mode in ("deterministic", "gemini_llm")

def test_empty_text_handling():
    extractor = ExtractionService()
    data = extractor.extract("")
    assert data.vendor_name is None
    assert data.invoice_number is None
    assert data.invoice_total is None
