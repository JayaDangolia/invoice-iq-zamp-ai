"""Disputes & Resolutions Module for InvoiceIQ.
Provides high-density AP dispute tracking, discrepancy categorization,
and settlement resolution workflows.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
from database.repository import InvoiceRepository
from ui.components import (
    render_app_header,
    render_page_heading,
    render_summary_kpi_card,
    render_status_pill,
    render_empty_state
)


def render_disputes_page(repository: InvoiceRepository) -> None:
    """Render the Disputes & Resolutions page."""
    render_app_header("Disputes & Resolutions")

    disputes = repository.list_disputes()
    open_disputes = [d for d in disputes if d.get("status") == "OPEN"]
    resolved_disputes = [d for d in disputes if d.get("status") == "RESOLVED"]

    # 1. Page Heading
    render_page_heading(
        title="Disputes & Resolutions",
        subtitle="Comprehensive log of disputed invoice items, short payments, and credit note reconciliations.",
        badge=f"{len(disputes)} Total Cases"
    )

    # 2. Top Summary KPI Cards
    total_disputed_val = sum(float(d.get("disputed_amount") or 0.0) for d in disputes)
    open_val = sum(float(d.get("disputed_amount") or 0.0) for d in open_disputes)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_summary_kpi_card(
            label="Total Disputes",
            value=str(len(disputes)),
            subtext="Tracked procurement exceptions",
            theme="blue",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v1"></path><path d="M18 8h4a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-4"></path><path d="M7 11h6"></path><path d="M7 15h4"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● All Disputes", key="kpi_card_dsp_all", use_container_width=True):
            st.session_state["dispute_status_flt"] = "ALL"
            st.session_state["selected_dispute_id"] = None
            st.rerun()
    with c2:
        st.markdown(render_summary_kpi_card(
            label="Open & Unresolved",
            value=str(len(open_disputes)),
            subtext=f"₹{open_val:,.0f} value pending agreement",
            theme="coral",
            trend_badge="ATTENTION",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Open Claims", key="kpi_card_dsp_open", use_container_width=True):
            st.session_state["dispute_status_flt"] = "OPEN"
            st.session_state["selected_dispute_id"] = None
            st.rerun()
    with c3:
        st.markdown(render_summary_kpi_card(
            label="Settled & Resolved",
            value=str(len(resolved_disputes)),
            subtext="Closed per settlement terms",
            theme="green",
            trend_badge="CLOSED",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Settled Claims", key="kpi_card_dsp_res", use_container_width=True):
            st.session_state["dispute_status_flt"] = "RESOLVED"
            st.session_state["selected_dispute_id"] = None
            st.rerun()
    with c4:
        st.markdown(render_summary_kpi_card(
            label="Cumulative Disputed",
            value=f"₹{total_disputed_val:,.0f}",
            subtext="Total dispute exposure",
            theme="purple",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Exposure View", key="kpi_card_dsp_exp", use_container_width=True):
            st.session_state["dispute_status_flt"] = "OPEN"
            st.session_state["selected_dispute_id"] = None
            st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Filter Bar
    st.markdown('<div class="table-container-card" style="padding: 1rem 1.25rem; margin-bottom: 1.25rem;">', unsafe_allow_html=True)
    f1, f2 = st.columns([3, 1])
    with f1:
        search_d = st.text_input(
            "Search Disputes",
            placeholder="Search by vendor name, invoice number, dispute ID, or reason...",
            label_visibility="collapsed"
        )
    with f2:
        dsp_opts = ["ALL", "OPEN", "RESOLVED"]
        default_d_idx = dsp_opts.index(st.session_state.get("dispute_status_flt", "ALL")) if st.session_state.get("dispute_status_flt", "ALL") in dsp_opts else 0
        status_d = st.selectbox(
            "Dispute Status Filter",
            options=dsp_opts,
            index=default_d_idx,
            label_visibility="collapsed",
            key="dsp_status_select"
        )
        st.session_state["dispute_status_flt"] = status_d
    st.markdown('</div>', unsafe_allow_html=True)

    filtered_disputes = disputes
    if status_d != "ALL":
        filtered_disputes = [d for d in filtered_disputes if d.get("status") == status_d]
    if search_d:
        sq = search_d.strip().lower()
        filtered_disputes = [
            d for d in filtered_disputes
            if sq in str(d.get("vendor_name", "")).lower() or
               sq in str(d.get("invoice_number", "")).lower() or
               sq in str(d.get("dispute_id", "")).lower() or
               sq in str(d.get("dispute_category", "")).lower()
        ]

    # 4. High-Density Disputes Table
    st.markdown(f"""
    <div class="table-container-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; padding-bottom: 0.65rem; border-bottom: 1px solid #F1F5F9;">
            <div style="font-weight: 700; font-size: 0.98rem; color: #0F172A;">Disputes & Claims Register</div>
            <div style="font-size: 0.78rem; color: #64748B;">Showing <b>{len(filtered_disputes)}</b> of {len(disputes)} cases</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: grid; grid-template-columns: 1.2fr 2.6fr 1.6fr 1.6fr 1.3fr 1.1fr 1fr; gap: 0.75rem; padding: 0.65rem 0.85rem; background: #F8FAFC; border-radius: 8px; font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
        <div>Dispute ID</div>
        <div>Vendor Supplier</div>
        <div>Invoice & PO</div>
        <div>Category</div>
        <div>Amount</div>
        <div>Status</div>
        <div style="text-align: right;">Action</div>
    </div>
    """, unsafe_allow_html=True)

    active_dispute_id = st.session_state.get("selected_dispute_id")

    for d in filtered_disputes:
        did = d.get("dispute_id")
        vname = d.get("vendor_name")
        inv_num = d.get("invoice_number")
        po_num = d.get("po_number") or "None"
        cat = d.get("dispute_category")
        amt = float(d.get("disputed_amount") or 0.0)
        d_stat = d.get("status")

        is_selected = (active_dispute_id == did)
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.2, 2.6, 1.6, 1.6, 1.3, 1.1, 1])
        with col1:
            st.markdown(f"<span style='font-family:JetBrains Mono; font-size:0.82rem; font-weight:700; color:#4338CA;'>{did}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:#0F172A;'>{vname}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div style='font-size:0.8rem; font-weight:600; color:#1E293B;'>{inv_num}</div><div style='font-size:0.7rem; color:#64748B;'>PO: {po_num}</div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<span style='font-size:0.78rem; color:#475569;'>{cat}</span>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"<span style='font-weight:700; font-size:0.82rem; color:#0F172A;'>₹{amt:,.2f}</span>", unsafe_allow_html=True)
        with col6:
            st.markdown(render_status_pill(d_stat), unsafe_allow_html=True)
        with col7:
            btn_txt = "Close" if is_selected else ("Resolve" if d_stat == "OPEN" else "View")
            if st.button(btn_txt, key=f"btn_act_dsp_{did}", use_container_width=True):
                if is_selected:
                    st.session_state["selected_dispute_id"] = None
                else:
                    st.session_state["selected_dispute_id"] = did
                st.rerun()

        st.markdown("<div style='height: 1px; background: #F1F5F9; margin: 0.35rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 5. Interactive Dispute Settlement Workspace
    if active_dispute_id:
        target_d = next((x for x in disputes if x.get("dispute_id") == active_dispute_id), None)
        if target_d:
            _render_dispute_workspace(target_d, repository)


def _render_dispute_workspace(dispute: Dict[str, Any], repository: InvoiceRepository) -> None:
    """Render the dispute inspection and resolution workspace."""
    did = dispute.get("dispute_id")
    vname = dispute.get("vendor_name")
    amt = float(dispute.get("disputed_amount") or 0.0)
    status = dispute.get("status")

    col_back, _ = st.columns([1.6, 4.4])
    with col_back:
        if st.button("← Back to Claims Register", key=f"btn_back_dsp_{did}", use_container_width=True):
            st.session_state["selected_dispute_id"] = None
            st.rerun()

    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1.5px solid #6366F1; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.75rem;">
            <div>
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: #6366F1; font-weight: 700;">Dispute Resolution Workspace</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-top: 0.2rem;">{vname} · <span style="font-family: JetBrains Mono; font-size: 1.05rem; color: #4338CA;">Case {did}</span></div>
            </div>
            <div>
                {render_status_pill(status)}
            </div>
        </div>
    """, unsafe_allow_html=True)

    c_left, c_right = st.columns([1.2, 1])

    with c_left:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;'>Dispute Diagnostics</div>", unsafe_allow_html=True)
        diag_html = (
            '<div style="background: #F8FAFC; border-radius: 8px; padding: 1rem; font-size: 0.85rem; color: #334155;">'
            f'<div style="margin-bottom: 0.4rem;"><b>Dispute Category:</b> {dispute.get("dispute_category")}</div>'
            f'<div style="margin-bottom: 0.4rem;"><b>Invoice Number:</b> {dispute.get("invoice_number")}</div>'
            f'<div style="margin-bottom: 0.4rem;"><b>Purchase Order:</b> {dispute.get("po_number") or "None"}</div>'
            f'<div style="margin-bottom: 0.4rem;"><b>Disputed Exposure:</b> ₹{amt:,.2f}</div>'
            f'<div><b>Created At:</b> {dispute.get("created_at")}</div>'
            '</div>'
        )
        st.markdown(diag_html, unsafe_allow_html=True)

    with c_right:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;'>Settlement Action</div>", unsafe_allow_html=True)
        if status == "OPEN":
            res_note = st.text_area(
                "Settlement Rationale & Terms *",
                placeholder="Enter agreed terms, credit note number, or negotiated discount...",
                key=f"d_res_note_{did}"
            )
            if st.button("Resolve & Close Dispute", type="primary", use_container_width=True, key=f"btn_close_d_{did}"):
                if not res_note.strip():
                    st.warning("Please provide settlement terms before closing.")
                else:
                    repository.resolve_dispute(did, res_note.strip())
                    st.success(f"Dispute {did} resolved and marked CLOSED in SQLite.")
                    st.session_state["selected_dispute_id"] = None
                    st.rerun()
        else:
            settled_html = (
                '<div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 1rem; font-size: 0.85rem; color: #166534;">'
                '<div style="font-weight: 700; margin-bottom: 0.35rem;">Case Resolved & Closed</div>'
                f'<div style="margin-bottom: 0.35rem;"><b>Resolved At:</b> {dispute.get("resolved_at")}</div>'
                f'<div><b>Settlement Summary:</b> {dispute.get("resolution_summary")}</div>'
                '</div>'
            )
            st.markdown(settled_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
