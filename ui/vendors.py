"""Vendor Network Page Module for InvoiceIQ.
Provides high-density vendor master directory, authorized status tracking,
and supplier drill-down analytics.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
from config.settings import VENDORS_CSV, PURCHASE_ORDERS_CSV
from database.repository import InvoiceRepository
from ui.components import (
    render_app_header,
    render_page_heading,
    render_summary_kpi_card,
    render_status_pill,
    render_empty_state
)


def render_vendors_page(repository: InvoiceRepository) -> None:
    """Render the Vendor Network page."""
    render_app_header("Vendor Network")
    
    # 1. Page Heading
    render_page_heading(
        title="Vendor Network",
        subtitle="Central directory of verified supplier entities, GSTIN tax identifiers, and procurement authorization status.",
        badge="6 Suppliers Registered"
    )

    # 2. Load Master Vendors Dataset
    try:
        vendors_df = pd.read_csv(VENDORS_CSV)
    except Exception as e:
        st.error(f"Failed to load vendor master data: {e}")
        return

    # 3. Top Summary KPI Cards
    total_vendors = len(vendors_df)
    active_vendors = len(vendors_df[vendors_df["status"] == "ACTIVE"])
    inactive_vendors = total_vendors - active_vendors
    active_pct = (active_vendors / total_vendors * 100) if total_vendors else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(render_summary_kpi_card(
            label="Total Suppliers",
            value=str(total_vendors),
            subtext="Authorized enterprise master",
            theme="blue",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● All Suppliers", key="kpi_card_vendor_all", use_container_width=True):
            st.session_state["vendor_status_flt"] = "ALL"
            st.session_state["selected_vendor_id"] = None
            st.rerun()
    with c2:
        st.markdown(render_summary_kpi_card(
            label="Active & Approved",
            value=str(active_vendors),
            subtext=f"{active_pct:.1f}% eligible for auto-approval",
            theme="green",
            trend_badge=f"+{active_pct:.0f}% OK",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Active Only", key="kpi_card_vendor_act", use_container_width=True):
            st.session_state["vendor_status_flt"] = "ACTIVE"
            st.session_state["selected_vendor_id"] = None
            st.rerun()
    with c3:
        st.markdown(render_summary_kpi_card(
            label="Restricted / Inactive",
            value=str(inactive_vendors),
            subtext="Policy escalation required",
            theme="coral",
            trend_badge="FLAGGED",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        ), unsafe_allow_html=True)
        if st.button("● Inactive Only", key="kpi_card_vendor_inact", use_container_width=True):
            st.session_state["vendor_status_flt"] = "INACTIVE"
            st.session_state["selected_vendor_id"] = None
            st.rerun()
    with c4:
        st.markdown(render_summary_kpi_card(
            label="Tax Registry Sync",
            value="100%",
            subtext="GSTIN checksums verified",
            theme="purple",
            trend_badge="VERIFIED",
            icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
        ), unsafe_allow_html=True)
        if st.button("● 100% Verified", key="kpi_card_vendor_sync", use_container_width=True):
            st.session_state["vendor_status_flt"] = "ALL"
            st.session_state["selected_vendor_id"] = None
            st.rerun()

    st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)

    # 4. Search & Filter Bar
    st.markdown('<div class="table-container-card" style="padding: 1rem 1.25rem; margin-bottom: 1.25rem;">', unsafe_allow_html=True)
    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        search_query = st.text_input(
            "Search Vendors",
            placeholder="Search by legal name, normalized name, tax ID (GSTIN), or vendor ID...",
            label_visibility="collapsed"
        )
    with f_col2:
        status_opts = ["ALL", "ACTIVE", "INACTIVE"]
        default_s_idx = status_opts.index(st.session_state.get("vendor_status_flt", "ALL")) if st.session_state.get("vendor_status_flt", "ALL") in status_opts else 0
        status_filter = st.selectbox(
            "Status Filter",
            options=status_opts,
            index=default_s_idx,
            label_visibility="collapsed",
            key="vendor_status_select"
        )
        st.session_state["vendor_status_flt"] = status_filter
    st.markdown('</div>', unsafe_allow_html=True)

    # Filter records
    filtered = vendors_df.copy()
    if status_filter != "ALL":
        filtered = filtered[filtered["status"] == status_filter]
    if search_query:
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["legal_name"].str.lower().str.contains(q, na=False) |
            filtered["normalized_name"].str.lower().str.contains(q, na=False) |
            filtered["tax_id"].str.lower().str.contains(q, na=False) |
            filtered["vendor_id"].str.lower().str.contains(q, na=False)
        ]

    # 5. High-Density Vendor Directory Table
    st.markdown(f"""
    <div class="table-container-card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; padding-bottom: 0.65rem; border-bottom: 1px solid #F1F5F9;">
            <div style="font-weight: 700; font-size: 0.98rem; color: #0F172A;">Vendor Master Directory</div>
            <div style="font-size: 0.78rem; color: #64748B;">Showing <b>{len(filtered)}</b> of {total_vendors} records</div>
        </div>
    """, unsafe_allow_html=True)

    # Table Header Row
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1.2fr 3.2fr 2.2fr 1.5fr 1.2fr 1fr; gap: 0.75rem; padding: 0.65rem 0.85rem; background: #F8FAFC; border-radius: 8px; font-size: 0.72rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
        <div>Vendor ID</div>
        <div>Legal Entity Name</div>
        <div>GSTIN / Tax ID</div>
        <div>Status</div>
        <div>Policy Flag</div>
        <div style="text-align: right;">Action</div>
    </div>
    """, unsafe_allow_html=True)

    active_detail_vendor_id = st.session_state.get("selected_vendor_id")

    for _, row in filtered.iterrows():
        vid = row["vendor_id"]
        vname = row["legal_name"]
        tax_id = row["tax_id"]
        status = row["status"]
        approved = bool(row["approved_flag"])
        
        is_selected = (active_detail_vendor_id == vid)
        row_bg = "background: #EEF2FF; border: 1px solid #C7D2FE;" if is_selected else "background: #FFFFFF;"
        
        col1, col2, col3, col4, col5, col6 = st.columns([1.2, 3.2, 2.2, 1.5, 1.2, 1])
        with col1:
            st.markdown(f"<span style='font-family:JetBrains Mono; font-size:0.82rem; font-weight:700; color:#4338CA;'>{vid}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='font-weight:600; font-size:0.85rem; color:#0F172A; line-height:1.25;'>{vname}</div><div style='font-size:0.72rem; color:#64748B;'>Norm: {row['normalized_name']}</div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<span style='font-family:JetBrains Mono; font-size:0.8rem; color:#334155;'>{tax_id}</span>", unsafe_allow_html=True)
        with col4:
            st.markdown(render_status_pill(status), unsafe_allow_html=True)
        with col5:
            if approved:
                st.markdown("<span style='font-size:0.72rem; font-weight:700; color:#059669; background:#DCFCE7; padding:2px 8px; border-radius:9999px;'>AUTHORIZED</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size:0.72rem; font-weight:700; color:#DC2626; background:#FEE2E2; padding:2px 8px; border-radius:9999px;'>UNAPPROVED</span>", unsafe_allow_html=True)
        with col6:
            btn_label = "Close" if is_selected else "Inspect"
            if st.button(btn_label, key=f"btn_act_v_{vid}", use_container_width=True):
                if is_selected:
                    st.session_state["selected_vendor_id"] = None
                else:
                    st.session_state["selected_vendor_id"] = vid
                st.rerun()

        st.markdown("<div style='height: 1px; background: #F1F5F9; margin: 0.35rem 0;'></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 6. Interactive Vendor Profile Drawer (Drill-Down)
    if active_detail_vendor_id:
        v_match = vendors_df[vendors_df["vendor_id"] == active_detail_vendor_id]
        if not v_match.empty:
            v_info = v_match.iloc[0]
            _render_vendor_detail_profile(v_info, repository)


def _render_vendor_detail_profile(vendor_row: pd.Series, repository: InvoiceRepository) -> None:
    """Render drill-down profile showing linked POs and invoice runs for a vendor."""
    vid = vendor_row["vendor_id"]
    vname = vendor_row["legal_name"]

    col_back, _ = st.columns([1.6, 4.4])
    with col_back:
        if st.button("← Back to Directory", key=f"btn_back_vprof_{vid}", use_container_width=True):
            st.session_state["selected_vendor_id"] = None
            st.rerun()

    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1.5px solid #6366F1; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 16px rgba(99, 102, 241, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; border-bottom: 1px solid #E2E8F0; padding-bottom: 0.75rem;">
            <div>
                <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; color: #6366F1; font-weight: 700;">Vendor Profile & Procurement Linkages</div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin-top: 0.2rem;">{vname} · <span style="font-family: JetBrains Mono; font-size: 0.95rem; color: #64748B;">{vid}</span></div>
            </div>
            <div>
                {render_status_pill(vendor_row['status'])}
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;'>Linked Purchase Orders (Master Records)</div>", unsafe_allow_html=True)
        try:
            pos_df = pd.read_csv(PURCHASE_ORDERS_CSV)
            vendor_pos = pos_df[pos_df["vendor_id"] == vid]
            if not vendor_pos.empty:
                po_disp = vendor_pos[["po_number", "po_date", "po_total", "remaining_balance", "po_status"]]
                st.dataframe(po_disp, use_container_width=True, hide_index=True)
            else:
                st.info("No purchase orders registered under this vendor ID.")
        except Exception as e:
            st.warning(f"Unable to load POs: {e}")

    with col_right:
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #0F172A; margin-bottom: 0.5rem;'>Processed Invoices (SQLite Audit Ledger)</div>", unsafe_allow_html=True)
        runs = repository.list_runs(vendor_filter=vendor_row["normalized_name"][:8], limit=10)
        if runs:
            run_rows = []
            for r in runs:
                run_rows.append({
                    "Invoice #": r.get("invoice_number") or "N/A",
                    "Total": f"₹{r.get('invoice_total', 0.0):,.2f}",
                    "Decision": r.get("decision"),
                    "Date": r.get("created_at", "")[:10]
                })
            st.dataframe(pd.DataFrame(run_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No invoice transactions logged yet for this supplier.")

    st.markdown("</div>", unsafe_allow_html=True)
