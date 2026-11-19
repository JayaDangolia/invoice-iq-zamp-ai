from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class DecisionOutcome(str, Enum):
    APPROVED = "APPROVED"
    PENDING_REVIEW = "PENDING REVIEW"
    REJECTED = "REJECTED"

class StageStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    FAILED = "FAILED"

class StageLog(BaseModel):
    stage_id: int
    stage_name: str
    status: StageStatus = StageStatus.NOT_STARTED
    message: str = ""
    duration_ms: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = ""

class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    line_total: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    confidence: float = 1.0

    model_config = ConfigDict(arbitrary_types_allowed=True)

class ExtractedInvoiceData(BaseModel):
    vendor_name: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    po_number: Optional[str] = None
    currency: Optional[str] = None
    line_items: List[LineItem] = Field(default_factory=list)
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    invoice_total: Optional[Decimal] = None
    base_amount: Optional[Decimal] = None
    is_tax_embedded: bool = False
    is_tax_separate: bool = True
    is_bundled_line_items: bool = False
    extraction_evidence: Dict[str, Any] = Field(default_factory=dict)
    extraction_mode: str = "deterministic"  # "llm", "deterministic", "ocr_fallback"
    ocr_applied: bool = False
    raw_text_snippet: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

class VendorRecord(BaseModel):
    vendor_id: str
    legal_name: str
    normalized_name: str
    tax_id: str
    status: str
    approved_flag: bool

class VendorValidationResult(BaseModel):
    is_verified: bool = False
    vendor_id: Optional[str] = None
    legal_name: Optional[str] = None
    status: Optional[str] = None
    is_approved: bool = False
    match_type: str = "NONE"  # "EXACT_TAX_ID", "EXACT_NAME", "NORMALIZED_NAME", "FUZZY_NAME", "NONE"
    match_confidence: float = 0.0
    notes: str = ""
    warnings: List[str] = Field(default_factory=list)

class DuplicateDetectionResult(BaseModel):
    is_duplicate: bool = False
    is_uncertain: bool = False
    match_type: str = "NONE"  # "EXACT_MATCH", "HASH_MATCH", "FUZZY_MATCH", "NONE"
    prior_invoice_id: Optional[str] = None
    prior_run_id: Optional[str] = None
    prior_submission_date: Optional[str] = None
    notes: str = ""
    confidence: float = 1.0

class POMatchingResult(BaseModel):
    is_matched: bool = False
    po_number: Optional[str] = None
    po_vendor_id: Optional[str] = None
    po_status: Optional[str] = None
    po_total: Optional[Decimal] = None
    remaining_balance: Optional[Decimal] = None
    initial_po_total: Optional[Decimal] = None
    cumulative_billed_amount: Decimal = Decimal("0.00")
    dynamic_remaining_balance: Decimal = Decimal("0.00")
    prior_accepted_invoices: List[Dict[str, Any]] = Field(default_factory=list)
    is_partial_invoice: bool = False
    currency: Optional[str] = None
    match_type: str = "NONE"  # "EXACT_PO_REF", "FALLBACK_CANDIDATE", "NONE", "AMBIGUOUS"
    candidate_po_count: int = 0
    candidate_pos: List[str] = Field(default_factory=list)
    candidate_po_details: List[Dict[str, Any]] = Field(default_factory=list)
    match_confidence: float = 0.0
    notes: str = ""
    line_matches: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)

class ReconciliationResult(BaseModel):
    invoice_total: Decimal = Decimal("0.00")
    po_applicable_amount: Decimal = Decimal("0.00")
    variance_amount: Decimal = Decimal("0.00")
    variance_pct: Decimal = Decimal("0.00")
    tolerance_threshold_amount: Decimal = Decimal("0.00")
    within_tolerance: bool = True
    tax_variance: Decimal = Decimal("0.00")
    is_partial_invoice: bool = False
    prior_billed_amount: Decimal = Decimal("0.00")
    remaining_balance_before: Decimal = Decimal("0.00")
    remaining_balance_after: Decimal = Decimal("0.00")
    exceeds_remaining_balance: bool = False
    is_tax_embedded: bool = False
    quantity_discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    line_item_discrepancies: List[Dict[str, Any]] = Field(default_factory=list)
    calculated_subtotal: Optional[Decimal] = None
    calculated_tax: Optional[Decimal] = None
    is_arithmetic_consistent: bool = True
    notes: str = ""

    model_config = ConfigDict(arbitrary_types_allowed=True)

class DecisionResult(BaseModel):
    decision: DecisionOutcome
    reason_code: str
    explanation: str
    passed_checks: List[str] = Field(default_factory=list)
    failed_checks: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommended_action: str
    decision_timestamp: str = ""

class AuditEvent(BaseModel):
    event_id: str
    run_id: str
    timestamp: str
    event_type: str
    actor: str  # "SYSTEM", "HUMAN_REVIEWER", "API"
    details: Dict[str, Any] = Field(default_factory=dict)
