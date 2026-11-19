from typing import Any, Dict, List, Optional
import streamlit as st
import pandas as pd
from database.repository import InvoiceRepository
from services.pdf_reader import PDFReaderService
from config.settings import SAMPLE_INVOICES_DIR
from ui.components import (
    render_app_header,
    render_page_heading,
    render_summary_kpi_card,
    render_status_pill,
    render_empty_state
)

def render_review_queue_page(
    repository: InvoiceRepository,
    selected_run_id: Optional[str] = None
) -> None:
    # 1. Top Enterprise Breadcrumb Bar
    render_app_header("Review Queue")

    # Fetch pending review runs
    pending_runs = repository.list_runs(decision_filter="PENDING REVIEW", limit=50)

    # 2. Page Title Header
    render_page_heading(
        title="Review Queue",
        subtitle="Invoices requiring Accounts Payable specialist inspection, discrepancy resolution, and manual sign-off.",
        badge=f"{len(pending_runs)} Pending Items"
    )

    if not pending_runs:
        render_empty_state(
            title="Review Queue is Clean",
            description="No invoices are currently pending human review. All processed documents have either passed automated validation or been rejected per policy."
        )
        return

    # Check if a specific run is being reviewed
    reviewing_id = st.session_state.get("reviewing_run_id") or selected_run_id
    active_run = None
    if reviewing_id:
        active_run = repository.get_run(reviewing_id)

    # 3. Top Summary KPI Cards (Pastel Style with 1-Click Interactive Drilldown)
    total_pending_amt = sum(float(r.get("invoice_total") or 0.0) for r in pending_runs)
    mismatch_count = sum(1 for r in pending_runs if "MISMATCH" in str(r.get("reason_code", "")) or "VARIANCE" in str(r.get("reason_code", "")))

    active_filter = st.session_state.get("rq_filter", "ALL")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(render_summary_kpi_card(
            label="Awaiting Inspection",
            value=str(len(pending_runs)),
            subtext="Invoices requiring manual resolution",
            theme="coral",
            trend_badge="ACTION REQ",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Show All Pending", key="kpi_card_rq_all", use_container_width=True):
            st.session_state["rq_filter"] = "ALL"
            st.session_state["reviewing_run_id"] = None
            st.rerun()
    with c2:
        st.markdown(render_summary_kpi_card(
            label="Total Value at Risk",
            value=f"₹{total_pending_amt:,.2f}",
            subtext="Cumulative pending invoice exposure",
            theme="blue",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● High Value (≥ ₹40k)", key="kpi_card_rq_high", use_container_width=True):
            st.session_state["rq_filter"] = "HIGH_VALUE"
            st.session_state["reviewing_run_id"] = None
            st.rerun()
    with c3:
        st.markdown(render_summary_kpi_card(
            label="Tolerance Exceptions",
            value=str(mismatch_count),
            subtext="Price or line-item variances",
            theme="purple",
            trend_badge="VARIANCE",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"></rect><path d="M8 12h8"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Tolerance Only", key="kpi_card_rq_var", use_container_width=True):
            st.session_state["rq_filter"] = "VARIANCE"
            st.session_state["reviewing_run_id"] = None
            st.rerun()

    # Filter display list based on active filter
    if active_filter == "HIGH_VALUE":
        display_runs = [r for r in pending_runs if float(r.get("invoice_total") or 0.0) >= 40000]
    elif active_filter == "VARIANCE":
        display_runs = [r for r in pending_runs if "MISMATCH" in str(r.get("reason_code", "")) or "VARIANCE" in str(r.get("reason_code", ""))]
    else:
        display_runs = pending_runs

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 4. If reviewing an active run, display workspace first
    if active_run:
        _render_review_workspace(active_run, repository)
        st.markdown("<div style='margin: 1.5rem 0 0.85rem 0; font-weight: 700; color: #0F172A; font-size: 1.05rem;'>All Pending Queue Items</div>", unsafe_allow_html=True)

    # 5. Review List Table (High Density)
    filter_label = f" (Filtered: {active_filter})" if active_filter != "ALL" else ""
    st.markdown(f"""
    <div class="table-container-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; padding-bottom: 0.65rem; border-bottom: 1px solid #F1F5F9;">
            <div style="font-weight: 700; font-size: 0.98rem; color: #0F172A;">Invoices Awaiting Review{filter_label}</div>
            <div style="font-size: 0.78rem; color: #64748B;">Showing <b>{len(display_runs)}</b> of {len(pending_runs)} exception items</div>
        </div>
    """, unsafe_allow_html=True)

    # Table Header Row
    st.markdown("""
    <div style="display: grid; grid-template-columns: 2fr 2.5fr 1.5fr 2fr 1.5fr 1fr; gap: 0.75rem; padding: 0.65rem 0.85rem; background: #F8FAFC; border-radius: 8px; font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
        <div>Invoice & Run ID</div>
        <div>Vendor & PO</div>
        <div>Amount</div>
        <div>Exception Reason</div>
        <div>Resolution Status</div>
        <div style="text-align: right;">Action</div>
    </div>
    """, unsafe_allow_html=True)

    for run in display_runs:
        is_selected = (active_run and active_run.get("run_id") == run.get("run_id"))
        
        c1, c2, c3, c4, c5, c6 = st.columns([2, 2.5, 1.5, 2, 1.5, 1])
        with c1:
            st.markdown(f"**{run.get('invoice_number') or 'Missing Inv #'}**<br/><span style='font-size:0.75rem; color:#6366F1; font-family:JetBrains Mono;'>{run.get('run_id')}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"**{run.get('vendor_name') or 'Unverified'}**<br/><span style='font-size:0.75rem; color:#64748B;'>PO: {run.get('po_number') or 'None'}</span>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"**₹{run.get('invoice_total', 0.0):,.2f}**")
        with c4:
            st.markdown(f"<span style='font-size:0.75rem; color:#B45309; font-weight:600; background:#FEF3C7; padding:2px 8px; border-radius:4px;'>{run.get('reason_code')}</span>", unsafe_allow_html=True)
        with c5:
            reviewer_status = run.get("reviewer_decision")
            if reviewer_status:
                st.markdown(render_status_pill(reviewer_status), unsafe_allow_html=True)
            else:
                st.markdown(render_status_pill("PENDING REVIEW"), unsafe_allow_html=True)
        with c6:
            btn_text = "Close" if is_selected else "Inspect"
            if st.button(btn_text, key=f"btn_act_rev_{run.get('run_id')}", use_container_width=True):
                if is_selected:
                    st.session_state["reviewing_run_id"] = None
                else:
                    st.session_state["reviewing_run_id"] = run.get("run_id")
                st.rerun()

        st.markdown("<div style='height: 1px; background: #F1F5F9; margin: 0.35rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_review_workspace(run: Dict[str, Any], repository: InvoiceRepository) -> None:
    inv_num = run.get("invoice_number") or "N/A"
    run_id = run.get("run_id")

    col_back, _ = st.columns([1.6, 4.4])
    with col_back:
        if st.button("← Back to Review Queue", key="btn_back_review_ws", use_container_width=True):
            st.session_state["reviewing_run_id"] = None
            st.session_state["active_run_id"] = None
            st.rerun()

    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1.5px solid #6366F1; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.75rem;">
            <div>
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: #6366F1; font-weight: 700;">Active Review Workspace</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-top: 0.2rem;">Invoice {inv_num} · <span style="font-family: JetBrains Mono; font-size: 0.95rem; color: #64748B;">{run_id}</span></div>
            </div>
            <div>
                {render_status_pill(run.get("decision", ""))}
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Exception Diagnostics Alert
    dec_res = run.get("decision_result", {})
    failed_checks = dec_res.get("failed_checks", [])
    warnings = dec_res.get("warnings", [])

    st.markdown(f"""
    <div style="background: #FFFBEB; border-left: 4px solid #D97706; padding: 0.85rem 1.15rem; border-radius: 0 8px 8px 0; margin-bottom: 1.25rem;">
        <div style="font-weight: 700; color: #92400E; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.04em;">Exception Diagnostics</div>
        <div style="color: #78350F; font-size: 0.9rem; margin-top: 0.25rem; font-weight: 500;"><b>Policy Trigger:</b> {run.get('explanation')}</div>
    </div>
    """, unsafe_allow_html=True)

    if failed_checks or warnings:
        fc_cols = st.columns(2)
        with fc_cols[0]:
            if failed_checks:
                st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #B91C1C; margin-bottom: 0.25rem;'>Validation Discrepancies:</div>", unsafe_allow_html=True)
                for f in failed_checks:
                    st.markdown(f"<div style='font-size: 0.8rem; color: #991B1B; margin-bottom: 0.2rem;'>• {f}</div>", unsafe_allow_html=True)
        with fc_cols[1]:
            if warnings:
                st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #B45309; margin-bottom: 0.25rem;'>Policy Warnings:</div>", unsafe_allow_html=True)
                for w in warnings:
                    st.markdown(f"<div style='font-size: 0.8rem; color: #92400E; margin-bottom: 0.2rem;'>• {w}</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # Split-Screen Layout: Document Preview on Left, Resolution Form on Right
    col_doc, col_actions = st.columns([1.1, 1])

    with col_doc:
        st.markdown("<div style='font-weight: 700; font-size: 0.9rem; color: #1E293B; margin-bottom: 0.5rem;'>Document Evidence Preview</div>", unsafe_allow_html=True)
        filename = run.get("filename", "")
        preset_file = SAMPLE_INVOICES_DIR / filename
        if preset_file.exists():
            try:
                reader = PDFReaderService()
                img_bytes = reader.render_page_image(preset_file.read_bytes(), page_number=0, dpi=120)
                st.image(img_bytes, caption=f"Original File: {filename}", use_container_width=True)
            except Exception:
                st.info(f"PDF Preview for {filename}")
        else:
            st.info(f"Original file '{filename}' was uploaded directly during session.")

    with col_actions:
        st.markdown("<div style='font-weight: 700; font-size: 0.9rem; color: #1E293B; margin-bottom: 0.5rem;'>Specialist Corrections & Resolution</div>", unsafe_allow_html=True)

        current_inv_num = st.text_input("Invoice Number", value=run.get("invoice_number") or "", key="ws_inv_num")
        current_vendor_name = st.text_input("Vendor Legal Name", value=run.get("vendor_name") or "", key="ws_vendor_name")

        candidate_pos = run.get("po_result", {}).get("candidate_po_details", [])
        if candidate_pos:
            st.markdown("""
            <div style="font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#4338CA; letter-spacing:0.4px; margin-top:0.4rem; margin-bottom:0.35rem;">
                Surfaced Candidate POs (1-Click Selection):
            </div>
            """, unsafe_allow_html=True)
            c_cols = st.columns(min(len(candidate_pos), 3))
            for c_idx, cpo in enumerate(candidate_pos[:3]):
                with c_cols[c_idx]:
                    c_po_num = cpo.get("po_number")
                    c_bal = float(cpo.get("remaining_balance") or 0.0)
                    st.markdown(f"<div style='background:#EEF2FF; border:1px solid #C7D2FE; border-radius:6px; padding:0.45rem; margin-bottom:0.35rem;'><span style='font-weight:700; font-size:0.8rem; color:#4338CA;'>{c_po_num}</span><br/><span style='font-size:0.72rem; color:#6B7280;'>Bal: ₹{c_bal:,.0f}</span></div>", unsafe_allow_html=True)
                    if st.button(f"Link {c_po_num}", key=f"btn_cpo_{c_idx}", use_container_width=True):
                        st.session_state["selected_candidate_po"] = c_po_num
                        st.rerun()

        default_po = st.session_state.get("selected_candidate_po", run.get("po_number") or "")
        current_po_num = st.text_input("Assigned Purchase Order (PO)", value=default_po, key="ws_po_num")
        current_amount = st.number_input("Verified Total Amount (INR)", value=float(run.get("invoice_total") or 0.0), step=100.0, key="ws_amt")

        reviewer_notes = st.text_area(
            "Reviewer Rationale & Audit Notes *",
            value=run.get("reviewer_notes") or "",
            placeholder="Document reason for approval or rejection, verified PO variance confirmation, or credit note details...",
            help="Reviewer notes are stored in the immutable audit trail and cannot be erased."
        )

        st.markdown("""
        <div style="font-size: 0.75rem; color: #64748B; margin: 0.75rem 0 1rem 0; line-height: 1.4;">
            <b>Compliance Note:</b> Manual decisions preserve the immutable original automated decision in SQLite audit records.
        </div>
        """, unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("Approve Invoice", type="primary", use_container_width=True, key="btn_approve_inv"):
                if not reviewer_notes.strip():
                    st.warning("Please record reviewer notes explaining the resolution before approving.")
                else:
                    corrected = {
                        "invoice_number": current_inv_num,
                        "vendor_name": current_vendor_name,
                        "po_number": current_po_num,
                        "invoice_total": current_amount,
                    }
                    repository.update_reviewer_action(
                        run_id=run.get("run_id"),
                        reviewer_decision="MANUALLY_APPROVED",
                        reviewer_notes=reviewer_notes,
                        corrected_fields=corrected
                    )
                    st.success("Invoice successfully marked as MANUALLY APPROVED. Audit event committed.")
                    st.session_state["reviewing_run_id"] = None
                    st.rerun()

        with btn_col2:
            if st.button("Reject Invoice", use_container_width=True, key="btn_reject_inv"):
                if not reviewer_notes.strip():
                    st.warning("Please record reviewer notes explaining the rejection before proceeding.")
                else:
                    corrected = {
                        "invoice_number": current_inv_num,
                        "vendor_name": current_vendor_name,
                        "po_number": current_po_num,
                        "invoice_total": current_amount,
                    }
                    repository.update_reviewer_action(
                        run_id=run.get("run_id"),
                        reviewer_decision="MANUALLY_REJECTED",
                        reviewer_notes=reviewer_notes,
                        corrected_fields=corrected
                    )
                    st.error("Invoice marked as MANUALLY REJECTED. Audit event committed.")
                    st.session_state["reviewing_run_id"] = None
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
