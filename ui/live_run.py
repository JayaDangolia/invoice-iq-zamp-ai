import time
from typing import Any, Dict, List, Optional
import textwrap
import streamlit as st
import pandas as pd
from core.models import StageStatus, StageLog
from core.workflow import WorkflowOrchestrator
from services.reporting_service import ReportingService
from ui.components import render_decision_banner, render_status_pill, render_four_phase_stepper

def execute_and_render_live_pipeline(
    file_bytes: bytes,
    filename: str,
    orchestrator: WorkflowOrchestrator
) -> Dict[str, Any]:
    """
    Execute backend pipeline with real-time updates grouped into the
    4 understandable business phases: Read -> Verify -> Reconcile -> Decide.
    """
    header_html = textwrap.dedent("""
    <div style="margin-bottom: 1.25rem;">
        <h2 style="font-size: 1.4rem; font-weight: 700; color: #172B4D; margin: 0 0 0.2rem 0; letter-spacing: -0.3px;">
            Processing Funnel
        </h2>
        <div style="color: #5E6C84; font-size: 0.85rem;">
            Executing end-to-end ingestion, validation, procurement matching and policy decisioning.
        </div>
    </div>
    """).strip()
    st.markdown(header_html, unsafe_allow_html=True)

    stepper_placeholder = st.empty()
    progress_bar = st.progress(0.0)

    def _on_stage_update(current_stage: StageLog, all_stages: List[StageLog]):
        stage_num = current_stage.stage_id

        # Phase 1 status (Stages 1-5)
        p1_stages = [s for s in all_stages if s.stage_id in range(1, 6)]
        p1_done = all(s.status in (StageStatus.SUCCESS, StageStatus.WARNING) for s in p1_stages if s.status != StageStatus.NOT_STARTED) and any(s.status != StageStatus.NOT_STARTED for s in p1_stages)
        p1_status = "success" if p1_done and stage_num >= 6 else ("active" if stage_num in range(1, 6) else "pending")

        # Phase 2 status (Stages 6-7)
        p2_stages = [s for s in all_stages if s.stage_id in (6, 7)]
        p2_warning = any(s.status == StageStatus.WARNING for s in p2_stages)
        p2_status = "warning" if (p2_warning and stage_num >= 8) else ("success" if stage_num >= 8 else ("active" if stage_num in (6, 7) else "pending"))

        # Phase 3 status (Stages 8-9)
        p3_stages = [s for s in all_stages if s.stage_id in (8, 9)]
        p3_warning = any(s.status == StageStatus.WARNING for s in p3_stages)
        p3_status = "warning" if (p3_warning and stage_num >= 10) else ("success" if stage_num >= 10 else ("active" if stage_num in (8, 9) else "pending"))

        # Phase 4 status (Stages 10-11)
        p4_status = "success" if stage_num == 11 and current_stage.status == StageStatus.SUCCESS else ("active" if stage_num in (10, 11) else "pending")

        completed_count = sum(1 for s in all_stages if s.status in (StageStatus.SUCCESS, StageStatus.WARNING, StageStatus.FAILED))
        progress_val = min(float(completed_count) / float(len(all_stages)), 1.0)
        progress_bar.progress(progress_val)

        with stepper_placeholder.container():
            render_four_phase_stepper(
                phase1_status=p1_status,
                phase2_status=p2_status,
                phase3_status=p3_status,
                phase4_status=p4_status,
                phase1_meta="Text & metadata parsing",
                phase2_meta="Master data & duplicates",
                phase3_meta="PO balance & variance",
                phase4_meta="Policy outcome"
            )

    run_record = orchestrator.execute_workflow(
        file_bytes=file_bytes,
        filename=filename,
        stage_callback=_on_stage_update
    )

    progress_bar.progress(1.0)
    time.sleep(0.3)
    return run_record

def render_decision_report(run: Dict[str, Any]) -> None:
    """
    Render the redesigned enterprise Decision Report structured into
    Sections A through H matching professional financial document standards.
    """
    decision = run.get("decision", "PENDING REVIEW")
    reason_code = run.get("reason_code", "")
    explanation = run.get("explanation", "")
    action = run.get("recommended_action", "")
    extracted = run.get("extracted_data", {})

    # Top Invoice Identity Bar
    inv_num = run.get("invoice_number") or "Unspecified"
    vend_title = run.get("vendor_name") or "Unverified Vendor"
    inv_date = run.get("invoice_date") or run.get("created_at", "")[:10]
    total_val = float(run.get("invoice_total") or 0.0)

    identity_bar_html = textwrap.dedent(f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; border-bottom: 1px solid #E2E6EC; padding-bottom: 0.75rem;">
        <div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #172B4D; letter-spacing: -0.3px;">
                {inv_num} · {vend_title}
            </div>
            <div style="font-size: 0.8rem; color: #7A869A; margin-top: 0.2rem;">
                Run ID: <span style="font-family:JetBrains Mono;">{run.get('run_id')}</span> · Received: {inv_date} · Total: <span style="font-weight:600; color:#172B4D;">₹{total_val:,.2f}</span>
            </div>
        </div>
        <div>
            {render_status_pill(decision)}
        </div>
    </div>
    """).strip()
    st.markdown(identity_bar_html, unsafe_allow_html=True)

    # 1. Authoritative Outcome Banner
    render_decision_banner(decision, reason_code, explanation, action)

    # 2. Section A: Invoice Information (Single self-contained HTML block)
    subtotal_val = float(extracted.get('subtotal') or 0.0)
    tax_val = float(extracted.get('tax') or 0.0)
    inv_tot_val = float(extracted.get('invoice_total') or 0.0)

    sec_a_html = textwrap.dedent(f"""
    <div class="ent-card">
        <div class="ent-card-header">
            <div class="ent-card-title">Section A — Invoice Information</div>
            <div class="ent-card-action">Extracted metadata</div>
        </div>
        <div class="meta-kv-grid">
            <div class="meta-kv">
                <span class="meta-kv-label">Vendor Name</span>
                <span class="meta-kv-val">{extracted.get('vendor_name') or 'N/A'}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Tax ID (GSTIN)</span>
                <span class="meta-kv-val" style="font-family:JetBrains Mono;">{extracted.get('vendor_tax_id') or 'N/A'}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Invoice Number</span>
                <span class="meta-kv-val" style="font-family:JetBrains Mono;">{extracted.get('invoice_number') or 'N/A'}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Invoice Date</span>
                <span class="meta-kv-val">{extracted.get('invoice_date') or 'N/A'}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">PO Reference</span>
                <span class="meta-kv-val" style="font-family:JetBrains Mono;">{extracted.get('po_number') or 'None'}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Currency</span>
                <span class="meta-kv-val">{extracted.get('currency', 'INR')}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Subtotal</span>
                <span class="meta-kv-val">₹{subtotal_val:,.2f}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Tax (GST)</span>
                <span class="meta-kv-val">₹{tax_val:,.2f}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Total Amount</span>
                <span class="meta-kv-val" style="font-weight:700; color:#172B4D;">₹{inv_tot_val:,.2f}</span>
            </div>
            <div class="meta-kv">
                <span class="meta-kv-label">Extraction Mode</span>
                <span class="meta-kv-val">{run.get('extraction_mode', 'deterministic')}</span>
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(sec_a_html, unsafe_allow_html=True)

    # Itemized Line Items Table
    line_items = extracted.get("line_items", [])
    if line_items:
        st.markdown("<div style='font-size:0.85rem; font-weight:600; color:#172B4D; margin: 0.75rem 0 0.4rem 0;'>Itemized Line Details</div>", unsafe_allow_html=True)
        items_rows = []
        for li in line_items:
            items_rows.append({
                "Description": li.get("description"),
                "Qty": float(li.get("quantity") or 0),
                "Unit Price": f"₹{float(li.get('unit_price') or 0):,.2f}",
                "Line Total": f"₹{float(li.get('line_total') or 0):,.2f}"
            })
        st.dataframe(pd.DataFrame(items_rows), use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

    # 3. Two-Column Layout for Section B, C, D
    col_left, col_right = st.columns([1, 1])

    with col_left:
        # SECTION B — Vendor Verification
        vendor_res = run.get("vendor_result", {})
        v_ok = vendor_res.get("is_verified", False) and vendor_res.get("is_approved", False)
        sec_b_html = textwrap.dedent(f"""
        <div class="ent-card">
            <div class="ent-card-header">
                <div class="ent-card-title">Section B — Vendor Verification</div>
                <div class="ent-card-action">{'Verified' if v_ok else 'Attention'}</div>
            </div>
            <div class="meta-kv-grid">
                <div class="meta-kv">
                    <span class="meta-kv-label">Master Vendor ID</span>
                    <span class="meta-kv-val" style="font-family:JetBrains Mono;">{vendor_res.get('vendor_id') or 'N/A'}</span>
                </div>
                <div class="meta-kv">
                    <span class="meta-kv-label">Legal Name</span>
                    <span class="meta-kv-val">{vendor_res.get('legal_name') or 'N/A'}</span>
                </div>
                <div class="meta-kv">
                    <span class="meta-kv-label">Authorization Status</span>
                    <span class="meta-kv-val"><b>{vendor_res.get('status', 'UNKNOWN')}</b></span>
                </div>
                <div class="meta-kv">
                    <span class="meta-kv-label">Payment Approval</span>
                    <span class="meta-kv-val">{'Approved' if vendor_res.get('is_approved') else 'Unapproved'}</span>
                </div>
                <div class="meta-kv" style="grid-column: span 2;">
                    <span class="meta-kv-label">Match Method</span>
                    <span class="meta-kv-val">{vendor_res.get('match_type')} ({int(vendor_res.get('match_confidence', 0)*100)}% match)</span>
                </div>
            </div>
        </div>
        """).strip()
        st.markdown(sec_b_html, unsafe_allow_html=True)

        # SECTION C — Duplicate Detection
        dup_res = run.get("duplicate_result", {})
        is_dup = dup_res.get("is_duplicate", False)
        dup_alert_html = f"""
        <div style="background:#FEF2F2; border:1px solid #FECACA; border-radius:6px; padding:0.75rem 1rem; color:#B91C1C; font-size:0.85rem;">
            <b>Duplicate Submission Detected:</b> {dup_res.get('notes')}<br/>
            Prior Run ID: <code style="font-family:JetBrains Mono;">{dup_res.get('prior_run_id')}</code><br/>
            Submitted: {dup_res.get('prior_submission_date')}
        </div>
        """ if is_dup else """
        <div style="font-size:0.85rem; color:#15803D; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:0.65rem 0.85rem;">
            No prior submission found with matching document content or Vendor + Invoice ID.
        </div>
        """

        sec_c_html = textwrap.dedent(f"""
        <div class="ent-card">
            <div class="ent-card-header">
                <div class="ent-card-title">Section C — Duplicate Detection</div>
                <div class="ent-card-action">{'Duplicate' if is_dup else 'Clean'}</div>
            </div>
            {dup_alert_html}
        </div>
        """).strip()
        st.markdown(sec_c_html, unsafe_allow_html=True)

    with col_right:
        # SECTION D — Purchase Order Match
        po_res = run.get("po_result", {})
        po_ok = po_res.get("is_matched", False)
        po_tot = float(po_res.get('initial_po_total') or po_res.get('po_total') or 0.0)
        cumul_billed = float(po_res.get('cumulative_billed_amount') or 0.0)
        po_rem = float(po_res.get('dynamic_remaining_balance') or po_res.get('remaining_balance') or 0.0)
        is_partial = po_res.get('is_partial_invoice', False)
        prior_invs = po_res.get('prior_accepted_invoices', [])
        candidate_pos = po_res.get('candidate_po_details', [])

        prior_info_html = ""
        if prior_invs:
            prior_info_html = f"<br/><span style='font-size:0.75rem; color:#6366F1;'>Prior accepted invoices: {', '.join(prior_invs)}</span>"

        sec_d_html = textwrap.dedent(f"""
        <div class="ent-card">
            <div class="ent-card-header">
                <div class="ent-card-title">Section D — Purchase Order Match</div>
                <div class="ent-card-action">{'Matched' if po_ok else ('Ambiguous Match' if candidate_pos else 'Unmatched')}</div>
            </div>
            <div class="meta-kv-grid">
                <div class="meta-kv">
                    <span class="meta-kv-label">Matched PO Number</span>
                    <span class="meta-kv-val" style="font-family:JetBrains Mono;">{po_res.get('po_number') or ('Multiple Candidates' if candidate_pos else 'None')}</span>
                </div>
                <div class="meta-kv">
                    <span class="meta-kv-label">Cumulative Billing Tracking</span>
                    <span class="meta-kv-val"><b>{'Split / Milestone Billing' if is_partial else 'Standard Billing'}</b></span>
                </div>
                <div class="meta-kv">
                    <span class="meta-kv-label">Initial PO Commitment</span>
                    <span class="meta-kv-val">₹{po_tot:,.2f}</span>
                </div>
                <div class="meta-kv">
                    <span class="meta-kv-label">Cumulative Prior Billed</span>
                    <span class="meta-kv-val">₹{cumul_billed:,.2f}</span>
                </div>
                <div class="meta-kv" style="grid-column: span 2;">
                    <span class="meta-kv-label">Dynamic Remaining Balance</span>
                    <span class="meta-kv-val" style="font-size:1.05rem; font-family:JetBrains Mono; color:{'#16A36A' if po_rem > 0 else '#E45D64'};">₹{po_rem:,.2f}</span>
                    {prior_info_html}
                </div>
                <div class="meta-kv" style="grid-column: span 2;">
                    <span class="meta-kv-label">Match Resolution</span>
                    <span class="meta-kv-val">{po_res.get('match_type')} — {po_res.get('notes')}</span>
                </div>
            </div>
        </div>
        """).strip()
        st.markdown(sec_d_html, unsafe_allow_html=True)

        if candidate_pos:
            st.markdown("""
            <div style="background:#EEF2FF; border:1px solid #C7D2FE; border-radius:6px; padding:0.75rem 1rem; margin-bottom:1rem; font-size:0.82rem; color:#3730A3;">
                <b>Surfaced Candidate Purchase Orders:</b> Multiple active PO commitments exist for this vendor.
            </div>
            """, unsafe_allow_html=True)

    # 4. SECTION E — Financial Reconciliation Comparison
    recon = run.get("reconciliation_result", {})
    inv_amount = float(recon.get("invoice_total") or 0.0)
    po_amount = float(recon.get("po_applicable_amount") or 0.0)
    var_amount = float(recon.get("variance_amount") or 0.0)
    var_pct = float(recon.get("variance_pct") or 0.0)
    tol_amount = float(recon.get("tolerance_threshold_amount") or 0.0)
    within_tol = recon.get("within_tolerance", True)

    var_color = '#B45309' if not within_tol else '#15803D'

    sec_e_html = textwrap.dedent(f"""
    <div class="ent-card">
        <div class="ent-card-header">
            <div class="ent-card-title">Section E — Financial Reconciliation</div>
            <div class="ent-card-action">Tolerance: 2% (Capped at ₹500)</div>
        </div>
        <div class="comparison-grid">
            <div class="comparison-item">
                <span class="comparison-label">Invoice Amount</span>
                <span class="comparison-value">₹{inv_amount:,.2f}</span>
            </div>
            <div class="comparison-item">
                <span class="comparison-label">Applicable PO Amount</span>
                <span class="comparison-value">₹{po_amount:,.2f}</span>
            </div>
            <div class="comparison-item">
                <span class="comparison-label">Net Variance</span>
                <span class="comparison-value" style="color: {var_color};">
                    ₹{abs(var_amount):,.2f} ({abs(var_pct):.1f}%)
                </span>
            </div>
            <div class="comparison-item">
                <span class="comparison-label">Tolerance Boundary</span>
                <span class="comparison-value">₹{tol_amount:,.2f} max</span>
            </div>
        </div>
    </div>
    """).strip()
    st.markdown(sec_e_html, unsafe_allow_html=True)

    # Detailed Table
    recon_df = pd.DataFrame([
        {"Item": "Total Billed vs PO", "Invoice Value": f"₹{inv_amount:,.2f}", "PO Baseline": f"₹{po_amount:,.2f}", "Variance": f"₹{abs(var_amount):,.2f}", "Compliance": "Within Limit" if within_tol else "Exceeds Tolerance"},
        {"Item": "Arithmetic Check", "Invoice Value": f"₹{subtotal_val:,.2f} + ₹{tax_val:,.2f}", "PO Baseline": f"₹{inv_amount:,.2f}", "Variance": "₹0.00", "Compliance": "Consistent" if recon.get("is_arithmetic_consistent", True) else "Discrepancy"},
    ])
    st.dataframe(recon_df, use_container_width=True, hide_index=True)

    # 5. SECTION F & SECTION G: Validation Results & Reasoning
    c_checks, c_reason = st.columns([1, 1])

    with c_checks:
        dec_res = run.get("decision_result", {})
        passed_checks = dec_res.get("passed_checks", [])
        failed_checks = dec_res.get("failed_checks", [])
        warnings = dec_res.get("warnings", [])

        passed_html = "".join([f"<div style='font-size:0.82rem; color:#172B4D; margin-bottom:0.25rem;'>✓ {p}</div>" for p in passed_checks])
        failed_html = "".join([f"<div style='font-size:0.82rem; color:#B91C1C; margin-bottom:0.25rem;'>✕ {f}</div>" for f in failed_checks])
        warning_html = "".join([f"<div style='font-size:0.82rem; color:#B45309; margin-bottom:0.25rem;'>! {w}</div>" for w in warnings])

        checks_body = ""
        if passed_checks:
            checks_body += f"<div style='font-size:0.75rem; font-weight:600; text-transform:uppercase; color:#15803D; margin-bottom:0.35rem;'>Passed Checks:</div>{passed_html}"
        if failed_checks or warnings:
            checks_body += f"<div style='margin-top:0.6rem; font-size:0.75rem; font-weight:600; text-transform:uppercase; color:#B45309; margin-bottom:0.35rem;'>Unresolved Exceptions:</div>{failed_html}{warning_html}"

        sec_f_html = textwrap.dedent(f"""
        <div class="ent-card">
            <div class="ent-card-header">
                <div class="ent-card-title">Section F — Validation Results</div>
                <div class="ent-card-action">Compliance checklist</div>
            </div>
            {checks_body}
        </div>
        """).strip()
        st.markdown(sec_f_html, unsafe_allow_html=True)

    with c_reason:
        sec_g_html = textwrap.dedent(f"""
        <div class="ent-card">
            <div class="ent-card-header">
                <div class="ent-card-title">Section G — Decision Reasoning</div>
                <div class="ent-card-action">Audit trail statement</div>
            </div>
            <div style="font-size: 0.88rem; line-height: 1.55; color: #172B4D; background: #F9FAFC; padding: 0.85rem 1rem; border-radius: 6px; border-left: 3px solid #172B4D; margin-bottom: 0.75rem;">
                <b>Rationale:</b><br/>{explanation}
            </div>
            <div style="font-size: 0.82rem; color: #5E6C84;">
                <b>Actionable Next Step:</b> {action}
            </div>
        </div>
        """).strip()
        st.markdown(sec_g_html, unsafe_allow_html=True)

    # 6. SECTION H — Audit Timeline
    sec_h_header = textwrap.dedent("""
    <div class="ent-card" style="margin-bottom: 1rem;">
        <div class="ent-card-header">
            <div class="ent-card-title">Section H — Audit Timeline & Execution Stages</div>
            <div class="ent-card-action">Stage performance logs</div>
        </div>
    </div>
    """).strip()
    st.markdown(sec_h_header, unsafe_allow_html=True)

    stages = run.get("stages_log", [])
    if stages:
        stage_items = []
        for s in stages:
            stage_items.append({
                "Stage": f"{s.get('stage_id')}. {s.get('stage_name')}",
                "Status": s.get("status"),
                "Execution Details": s.get("message"),
                "Duration": f"{s.get('duration_ms', 0):.0f} ms"
            })
        st.dataframe(pd.DataFrame(stage_items), use_container_width=True, hide_index=True)

    # Download Report Button
    csv_report = ReportingService.generate_csv_report(run)
    st.download_button(
        label="Download decision report (CSV)",
        data=csv_report,
        file_name=f"InvoiceIQ_{run.get('run_id')}.csv",
        mime="text/csv",
        use_container_width=True
    )
