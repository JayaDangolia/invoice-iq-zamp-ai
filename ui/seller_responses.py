"""Seller Responses Module for InvoiceIQ.
Provides vendor communication, exception clarifications, submitted evidence review,
and buyer settlement actions.
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


def render_seller_responses_page(repository: InvoiceRepository) -> None:
    """Render the Seller Responses vendor collaboration page."""
    render_app_header("Seller Responses")

    responses = repository.list_seller_responses()
    pending_responses = [r for r in responses if r.get("status") == "PENDING_BUYER_ACTION"]
    resolved_responses = [r for r in responses if r.get("status") != "PENDING_BUYER_ACTION"]

    # 1. Page Heading
    render_page_heading(
        title="Seller Responses",
        subtitle="Manage supplier clarifications, submitted change order documentation, and exception disputes.",
        badge=f"{len(pending_responses)} Pending Buyer Action"
    )

    # 2. Top Summary KPI Cards (Pastel Style with 1-Click Interactive Drilldown)
    total_val_pending = sum(float(r.get("disputed_amount") or 0.0) for r in pending_responses)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_summary_kpi_card(
            label="Pending Action",
            value=str(len(pending_responses)),
            subtext="Supplier explanations awaiting review",
            theme="coral",
            trend_badge="ACTION REQ",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Pending Action", key="kpi_card_sr_pend", use_container_width=True):
            st.session_state["sr_filter"] = "PENDING"
            st.rerun()
    with c2:
        st.markdown(render_summary_kpi_card(
            label="Value at Clarification",
            value=f"₹{total_val_pending:,.0f}",
            subtext="Total amount under explanation",
            theme="blue",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Exposure View", key="kpi_card_sr_exp", use_container_width=True):
            st.session_state["sr_filter"] = "ALL"
            st.rerun()
    with c3:
        st.markdown(render_summary_kpi_card(
            label="Resolved Cases",
            value=str(len(resolved_responses)),
            subtext="Settled through collaboration",
            theme="green",
            trend_badge="SETTLED",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Resolved Ledger", key="kpi_card_sr_res", use_container_width=True):
            st.session_state["sr_filter"] = "RESOLVED"
            st.rerun()
    with c4:
        st.markdown(render_summary_kpi_card(
            label="Avg Response Turnaround",
            value="1.2 Days",
            subtext="Vendor submission speed",
            theme="purple",
            trend_badge="FAST",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● All Cases", key="kpi_card_sr_all", use_container_width=True):
            st.session_state["sr_filter"] = "ALL"
            st.rerun()

    sr_mode = st.session_state.get("sr_filter", "ALL")

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 3. Active Pending Responses Section
    st.markdown("""
    <div style="font-weight: 700; font-size: 1.1rem; color: #0F172A; margin-bottom: 0.85rem;">
        Pending Supplier Explanations
    </div>
    """, unsafe_allow_html=True)

    if not pending_responses:
        st.markdown("""
        <div class="table-container-card" style="padding: 2.5rem; text-align: center; color: #64748B;">
            <div style="font-weight: 600; color: #059669; font-size: 1.05rem; margin-bottom: 0.25rem;">All Vendor Responses Actioned</div>
            <div style="font-size: 0.85rem;">There are no outstanding supplier clarifications requiring buyer action.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for resp in pending_responses:
            resp_id = resp.get("response_id")
            vname = resp.get("vendor_name")
            inv_num = resp.get("invoice_number")
            po_num = resp.get("po_number") or "N/A"
            disc_type = resp.get("discrepancy_type")
            amt = float(resp.get("disputed_amount") or 0.0)
            expl = resp.get("vendor_explanation")
            evidence = resp.get("evidence_file")
            created = resp.get("created_at")

            card_html = (
                '<div class="table-container-card" style="padding: 1.35rem 1.6rem; margin-bottom: 0.85rem; border: 1.5px solid #CBD5E1; box-shadow: 0 4px 14px rgba(0,0,0,0.03);">'
                '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.85rem; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.75rem;">'
                '<div>'
                f'<div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #4338CA; font-weight: 700;">Case {resp_id} · Submitted {created}</div>'
                f'<div style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin-top: 0.2rem;">{vname} · Invoice <span style="font-family: JetBrains Mono; color: #1E293B;">{inv_num}</span></div>'
                f'<div style="font-size: 0.8rem; color: #64748B; margin-top: 0.15rem;">PO Reference: <b style="color: #334155;">{po_num}</b> · Disputed Amount: <b style="color: #0F172A;">₹{amt:,.2f}</b></div>'
                '</div>'
                '<div>'
                '<span class="badge-status-review">AWAITING BUYER DECISION</span>'
                '</div>'
                '</div>'
                '<div style="background: #F8FAFC; border-left: 4px solid #6366F1; border-radius: 0 8px 8px 0; padding: 0.95rem 1.15rem;">'
                f'<div style="font-size: 0.75rem; font-weight: 700; color: #4338CA; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem;">Exception: {disc_type}</div>'
                f'<div style="font-size: 0.88rem; color: #1E293B; line-height: 1.5;"><b>Vendor Clarification:</b> "{expl}"</div>'
                '<div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">'
                '<span style="font-size: 0.74rem; font-weight: 600; color: #64748B;">Attached Supporting Document:</span>'
                f'<span style="font-size: 0.74rem; font-weight: 600; color: #4338CA; background: #EEF2FF; border: 1px solid #C7D2FE; border-radius: 4px; padding: 2px 8px; font-family: monospace;">📄 {evidence}</span>'
                '</div>'
                '</div>'
                '</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            col_notes, col_btns = st.columns([2, 1.2])
            with col_notes:
                buyer_note = st.text_input(
                    "Buyer Review Rationale",
                    placeholder="Enter audit notes for settling or contesting this explanation...",
                    key=f"note_{resp_id}"
                )
            with col_btns:
                st.markdown("<div style='height: 1.7rem;'></div>", unsafe_allow_html=True)
                btn_accept, btn_credit = st.columns(2)
                with btn_accept:
                    if st.button("Accept & Settle", key=f"btn_acc_{resp_id}", type="primary", use_container_width=True):
                        note_to_save = buyer_note.strip() or "Accepted vendor explanation and supporting change order documentation."
                        repository.update_seller_response_action(
                            response_id=resp_id,
                            action="ACCEPTED_AND_APPROVED",
                            notes=note_to_save,
                            approve_invoice=True
                        )
                        st.success(f"Case {resp_id} settled and invoice approved in SQLite.")
                        st.rerun()
                with btn_credit:
                    if st.button("Request Credit Note", key=f"btn_cr_{resp_id}", use_container_width=True):
                        note_to_save = buyer_note.strip() or "Explanation rejected; formal credit note requested from vendor."
                        repository.update_seller_response_action(
                            response_id=resp_id,
                            action="REQUESTED_CREDIT_NOTE",
                            notes=note_to_save,
                            approve_invoice=False
                        )
                        st.warning(f"Credit note requested for Case {resp_id}.")
                        st.rerun()

            st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # 4. Resolved / Settled Responses History
    if resolved_responses:
        st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A; margin-bottom: 0.85rem;">
            Resolved Supplier Cases Ledger
        </div>
        """, unsafe_allow_html=True)
        
        hist_rows = []
        for r in resolved_responses:
            hist_rows.append({
                "Case ID": r.get("response_id"),
                "Vendor Legal Name": r.get("vendor_name"),
                "Invoice #": r.get("invoice_number"),
                "Disputed Value": f"₹{float(r.get('disputed_amount') or 0.0):,.2f}",
                "Status": r.get("status"),
                "Buyer Action": r.get("buyer_action"),
                "Settled At": r.get("updated_at") or r.get("created_at")
            })
        st.markdown('<div class="table-container-card" style="padding: 1.25rem 1.5rem;">', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
