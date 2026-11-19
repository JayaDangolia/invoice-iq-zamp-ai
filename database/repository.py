import json
import sqlite3
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from database.db import get_db_connection

class InvoiceRepository:
    def __init__(self):
        pass

    def save_run(self, run: Dict[str, Any]) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO invoice_runs (
            run_id, filename, file_hash, file_size_bytes, page_count,
            invoice_number, invoice_date, vendor_id, vendor_name, po_number,
            invoice_total, currency, extraction_mode, decision, reason_code,
            explanation, recommended_action, stages_log_json, extracted_data_json,
            vendor_result_json, duplicate_result_json, po_result_json,
            reconciliation_result_json, decision_result_json, created_at,
            duration_ms, status, reviewer_decision, reviewer_notes,
            reviewed_at, corrected_fields_json
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?,
            ?
        )
        """, (
            run.get("run_id"),
            run.get("filename"),
            run.get("file_hash"),
            run.get("file_size_bytes", 0),
            run.get("page_count", 1),
            run.get("invoice_number"),
            run.get("invoice_date"),
            run.get("vendor_id"),
            run.get("vendor_name"),
            run.get("po_number"),
            float(run.get("invoice_total") or 0.0),
            run.get("currency", "INR"),
            run.get("extraction_mode", "deterministic"),
            run.get("decision", "PENDING REVIEW"),
            run.get("reason_code", ""),
            run.get("explanation", ""),
            run.get("recommended_action", ""),
            json.dumps(run.get("stages_log", []), default=str),
            json.dumps(run.get("extracted_data", {}), default=str),
            json.dumps(run.get("vendor_result", {}), default=str),
            json.dumps(run.get("duplicate_result", {}), default=str),
            json.dumps(run.get("po_result", {}), default=str),
            json.dumps(run.get("reconciliation_result", {}), default=str),
            json.dumps(run.get("decision_result", {}), default=str),
            run.get("created_at", datetime.now(timezone.utc).isoformat()),
            float(run.get("duration_ms", 0.0)),
            run.get("status", "COMPLETED"),
            run.get("reviewer_decision"),
            run.get("reviewer_notes"),
            run.get("reviewed_at"),
            json.dumps(run.get("corrected_fields", {}), default=str)
        ))
        
        conn.commit()
        conn.close()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoice_runs WHERE run_id = ?", (run_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_dict(row)

    def find_duplicate_candidate(
        self, file_hash: str, vendor_id: Optional[str] = None, invoice_number: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check file hash match first (identical file content)
        if file_hash:
            cursor.execute(
                "SELECT * FROM invoice_runs WHERE file_hash = ? ORDER BY created_at ASC LIMIT 1",
                (file_hash,)
            )
            row = cursor.fetchone()
            if row:
                conn.close()
                d = self._row_to_dict(row)
                d["_duplicate_match_reason"] = "EXACT_FILE_HASH"
                return d

        # Check vendor + invoice_number match (same invoice identity, possibly renamed file)
        if vendor_id and invoice_number:
            normalized_inv = invoice_number.strip().upper()
            cursor.execute(
                """SELECT * FROM invoice_runs 
                   WHERE vendor_id = ? AND UPPER(TRIM(invoice_number)) = ?
                   ORDER BY created_at ASC LIMIT 1""",
                (vendor_id, normalized_inv)
            )
            row = cursor.fetchone()
            if row:
                conn.close()
                d = self._row_to_dict(row)
                d["_duplicate_match_reason"] = "VENDOR_AND_INVOICE_NUMBER"
                return d

        conn.close()
        return None

    def list_runs(
        self,
        decision_filter: Optional[str] = None,
        vendor_filter: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM invoice_runs WHERE 1=1"
        params: List[Any] = []

        if decision_filter and decision_filter != "ALL":
            query += " AND decision = ?"
            params.append(decision_filter)

        if vendor_filter and vendor_filter != "ALL":
            query += " AND (vendor_id = ? OR vendor_name LIKE ?)"
            params.append(vendor_filter)
            params.append(f"%{vendor_filter}%")

        if search_query:
            query += " AND (invoice_number LIKE ? OR run_id LIKE ? OR filename LIKE ? OR vendor_name LIKE ?)"
            like_term = f"%{search_query.strip()}%"
            params.extend([like_term, like_term, like_term, like_term])

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(r) for r in rows]

    def update_reviewer_action(
        self,
        run_id: str,
        reviewer_decision: str,
        reviewer_notes: str,
        corrected_fields: Optional[Dict[str, Any]] = None
    ) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
        UPDATE invoice_runs
        SET reviewer_decision = ?,
            reviewer_notes = ?,
            reviewed_at = ?,
            corrected_fields_json = ?
        WHERE run_id = ?
        """, (
            reviewer_decision,
            reviewer_notes,
            now_iso,
            json.dumps(corrected_fields or {}, default=str),
            run_id
        ))
        
        conn.commit()
        conn.close()

        # Record audit event
        self.log_audit_event(
            run_id=run_id,
            event_type="HUMAN_REVIEW_DECISION",
            actor="HUMAN_REVIEWER",
            details={
                "reviewer_decision": reviewer_decision,
                "notes": reviewer_notes,
                "corrected_fields": corrected_fields or {}
            }
        )

    def log_audit_event(
        self,
        run_id: str,
        event_type: str,
        actor: str,
        details: Optional[Dict[str, Any]] = None
    ) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        event_id = f"EVT-{uuid.uuid4().hex[:10].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        cursor.execute("""
        INSERT INTO audit_events (event_id, run_id, timestamp, event_type, actor, details_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            run_id,
            now_iso,
            event_type,
            actor,
            json.dumps(details or {}, default=str)
        ))
        
        conn.commit()
        conn.close()
        return event_id

    def get_audit_events(self, run_id: str) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM audit_events WHERE run_id = ? ORDER BY timestamp ASC",
            (run_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        events = []
        for r in rows:
            events.append({
                "event_id": r["event_id"],
                "run_id": r["run_id"],
                "timestamp": r["timestamp"],
                "event_type": r["event_type"],
                "actor": r["actor"],
                "details": json.loads(r["details_json"] or "{}")
            })
        return events

    def get_kpis(self) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM invoice_runs")
        total_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM invoice_runs WHERE decision = 'APPROVED'")
        approved_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM invoice_runs WHERE decision = 'PENDING REVIEW'")
        pending_review_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM invoice_runs WHERE decision = 'REJECTED'")
        rejected_count = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(duration_ms) FROM invoice_runs WHERE duration_ms > 0")
        avg_duration = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(invoice_total) FROM invoice_runs")
        total_vol = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(DISTINCT vendor_id) FROM invoice_runs WHERE vendor_id IS NOT NULL")
        distinct_vendors = cursor.fetchone()[0] or 0

        conn.close()
        return {
            "total_processed": total_count,
            "approved": approved_count,
            "pending_review": pending_review_count,
            "rejected": rejected_count,
            "avg_duration_ms": round(float(avg_duration), 2),
            "total_volume_inr": round(float(total_vol), 2),
            "distinct_vendors": distinct_vendors
        }

    def get_decision_volume_breakdown(self) -> Dict[str, float]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT decision, COALESCE(SUM(invoice_total), 0.0) as vol FROM invoice_runs GROUP BY decision")
        rows = cursor.fetchall()
        conn.close()
        res = {"APPROVED": 0.0, "PENDING REVIEW": 0.0, "REJECTED": 0.0}
        for r in rows:
            res[r["decision"]] = float(r["vol"])
        return res

    def get_kpi_sparkline_series(self) -> Dict[str, List[float]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT decision, invoice_total FROM invoice_runs ORDER BY created_at ASC")
        rows = cursor.fetchall()
        conn.close()

        tot_series = []
        app_series = []
        pen_series = []
        rej_series = []

        c_tot = 0
        c_app = 0
        c_pen = 0
        c_rej = 0

        for r in rows:
            c_tot += 1
            dec = (r["decision"] or "").upper()
            if dec == "APPROVED":
                c_app += 1
            elif dec == "PENDING REVIEW":
                c_pen += 1
            elif dec == "REJECTED":
                c_rej += 1

            tot_series.append(float(c_tot))
            app_series.append(float(c_app))
            pen_series.append(float(c_pen))
            rej_series.append(float(c_rej))

        return {
            "total": tot_series if tot_series else [0.0],
            "approved": app_series if app_series else [0.0],
            "pending": pen_series if pen_series else [0.0],
            "rejected": rej_series if rej_series else [0.0]
        }

    def get_decision_distribution(self) -> Dict[str, int]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT decision, COUNT(*) as cnt FROM invoice_runs GROUP BY decision")
        rows = cursor.fetchall()
        conn.close()
        dist = {"APPROVED": 0, "PENDING REVIEW": 0, "REJECTED": 0}
        for r in rows:
            dist[r["decision"]] = r["cnt"]
        return dist

    def get_exception_categories(self) -> Dict[str, int]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT reason_code, COUNT(*) as cnt 
        FROM invoice_runs 
        WHERE decision != 'APPROVED' AND reason_code != '' 
        GROUP BY reason_code 
        ORDER BY cnt DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return {r["reason_code"]: r["cnt"] for r in rows}

    def get_cumulative_billed_for_po(self, po_number: str) -> Decimal:
        """
        Calculate total amount billed and approved against a purchase order in SQLite.
        Considers both automated approvals and manual specialist sign-offs.
        """
        if not po_number:
            return Decimal("0.00")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(SUM(invoice_total), 0.0) 
            FROM invoice_runs 
            WHERE UPPER(TRIM(po_number)) = ? 
              AND (decision = 'APPROVED' OR reviewer_decision = 'MANUALLY_APPROVED')
        """, (po_number.strip().upper(),))
        total = cursor.fetchone()[0] or 0.0
        conn.close()
        return Decimal(str(total)).quantize(Decimal("0.01"))

    def get_accepted_invoices_for_po(self, po_number: str) -> List[Dict[str, Any]]:
        """
        Retrieve all accepted invoices previously recorded against a purchase order.
        """
        if not po_number:
            return []
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT run_id, invoice_number, invoice_total, created_at, decision, reviewer_decision
            FROM invoice_runs 
            WHERE UPPER(TRIM(po_number)) = ? 
              AND (decision = 'APPROVED' OR reviewer_decision = 'MANUALLY_APPROVED')
            ORDER BY created_at ASC
        """, (po_number.strip().upper(),))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_po_balance_summary(self, po_number: str, po_total: Decimal) -> Dict[str, Any]:
        """
        Return comprehensive cumulative balance summary for a purchase order.
        """
        cumulative_billed = self.get_cumulative_billed_for_po(po_number)
        remaining = max(po_total - cumulative_billed, Decimal("0.00"))
        prior_invoices = self.get_accepted_invoices_for_po(po_number)
        return {
            "po_number": po_number,
            "po_total": po_total,
            "cumulative_billed": cumulative_billed,
            "remaining_balance": remaining,
            "prior_invoice_count": len(prior_invoices),
            "prior_invoices": prior_invoices
        }

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        for json_col in [
            "stages_log_json", "extracted_data_json", "vendor_result_json",
            "duplicate_result_json", "po_result_json", "reconciliation_result_json",
            "decision_result_json", "corrected_fields_json"
        ]:
            key = json_col.replace("_json", "")
            if key == "stages_log":
                d[key] = json.loads(d.get(json_col) or "[]")
            else:
                d[key] = json.loads(d.get(json_col) or "{}")
        return d

    def list_seller_responses(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List seller response cases, optionally filtered by status."""
        conn = get_db_connection()
        cursor = conn.cursor()
        if status and status != "ALL":
            cursor.execute("SELECT * FROM seller_responses WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM seller_responses ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_seller_response_action(
        self,
        response_id: str,
        action: str,
        notes: str,
        approve_invoice: bool = False
    ) -> None:
        """Record buyer decision on seller response and update audit event."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Update response
        new_status = "RESOLVED_ACCEPTED" if approve_invoice else "ACTIONED_REQ_CREDIT_NOTE"
        cursor.execute("""
            UPDATE seller_responses
            SET status = ?, buyer_action = ?, buyer_notes = ?, updated_at = ?
            WHERE response_id = ?
        """, (new_status, action, notes, now_str, response_id))
        
        # 2. Fetch linked run_id
        cursor.execute("SELECT run_id, invoice_number, vendor_name FROM seller_responses WHERE response_id = ?", (response_id,))
        row = cursor.fetchone()
        if row and row["run_id"]:
            run_id = row["run_id"]
            # Record audit event
            event_id = f"EVT-{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO audit_events (event_id, run_id, timestamp, event_type, actor, details_json)
                VALUES (?, ?, ?, 'SELLER_RESPONSE_ACTIONED', 'AP Specialist', ?)
            """, (event_id, run_id, now_str, json.dumps({"response_id": response_id, "action": action, "notes": notes})))
            
            # If accepted and approve_invoice is true, mark invoice as MANUALLY_APPROVED
            if approve_invoice:
                cursor.execute("""
                    UPDATE invoice_runs
                    SET reviewer_decision = 'MANUALLY_APPROVED', reviewer_notes = ?, reviewed_at = ?
                    WHERE run_id = ?
                """, (f"Accepted seller explanation ({action}): {notes}", now_str, run_id))

        conn.commit()
        conn.close()

    def list_disputes(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List AP dispute records, optionally filtered by status."""
        conn = get_db_connection()
        cursor = conn.cursor()
        if status and status != "ALL":
            cursor.execute("SELECT * FROM disputes WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM disputes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def resolve_dispute(self, dispute_id: str, resolution_notes: str) -> None:
        """Resolve a dispute and commit settlement summary."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE disputes
            SET status = 'RESOLVED', resolution_summary = ?, resolved_at = ?
            WHERE dispute_id = ?
        """, (resolution_notes, now_str, dispute_id))
        conn.commit()
        conn.close()

