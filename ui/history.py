from typing import Any, Dict, List, Optional
import streamlit as st
import pandas as pd
from database.repository import InvoiceRepository
from services.reporting_service import ReportingService
from ui.components import (
    render_app_header,
    render_page_heading,
    render_summary_kpi_card,
    render_status_pill,
    render_empty_state
)

def render_history_page(
    repository: InvoiceRepository,
    selected_run_id: Optional[str] = None
) -> None:
    # 1. Top Enterprise Breadcrumb Bar
    render_app_header("Invoices & History")

    # 2. Filter Bar
    st.markdown('<div class="table-container-card" style="padding: 1rem 1.25rem; margin-bottom: 1.25rem;">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3 = st.columns([2.5, 1.2, 1.3])

    with f_col1:
        search_query = st.text_input(
            "Search Records",
            placeholder="Search by Invoice #, Run ID, Vendor name...",
            label_visibility="collapsed"
        )
    with f_col2:
        decision_filter = st.selectbox(
            "Status Filter",
            options=["ALL", "APPROVED", "PENDING REVIEW", "REJECTED"],
            index=0,
            label_visibility="collapsed"
        )
    with f_col3:
        vendor_filter = st.selectbox(
            "Vendor Filter",
            options=["ALL", "TechCorp", "Apex Cloud", "GreenLogistics", "Bharat Security", "Synergy", "Quantum"],
            index=0,
            label_visibility="collapsed"
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. Query Runs
    runs = repository.list_runs(
        decision_filter=decision_filter if decision_filter != "ALL" else None,
        vendor_filter=vendor_filter if vendor_filter != "ALL" else None,
        search_query=search_query if search_query else None,
        limit=100
    )

    # 4. Page Title Header
    render_page_heading(
        title="Invoices & History",
        subtitle="Complete transaction ledger, 11-stage pipeline execution logs, and compliance audit trail.",
        badge=f"{len(runs)} Audit Records"
    )

    if not runs:
        render_empty_state(
            title="No Matching Records Found",
            description="No invoice processing runs matched the current search criteria or the database is empty."
        )
        return

    # 5. Top Summary Metrics (Pastel Cards)
    total_val = sum(float(r.get("invoice_total") or 0.0) for r in runs)
    avg_duration = sum(float(r.get("duration_ms") or 0.0) for r in runs) / max(len(runs), 1)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(render_summary_kpi_card(
            label="Total Ledger Records",
            value=str(len(runs)),
            subtext="Matches found in SQLite audit store",
            theme="blue",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● All Ledger Runs", key="kpi_card_hist_all", use_container_width=True):
            st.session_state["history_status_flt"] = "ALL"
            st.rerun()
    with m2:
        st.markdown(render_summary_kpi_card(
            label="Aggregate Volume",
            value=f"₹{total_val:,.2f}",
            subtext="Total transaction volume listed",
            theme="green",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Transaction Volume", key="kpi_card_hist_vol", use_container_width=True):
            st.session_state["history_status_flt"] = "ALL"
            st.rerun()
    with m3:
        st.markdown(render_summary_kpi_card(
            label="Avg Pipeline Latency",
            value=f"{avg_duration:.0f} ms",
            subtext="End-to-end execution speed",
            theme="purple",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Execution Speed", key="kpi_card_hist_perf", use_container_width=True):
            st.session_state["history_status_flt"] = "ALL"
            st.rerun()

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    if selected_run_id:
        col_b, _ = st.columns([1.6, 4.4])
        with col_b:
            if st.button("← Back to Full History", key="btn_back_full_hist", use_container_width=True):
                st.session_state["active_run_id"] = None
                st.rerun()

    # 6. Render Runs List
    st.markdown(f"<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 0.75rem; font-weight: 600;'>Showing <b>{len(runs)}</b> execution record(s)</div>", unsafe_allow_html=True)

    for run in runs:
        run_title = f"{run.get('decision')} · {run.get('invoice_number') or 'N/A'} · {run.get('vendor_name') or 'Unknown'} (₹{run.get('invoice_total', 0.0):,.2f}) — {run.get('run_id')}"
        is_expanded = (selected_run_id == run.get("run_id"))

        with st.expander(run_title, expanded=is_expanded):
            _render_run_details(run, repository)


def _render_run_details(run: Dict[str, Any], repository: InvoiceRepository) -> None:
    badge_html = render_status_pill(run.get("decision", ""))
    
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.75rem;">
        <div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">Run Identifier: <code style="color: #4338CA;">{run.get('run_id')}</code></div>
            <div style="font-size: 0.8rem; color: #64748B; margin-top: 0.2rem;">Processed on {run.get('created_at')} · Latency: <b>{run.get('duration_ms', 0):.0f} ms</b> · Mode: <code>{run.get('extraction_mode')}</code></div>
        </div>
        <div>
            {badge_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Decision Summary
    st.markdown(f"""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
        <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.3rem;"><b>Decision Policy Code:</b> <code>{run.get('reason_code')}</code></div>
        <div style="font-size: 0.85rem; color: #1E293B; margin-bottom: 0.3rem;"><b>Explanation:</b> {run.get('explanation')}</div>
        <div style="font-size: 0.85rem; color: #4338CA;"><b>Recommended Action:</b> {run.get('recommended_action')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Human Reviewer Resolution if present
    if run.get("reviewer_decision"):
        st.markdown(f"""
        <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-left: 4px solid #16A34A; border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 1rem;">
            <div style="font-weight: 700; color: #166534; font-size: 0.88rem;">Human Reviewer Resolution: {run.get('reviewer_decision')}</div>
            <div style="font-size: 0.8rem; color: #14532D; margin-top: 0.2rem;"><b>Resolved At:</b> {run.get('reviewed_at')}</div>
            <div style="font-size: 0.85rem; color: #14532D; margin-top: 0.4rem;"><b>Reviewer Notes:</b> {run.get('reviewer_notes')}</div>
        </div>
        """, unsafe_allow_html=True)

    # 11-Stage Log Table
    st.markdown("<div style='font-weight: 700; font-size: 0.92rem; color: #1E293B; margin: 1rem 0 0.5rem 0;'>11-Stage Pipeline Execution Performance</div>", unsafe_allow_html=True)
    stages = run.get("stages_log", [])
    if stages:
        stage_rows = []
        for s in stages:
            stage_rows.append({
                "Stage": f"{s.get('stage_id')}. {s.get('stage_name')}",
                "Status": s.get("status"),
                "Execution Details": s.get("message"),
                "Duration": f"{s.get('duration_ms', 0):.0f} ms"
            })
        st.dataframe(pd.DataFrame(stage_rows), use_container_width=True, hide_index=True)

    # Immutable Audit Trail Events
    st.markdown("<div style='font-weight: 700; font-size: 0.92rem; color: #1E293B; margin: 1.25rem 0 0.5rem 0;'>Immutable Audit Trail Events (SQLite)</div>", unsafe_allow_html=True)
    audit_events = repository.get_audit_events(run.get("run_id"))
    if audit_events:
        evt_rows = []
        for e in audit_events:
            evt_rows.append({
                "Timestamp": e.get("timestamp"),
                "Event ID": e.get("event_id"),
                "Actor": e.get("actor"),
                "Event Type": e.get("event_type"),
                "Details": str(e.get("details"))
            })
        st.dataframe(pd.DataFrame(evt_rows), use_container_width=True, hide_index=True)

    # Download CSV Report
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    csv_report = ReportingService.generate_csv_report(run)
    st.download_button(
        label=f"Download Audit Report ({run.get('run_id')}.csv)",
        data=csv_report,
        file_name=f"AuditReport_{run.get('run_id')}.csv",
        mime="text/csv",
        key=f"dl_hist_{run.get('run_id')}"
    )
