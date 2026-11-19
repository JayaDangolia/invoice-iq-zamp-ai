import io
import csv
from typing import Any, Dict

class ReportingService:
    @staticmethod
    def generate_csv_report(run: Dict[str, Any]) -> str:
        """Generate a downloadable CSV decision summary report for a run."""
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["INVOICEIQ DECISION & AUDIT REPORT"])
        writer.writerow([])
        writer.writerow(["Field", "Value"])
        writer.writerow(["Run ID", run.get("run_id")])
        writer.writerow(["Filename", run.get("filename")])
        writer.writerow(["Submission Date", run.get("created_at")])
        writer.writerow(["Overall Decision", run.get("decision")])
        writer.writerow(["Reason Code", run.get("reason_code")])
        writer.writerow(["Extraction Mode", run.get("extraction_mode")])
        writer.writerow(["Processing Time (ms)", run.get("duration_ms")])
        writer.writerow([])

        # Invoice Info
        writer.writerow(["INVOICE METADATA"])
        writer.writerow(["Invoice Number", run.get("invoice_number") or "N/A"])
        writer.writerow(["Invoice Date", run.get("invoice_date") or "N/A"])
        writer.writerow(["Vendor Name", run.get("vendor_name") or "N/A"])
        writer.writerow(["Vendor ID", run.get("vendor_id") or "N/A"])
        writer.writerow(["PO Number", run.get("po_number") or "N/A"])
        writer.writerow(["Total Amount", run.get("invoice_total") or 0.0])
        writer.writerow(["Currency", run.get("currency") or "INR"])
        writer.writerow([])

        # Decision & Action
        writer.writerow(["DECISION DETAILS"])
        writer.writerow(["Explanation", run.get("explanation")])
        writer.writerow(["Recommended Action", run.get("recommended_action")])
        if run.get("reviewer_decision"):
            writer.writerow(["Reviewer Decision", run.get("reviewer_decision")])
            writer.writerow(["Reviewer Notes", run.get("reviewer_notes")])
            writer.writerow(["Reviewed At", run.get("reviewed_at")])
        writer.writerow([])

        # Line Items
        extracted = run.get("extracted_data", {})
        line_items = extracted.get("line_items", [])
        if line_items:
            writer.writerow(["EXTRACTED LINE ITEMS"])
            writer.writerow(["Description", "Quantity", "Unit Price", "Line Total"])
            for li in line_items:
                writer.writerow([
                    li.get("description", ""),
                    li.get("quantity", ""),
                    li.get("unit_price", ""),
                    li.get("line_total", "")
                ])
            writer.writerow([])

        # Checks
        dec_res = run.get("decision_result", {})
        writer.writerow(["VALIDATION CHECKS"])
        for p in dec_res.get("passed_checks", []):
            writer.writerow(["PASSED", p])
        for f in dec_res.get("failed_checks", []):
            writer.writerow(["FAILED", f])
        for w in dec_res.get("warnings", []):
            writer.writerow(["WARNING", w])

        return output.getvalue()
