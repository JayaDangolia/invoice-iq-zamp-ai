"""Custom exceptions for the InvoiceIQ platform."""

class InvoiceIQException(Exception):
    """Base exception for all InvoiceIQ processing errors."""
    pass

class ExtractionError(InvoiceIQException):
    """Raised when text or structured extraction fails."""
    pass

class OCRError(InvoiceIQException):
    """Raised when OCR fallback processing fails."""
    pass

class VendorValidationError(InvoiceIQException):
    """Raised when vendor verification encounters an unrecoverable error."""
    pass

class DuplicateInvoiceError(InvoiceIQException):
    """Raised when duplicate detection encounters an unrecoverable error."""
    pass

class POMatchingError(InvoiceIQException):
    """Raised when PO matching encounters an unrecoverable error."""
    pass

class ReconciliationError(InvoiceIQException):
    """Raised when financial reconciliation encounters a calculation failure."""
    pass

class DecisionEngineError(InvoiceIQException):
    """Raised when decision evaluation fails."""
    pass
