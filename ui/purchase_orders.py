"""Purchase Orders Management Module for InvoiceIQ.
Provides high-density procurement commitments, line-item inspection,
and remaining balance tracking.
"""

from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
from config.settings import PURCHASE_ORDERS_CSV, PO_LINE_ITEMS_CSV, VENDORS_CSV
from database.repository import InvoiceRepository
from ui.components import (
    render_app_header,
    render_page_heading,
    render_summary_kpi_card,
    render_status_pill,
    render_empty_state
)


def render_po_page(repository: InvoiceRepository) -> None:
    """Render the PO Management page."""
    render_app_header("PO Management")

    # 1. Page Heading
    render_page_heading(
        title="PO Management",
        subtitle="Authorized procurement commitments, itemized line items, and cumulative balance tracking.",
        badge="9 POs Master"
    )

    # 2. Load PO Datasets
    try:
        po_df = pd.read_csv(PURCHASE_ORDERS_CSV)
        line_items_df = pd.read_csv(PO_LINE_ITEMS_CSV)
        vendors_df = pd.read_csv(VENDORS_CSV)
        # Create vendor name mapping
        vendor_map = dict(zip(vendors_df["vendor_id"], vendors_df["legal_name"]))
    except Exception as e:
        st.error(f"Failed to load purchase order master records: {e}")
        return

    # 3. Top Summary KPI Cards
    total_committed = po_df["po_total"].sum()
    total_remaining = po_df["remaining_balance"].sum()
    open_pos = len(po_df[po_df["po_status"] == "OPEN"])
    closed_pos = len(po_df[po_df["po_status"] == "CLOSED"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_summary_kpi_card(
            label="Total Committed",
            value=f"₹{total_committed:,.0f}",
            subtext="Procurement budget ceiling",
            theme="blue",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line></svg>'
        ), unsafe_allow_html=True)
        if st.button("● All POs", key="kpi_card_po_all", use_container_width=True):
            st.session_state["po_status_flt"] = "ALL"
            st.session_state["selected_po_num"] = None
            st.rerun()
    with c2:
        st.markdown(render_summary_kpi_card(
            label="Open Commitments",
            value=str(open_pos),
            subtext="Available for invoice matching",
            theme="green",
            trend_badge="ACTIVE",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Open Commitments", key="kpi_card_po_open", use_container_width=True):
            st.session_state["po_status_flt"] = "OPEN"
            st.session_state["selected_po_num"] = None
            st.rerun()
    with c3:
        st.markdown(render_summary_kpi_card(
            label="Remaining Balance",
            value=f"₹{total_remaining:,.0f}",
            subtext="Unbilled commitment pool",
            theme="purple",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Unbilled Bal", key="kpi_card_po_rem", use_container_width=True):
            st.session_state["po_status_flt"] = "OPEN"
            st.session_state["selected_po_num"] = None
            st.rerun()
    with c4:
        st.markdown(render_summary_kpi_card(
            label="Closed / Depleted",
            value=str(closed_pos),
            subtext="Zero balance remaining",
            theme="coral",
            trend_badge="EXHAUSTED",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Closed Only", key="kpi_card_po_closed", use_container_width=True):
            st.session_state["po_status_flt"] = "CLOSED"
            st.session_state["selected_po_num"] = None
            st.rerun()

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 4. Search & Filter Bar
    st.markdown('<div class="table-container-card" style="padding: 1rem 1.25rem; margin-bottom: 1.25rem;">', unsafe_allow_html=True)
    f1, f2 = st.columns([3, 1])
    with f1:
        po_search = st.text_input(
            "Search Purchase Orders",
            placeholder="Search by PO number (e.g. PO-2024-001) or vendor ID...",
            label_visibility="collapsed"
        )
    with f2:
        po_opts = ["ALL", "OPEN", "CLOSED"]
        default_po_idx = po_opts.index(st.session_state.get("po_status_flt", "ALL")) if st.session_state.get("po_status_flt", "ALL") in po_opts else 0
        po_filter = st.selectbox(
            "PO Status Filter",
            options=po_opts,
            index=default_po_idx,
            label_visibility="collapsed",
            key="po_status_select"
        )
        st.session_state["po_status_flt"] = po_filter
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter records
    filtered_pos = po_df.copy()
    if po_filter != "ALL":
        filtered_pos = filtered_pos[filtered_pos["po_status"] == po_filter]
    if po_search:
        q = po_search.strip().lower()
        filtered_pos = filtered_pos[
            filtered_pos["po_number"].str.lower().str.contains(q, na=False) |
            filtered_pos["vendor_id"].str.lower().str.contains(q, na=False)
        ]

    # 5. High-Density PO Master Table
    st.markdown(f"""
    <div class="table-container-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; padding-bottom: 0.65rem; border-bottom: 1px solid #F1F5F9;">
            <div style="font-weight: 700; font-size: 0.98rem; color: #0F172A;">Procurement Purchase Orders</div>
            <div style="font-size: 0.78rem; color: #64748B;">Showing <b>{len(filtered_pos)}</b> of {len(po_df)} purchase orders</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="display: grid; grid-template-columns: 1.4fr 2.6fr 1.1fr 1.3fr 1.8fr 1.1fr 1fr; gap: 0.75rem; padding: 0.65rem 0.85rem; background: #F8FAFC; border-radius: 8px; font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
        <div>PO Number</div>
        <div>Vendor Supplier</div>
        <div>PO Date</div>
        <div>Total Value</div>
        <div>Remaining Balance</div>
        <div>Status</div>
        <div style="text-align: right;">Action</div>
    </div>
    """, unsafe_allow_html=True)

    active_po = st.session_state.get("selected_po_num")

    for _, row in filtered_pos.iterrows():
        po_num = row["po_number"]
        vid = row["vendor_id"]
        vname = vendor_map.get(vid, vid)
        p_date = row["po_date"]
        p_tot = float(row["po_total"])
        p_rem = float(row["remaining_balance"])
        p_stat = row["po_status"]

        is_selected = (active_po == po_num)
        rem_pct = min(max((p_rem / p_tot * 100), 0), 100) if p_tot > 0 else 0
        bar_color = "#10B981" if rem_pct > 30 else ("#F59E0B" if rem_pct > 0 else "#EF4444")

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1.4, 2.6, 1.1, 1.3, 1.8, 1.1, 1])
        with col1:
            st.markdown(f"<span style='font-family:JetBrains Mono; font-size:0.82rem; font-weight:700; color:#4338CA;'>{po_num}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='font-weight:600; font-size:0.82rem; color:#0F172A;'>{vname}</div><div style='font-size:0.7rem; color:#64748B;'>{vid}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='font-size:0.78rem; color:#475569;'>{p_date}</span>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<span style='font-weight:700; font-size:0.82rem; color:#0F172A;'>₹{p_tot:,.2f}</span>", unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div style="width: 100%;">
                <div style="display: flex; justify-content: space-between; font-size: 0.72rem; margin-bottom: 2px;">
                    <span style="font-weight:600; color:#1E293B;">₹{p_rem:,.0f}</span>
                    <span style="color:#64748B;">{rem_pct:.0f}%</span>
                </div>
                <div style="width: 100%; height: 5px; background: #E2E8F0; border-radius: 9999px; overflow: hidden;">
                    <div style="width: {rem_pct}%; height: 100%; background: {bar_color}; border-radius: 9999px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col6:
            st.markdown(render_status_pill(p_stat), unsafe_allow_html=True)
        with col7:
            btn_txt = "Close" if is_selected else "Lines"
            if st.button(btn_txt, key=f"btn_act_po_{po_num}", use_container_width=True):
                if is_selected:
                    st.session_state["selected_po_num"] = None
                else:
                    st.session_state["selected_po_num"] = po_num
                st.rerun()

        st.markdown("<div style='height: 1px; background: #F1F5F9; margin: 0.35rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 6. Interactive Drill-Down Workspace (Line Items & Billing Ledger)
    if active_po:
        _render_po_line_items_detail(active_po, line_items_df, repository)


def _render_po_line_items_detail(po_number: str, line_items_df: pd.DataFrame, repository: InvoiceRepository) -> None:
    """Render line items breakdown and cumulative billing ledger for a specific PO."""
    po_lines = line_items_df[line_items_df["po_number"] == po_number]

    col_back, _ = st.columns([1.6, 4.4])
    with col_back:
        if st.button("← Back to PO List", key=f"btn_back_po_{po_number}", use_container_width=True):
            st.session_state["selected_po_num"] = None
            st.rerun()

    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1.5px solid #6366F1; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.75rem;">
            <div>
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: #6366F1; font-weight: 700;">Purchase Order Line Items Breakdown</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-top: 0.2rem;">Commitment Schedule · <span style="font-family: JetBrains Mono; font-size: 1.05rem; color: #4338CA;">{po_number}</span></div>
            </div>
            <div style="font-size: 0.8rem; color: #64748B;">
                {len(po_lines)} itemized schedule line(s)
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_lines, col_invoices = st.columns([1.3, 1])

    with col_lines:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;'>Authorized Schedule Lines</div>", unsafe_allow_html=True)
        if not po_lines.empty:
            disp_lines = po_lines[["item_id", "description", "quantity", "unit_price", "line_total", "tax_rate"]].copy()
            disp_lines["unit_price"] = disp_lines["unit_price"].apply(lambda v: f"₹{float(v):,.2f}")
            disp_lines["line_total"] = disp_lines["line_total"].apply(lambda v: f"₹{float(v):,.2f}")
            disp_lines["tax_rate"] = disp_lines["tax_rate"].apply(lambda v: f"{float(v)*100:.0f}%")
            st.dataframe(disp_lines, use_container_width=True, hide_index=True)
        else:
            st.info("No itemized schedule lines registered for this PO.")

    with col_invoices:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;'>Cumulative Invoices Billed (SQLite Ledger)</div>", unsafe_allow_html=True)
        billed_invoices = repository.get_accepted_invoices_for_po(po_number)
        if billed_invoices:
            inv_rows = []
            for inv in billed_invoices:
                inv_rows.append({
                    "Invoice #": inv.get("invoice_number"),
                    "Billed Total": f"₹{float(inv.get('invoice_total') or 0.0):,.2f}",
                    "Status": inv.get("decision"),
                    "Date": str(inv.get("created_at"))[:10]
                })
            st.dataframe(pd.DataFrame(inv_rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"No accepted invoices currently billed against {po_number}.")

    st.markdown("</div>", unsafe_allow_html=True)
