import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from core.models import (
    StageStatus,
    StageLog,
    ExtractedInvoiceData,
    VendorValidationResult,
    DuplicateDetectionResult,
    POMatchingResult,
    ReconciliationResult,
    DecisionResult,
)
from services.pdf_reader import PDFReaderService
from services.ocr_service import OCRService
from services.extraction_service import ExtractionService
from services.vendor_service import VendorService
from services.duplicate_service import DuplicateDetectionService
from services.po_matching_service import POMatchingService
from services.reconciliation_service import ReconciliationService
from services.decision_engine import DecisionEngine
from services.audit_service import AuditService
from database.repository import InvoiceRepository

class WorkflowOrchestrator:
    def __init__(
        self,
        repository: Optional[InvoiceRepository] = None,
        audit_service: Optional[AuditService] = None,
    ):
        self.repository = repository or InvoiceRepository()
        self.audit_service = audit_service or AuditService(self.repository)
        self.pdf_reader = PDFReaderService()
        self.ocr_service = OCRService()
        self.extraction_service = ExtractionService()
        self.vendor_service = VendorService()
        self.duplicate_service = DuplicateDetectionService(self.repository)
        self.po_matching_service = POMatchingService(repository=self.repository)
        self.reconciliation_service = ReconciliationService()
        self.decision_engine = DecisionEngine()

    def execute_workflow(
        self,
        file_bytes: bytes,
        filename: str,
        stage_callback: Optional[Callable[[StageLog, List[StageLog]], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute the complete 11-stage invoice processing pipeline.
        Emits live stage updates via stage_callback if provided.
        """
        overall_start = time.perf_counter()
        run_id = f"RUN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        stage_definitions = [
            (1, "Document received"),
            (2, "PDF text extraction"),
            (3, "OCR fallback if required"),
            (4, "AI invoice data extraction"),
            (5, "Required field validation"),
            (6, "Vendor verification"),
            (7, "Duplicate detection"),
            (8, "Purchase order matching"),
            (9, "Financial reconciliation"),
            (10, "Decision generation"),
            (11, "Audit record saved"),
        ]

        stages_log: List[StageLog] = [
            StageLog(stage_id=s_id, stage_name=s_name, status=StageStatus.NOT_STARTED)
            for s_id, s_name in stage_definitions
        ]

        def _update_stage(stage_idx: int, status: StageStatus, message: str, details: Optional[Dict[str, Any]] = None, duration: float = 0.0):
            stages_log[stage_idx].status = status
            stages_log[stage_idx].message = message
            stages_log[stage_idx].duration_ms = round(duration * 1000, 2)
            stages_log[stage_idx].timestamp = datetime.now(timezone.utc).isoformat()
            if details:
                stages_log[stage_idx].details = details
            if stage_callback:
                stage_callback(stages_log[stage_idx], list(stages_log))

        # -------------------------------------------------------------
        # STAGE 1: Document Received
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(0, StageStatus.RUNNING, "Receiving document and generating security hash...")
        file_hash = self.pdf_reader.calculate_file_hash(file_bytes)
        file_size_bytes = len(file_bytes)
        self.audit_service.record_event(
            run_id, "WORKFLOW_INITIALIZED", "SYSTEM",
            {"filename": filename, "file_size_bytes": file_size_bytes, "file_hash": file_hash}
        )
        t_dur = time.perf_counter() - t0
        _update_stage(0, StageStatus.SUCCESS, f"Received {file_size_bytes:,} bytes. SHA-256 hash computed.", {"file_hash": file_hash}, t_dur)

        # -------------------------------------------------------------
        # STAGE 2: PDF Text Extraction
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(1, StageStatus.RUNNING, "Extracting text layers from PDF document...")
        pdf_info = self.pdf_reader.inspect_and_extract_text(file_bytes)
        page_count = pdf_info["page_count"]
        extracted_text = pdf_info["full_text"]
        needs_ocr = pdf_info["needs_ocr"]
        t_dur = time.perf_counter() - t0
        _update_stage(
            1, StageStatus.SUCCESS,
            f"Extracted {pdf_info['char_count']} characters across {page_count} page(s).",
            {"page_count": page_count, "char_count": pdf_info["char_count"], "needs_ocr": needs_ocr},
            t_dur
        )

        # -------------------------------------------------------------
        # STAGE 3: OCR Fallback if Required
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        ocr_confidence = 1.0
        is_ocr_applied = False
        if needs_ocr:
            _update_stage(2, StageStatus.RUNNING, "Document is scanned / image-based. Executing OCR fallback...")
            ocr_result = self.ocr_service.process_scanned_pdf(file_bytes)
            extracted_text = ocr_result["ocr_text"]
            ocr_confidence = ocr_result["confidence"]
            is_ocr_applied = True
            t_dur = time.perf_counter() - t0
            _update_stage(
                2, StageStatus.SUCCESS,
                f"OCR completed via {ocr_result['engine_used']} (Confidence: {int(ocr_confidence*100)}%).",
                ocr_result,
                t_dur
            )
        else:
            t_dur = time.perf_counter() - t0
            _update_stage(2, StageStatus.SUCCESS, "Text extraction sufficient; OCR fallback not required.", {"ocr_skipped": True}, t_dur)

        # -------------------------------------------------------------
        # STAGE 4: AI Invoice Data Extraction
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(3, StageStatus.RUNNING, "Running structured information extraction...")
        extracted_data: ExtractedInvoiceData = self.extraction_service.extract(
            extracted_text, is_ocr=is_ocr_applied, ocr_confidence=ocr_confidence
        )
        t_dur = time.perf_counter() - t0
        _update_stage(
            3, StageStatus.SUCCESS,
            f"Extraction completed via {extracted_data.extraction_mode} mode. {len(extracted_data.line_items)} line item(s) found.",
            {
                "vendor_name": extracted_data.vendor_name,
                "invoice_number": extracted_data.invoice_number,
                "total": float(extracted_data.invoice_total or 0.0),
                "mode": extracted_data.extraction_mode,
            },
            t_dur
        )

        # -------------------------------------------------------------
        # STAGE 5: Required Field Validation
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(4, StageStatus.RUNNING, "Validating presence of mandatory invoice metadata...")
        missing_fields = []
        if not extracted_data.invoice_number:
            missing_fields.append("invoice_number")
        if not extracted_data.invoice_date:
            missing_fields.append("invoice_date")
        if not extracted_data.vendor_name:
            missing_fields.append("vendor_name")
        if extracted_data.invoice_total is None:
            missing_fields.append("invoice_total")

        t_dur = time.perf_counter() - t0
        if missing_fields:
            _update_stage(
                4, StageStatus.WARNING,
                f"Missing critical metadata: {', '.join(missing_fields)}.",
                {"missing": missing_fields},
                t_dur
            )
        else:
            _update_stage(4, StageStatus.SUCCESS, "All mandatory invoice fields present and validated.", {}, t_dur)

        # -------------------------------------------------------------
        # STAGE 6: Vendor Verification
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(5, StageStatus.RUNNING, "Verifying vendor against Vendor Master records...")
        vendor_res: VendorValidationResult = self.vendor_service.verify_vendor(
            extracted_name=extracted_data.vendor_name,
            extracted_tax_id=extracted_data.vendor_tax_id
        )
        t_dur = time.perf_counter() - t0
        if vendor_res.is_verified and vendor_res.is_approved:
            _update_stage(
                5, StageStatus.SUCCESS,
                f"Vendor verified: {vendor_res.legal_name} (ID: {vendor_res.vendor_id}). Status: ACTIVE.",
                vendor_res.model_dump(),
                t_dur
            )
        elif vendor_res.is_verified and not vendor_res.is_approved:
            _update_stage(
                5, StageStatus.WARNING,
                f"Vendor [{vendor_res.vendor_id}] is {vendor_res.status} or unapproved.",
                vendor_res.model_dump(),
                t_dur
            )
        else:
            _update_stage(
                5, StageStatus.WARNING,
                f"Vendor verification failed: {vendor_res.notes}",
                vendor_res.model_dump(),
                t_dur
            )

        # -------------------------------------------------------------
        # STAGE 7: Duplicate Detection
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(6, StageStatus.RUNNING, "Checking for prior duplicate submissions...")
        dup_res: DuplicateDetectionResult = self.duplicate_service.check_duplicate(
            file_hash=file_hash,
            vendor_id=vendor_res.vendor_id,
            invoice_number=extracted_data.invoice_number,
            current_run_id=run_id
        )
        t_dur = time.perf_counter() - t0
        if dup_res.is_duplicate:
            _update_stage(
                6, StageStatus.WARNING,
                f"DUPLICATE DETECTED! Matched prior run {dup_res.prior_run_id} ({dup_res.match_type}).",
                dup_res.model_dump(),
                t_dur
            )
        else:
            _update_stage(6, StageStatus.SUCCESS, "No duplicate submission detected in database records.", {}, t_dur)

        # -------------------------------------------------------------
        # STAGE 8: Purchase Order Matching
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(7, StageStatus.RUNNING, "Matching Purchase Order reference and line items...")
        po_res: POMatchingResult = self.po_matching_service.match_po(
            extracted_po_number=extracted_data.po_number,
            verified_vendor_id=vendor_res.vendor_id,
            invoice_total=extracted_data.invoice_total,
            line_items=extracted_data.line_items,
            currency=extracted_data.currency or "INR"
        )
        t_dur = time.perf_counter() - t0
        if po_res.is_matched:
            if po_res.is_partial_invoice:
                msg = f"PO matched: [{po_res.po_number}] (Partial invoice: Prior billed ₹{po_res.cumulative_billed_amount:,.2f}, Remaining balance ₹{po_res.dynamic_remaining_balance:,.2f})."
            else:
                msg = f"PO matched: [{po_res.po_number}] (Status: {po_res.po_status}, Full commitment: ₹{po_res.po_total:,.2f})."
            _update_stage(7, StageStatus.SUCCESS, msg, po_res.model_dump(), t_dur)
        else:
            _update_stage(
                7, StageStatus.WARNING,
                f"PO matching: {po_res.notes}",
                po_res.model_dump(),
                t_dur
            )

        # -------------------------------------------------------------
        # STAGE 9: Financial Reconciliation
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(8, StageStatus.RUNNING, "Calculating financial variances and tolerance limits...")
        recon_res: ReconciliationResult = self.reconciliation_service.reconcile(
            extracted=extracted_data,
            po_match=po_res
        )
        t_dur = time.perf_counter() - t0
        if recon_res.within_tolerance and recon_res.is_arithmetic_consistent:
            if recon_res.is_partial_invoice:
                msg = f"Partial billing within limits: ₹{recon_res.invoice_total:,.2f} billed against available ₹{recon_res.remaining_balance_before:,.2f} (Remaining balance after invoice: ₹{recon_res.remaining_balance_after:,.2f})."
            else:
                msg = f"Reconciliation passed cleanly. Variance: ₹{recon_res.variance_amount:,.2f} ({recon_res.variance_pct}%)."
            _update_stage(8, StageStatus.SUCCESS, msg, recon_res.model_dump(), t_dur)
        else:
            _update_stage(
                8, StageStatus.WARNING,
                f"Reconciliation flag: {recon_res.notes}",
                recon_res.model_dump(),
                t_dur
            )

        # -------------------------------------------------------------
        # STAGE 10: Decision Generation
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(9, StageStatus.RUNNING, "Evaluating AP decision policy precedence...")
        decision_res: DecisionResult = self.decision_engine.evaluate(
            extracted=extracted_data,
            vendor=vendor_res,
            duplicate=dup_res,
            po_match=po_res,
            recon=recon_res
        )
        t_dur = time.perf_counter() - t0
        _update_stage(
            9, StageStatus.SUCCESS,
            f"Decision finalized: {decision_res.decision.value} (Reason: {decision_res.reason_code}).",
            decision_res.model_dump(),
            t_dur
        )

        # -------------------------------------------------------------
        # STAGE 11: Audit Record Saved
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        _update_stage(10, StageStatus.RUNNING, "Persisting run records and immutable audit trail...")
        overall_duration_ms = round((time.perf_counter() - overall_start) * 1000, 2)

        run_record = {
            "run_id": run_id,
            "filename": filename,
            "file_hash": file_hash,
            "file_size_bytes": file_size_bytes,
            "page_count": page_count,
            "invoice_number": extracted_data.invoice_number,
            "invoice_date": extracted_data.invoice_date,
            "vendor_id": vendor_res.vendor_id,
            "vendor_name": vendor_res.legal_name or extracted_data.vendor_name,
            "po_number": po_res.po_number or extracted_data.po_number,
            "invoice_total": float(extracted_data.invoice_total or 0.0),
            "currency": extracted_data.currency or "INR",
            "extraction_mode": extracted_data.extraction_mode,
            "decision": decision_res.decision.value,
            "reason_code": decision_res.reason_code,
            "explanation": decision_res.explanation,
            "recommended_action": decision_res.recommended_action,
            "stages_log": [s.model_dump() for s in stages_log],
            "extracted_data": extracted_data.model_dump(),
            "vendor_result": vendor_res.model_dump(),
            "duplicate_result": dup_res.model_dump(),
            "po_result": po_res.model_dump(),
            "reconciliation_result": recon_res.model_dump(),
            "decision_result": decision_res.model_dump(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "duration_ms": overall_duration_ms,
            "status": "COMPLETED",
        }

        self.repository.save_run(run_record)
        self.audit_service.record_event(
            run_id=run_id,
            event_type="DECISION_COMMITTED",
            actor="SYSTEM",
            details={
                "decision": decision_res.decision.value,
                "reason_code": decision_res.reason_code,
                "invoice_total": float(extracted_data.invoice_total or 0.0),
                "duration_ms": overall_duration_ms
            }
        )
        t_dur = time.perf_counter() - t0
        _update_stage(10, StageStatus.SUCCESS, f"Run [{run_id}] and audit events successfully committed to SQLite.", {}, t_dur)

        # Update final run_record with the finished stages_log
        run_record["stages_log"] = [s.model_dump() for s in stages_log]
        self.repository.save_run(run_record)

        return run_record
