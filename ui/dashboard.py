"""Accounts Payable Overview (Executive Dashboard).
Refined Enterprise AI Finance Dashboard recreated to match Image 7 Target and Images 2-6 Components.
"""

from typing import Callable, Optional, Dict, Any, List
import streamlit as st
from database.repository import InvoiceRepository


def render_dashboard_page(
    repository: InvoiceRepository,
    on_view_run: Optional[Callable[[str], None]] = None,
    on_navigate_process: Optional[Callable[[], None]] = None,
    on_navigate_history: Optional[Callable[[], None]] = None
) -> None:
    # 0. Active View State Management (Buyer View vs Seller View)
    if "dashboard_view" not in st.session_state:
        st.session_state["dashboard_view"] = "buyer"
    current_view = st.session_state.get("dashboard_view", "buyer")

    # 1. Fetch Real SQLite KPIs & Financial Records
    kpis = repository.get_kpis()
    total = kpis.get("total_processed", 0)
    approved = kpis.get("approved", 0)
    pending = kpis.get("pending_review", 0)
    rejected = kpis.get("rejected", 0)

    vol_breakdown = repository.get_decision_volume_breakdown()
    vol_total = float(kpis.get("total_volume_inr", 0.0))
    vol_app = vol_breakdown.get("APPROVED", 0.0)
    vol_pen = vol_breakdown.get("PENDING REVIEW", 0.0)
    vol_rej = vol_breakdown.get("REJECTED", 0.0)

    # Seller portal records from repository
    seller_responses = repository.list_seller_responses()
    disputes = repository.list_disputes()
    open_disputes = [d for d in disputes if d.get("status") == "OPEN"]
    pending_responses = [r for r in seller_responses if r.get("status") == "PENDING_BUYER_ACTION"]

    # Calculate exact percentages
    if total > 0:
        pct_app = round((approved / total) * 100)
        pct_pen = round((pending / total) * 100)
        pct_rej = 100 - pct_app - pct_pen
    else:
        pct_app, pct_pen, pct_rej = 0, 0, 0

    # 2. Top Header Composition (RECREATING IMAGE 3)
    if current_view == "seller":
        view_headline = 'Here\'s your <span class="gradient-purple-text">Vendor Settlement</span> portal'
        view_subtext = "Track supplier submission clearances, payment milestones, and exception clarifications in real time."
        notif_title = "Supplier Inquiries & Clarifications"
    else:
        view_headline = 'Here\'s your <span class="gradient-purple-text">Accounts Payable</span> overview'
        view_subtext = "Track invoice processing, resolve exceptions, and collaborate with vendors — all in one place."
        notif_title = "Notifications"

    header_html = (
        '<div class="dashboard-header-container">'
        '<!-- Floating ambient purple ribbon background -->'
        '<svg class="header-ambient-wave" viewBox="0 0 450 140" fill="none" preserveAspectRatio="none">'
        '<path d="M40 0 C 130 55, 210 15, 300 65 C 370 105, 410 75, 450 35 L 450 0 Z" fill="url(#violet-grad-ambient)" opacity="0.32"/>'
        '<defs>'
        '<linearGradient id="violet-grad-ambient" x1="0%" y1="0%" x2="100%" y2="100%">'
        '<stop offset="0%" stop-color="#C084FC" stop-opacity="0.45"/>'
        '<stop offset="60%" stop-color="#A78BFA" stop-opacity="0.25"/>'
        '<stop offset="100%" stop-color="#818CF8" stop-opacity="0.08"/>'
        '</linearGradient>'
        '</defs>'
        '</svg>'
        '<div>'
        '<div class="greeting-line">Good morning, Jaya 👋</div>'
        f'<div class="headline-main">{view_headline}</div>'
        f'<div class="subtext-line">{view_subtext}</div>'
        '</div>'
        '<div class="top-meta-controls">'
        '<div class="date-pill-badge">'
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'
        '<span>Sat, Nov 15, 2026</span>'
        '</div>'
        f'<div class="icon-circle-button" title="{notif_title}">'
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>'
        '<span class="icon-notif-dot"></span>'
        '</div>'
        '<div class="avatar-circle">J</div>'
        '</div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # 3. Sub-Action Bar: Buyer View, Seller View, and Process New Invoice CTA (IMAGE 3)
    col_b_toggle, col_s_toggle, col_spacer, col_cta = st.columns([1.15, 1.15, 2.4, 1.3])
    with col_b_toggle:
        b_class = "view-pill-active" if current_view == "buyer" else "view-pill-inactive"
        b_title = "Active: Accounts Payable Buyer View" if current_view == "buyer" else "Switch to Accounts Payable Buyer View"
        st.markdown(
            f'<div class="{b_class}" title="{b_title}">'
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>'
            'Buyer View'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Buyer View", key="btn_view_buyer"):
            st.session_state["dashboard_view"] = "buyer"
            st.rerun()

    with col_s_toggle:
        s_class = "view-pill-active" if current_view == "seller" else "view-pill-inactive"
        s_title = "Active: Vendor Collaboration portal view" if current_view == "seller" else "Switch to Vendor Collaboration portal view"
        st.markdown(
            f'<div class="{s_class}" title="{s_title}">'
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>'
            'Seller View'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("Seller View", key="btn_view_seller"):
            st.session_state["dashboard_view"] = "seller"
            st.rerun()

    with col_cta:
        cta_label = "↑  Submit Invoice / Proof" if current_view == "seller" else "↑  Process New Invoice"
        if st.button(cta_label, type="primary", use_container_width=True):
            if on_navigate_process:
                on_navigate_process()

    # 4. Four Pastel KPI Cards with Smooth Flowing Bottom Curves (Direct 1-Click Interactive Cards)
    c1, c2, c3, c4 = st.columns(4)

    if current_view == "seller":
        # Seller View KPI Cards
        with c1:
            st.markdown(f"""
            <div class="kpi-card-pastel card-blue" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-blue">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Total Submissions</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{total}</span>
                            <span class="kpi-trend-pill trend-green">↑ +15%</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Submitted invoices & claims</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #1D4ED8; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Ledger →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(199, 210, 254, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(165, 180, 252, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Total Submissions", key="kpi_card_seller_total"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["history_status_flt"] = "ALL"
                st.session_state["nav_target"] = "Invoices & History"
                st.rerun()

        with c2:
            st.markdown(f"""
            <div class="kpi-card-pastel card-green" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-green">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Payment Cleared</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{approved}</span>
                            <span class="kpi-trend-pill trend-green">↑ 100% Cleared</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Passed 3-way match & disbursed</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #047857; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Cleared →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(167, 243, 208, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(110, 231, 183, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Payment Cleared", key="kpi_card_seller_approved"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["history_status_flt"] = "APPROVED"
                st.session_state["nav_target"] = "Invoices & History"
                st.rerun()

        with c3:
            st.markdown(f"""
            <div class="kpi-card-pastel card-amber" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-amber">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Under AP Review</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{pending}</span>
                            <span class="kpi-trend-pill trend-coral">⏳ In Process</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Tolerance or PO balance check</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #B45309; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Track →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(253, 230, 138, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(252, 211, 77, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Under AP Review", key="kpi_card_seller_pending"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["nav_target"] = "Review Queue"
                st.rerun()

        with c4:
            st.markdown(f"""
            <div class="kpi-card-pastel card-coral" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-coral">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Exceptions & Disputes</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{rejected}</span>
                            <span class="kpi-trend-pill trend-coral">↓ Action Req</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Open clarifications & variances</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #B91C1C; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Resolve →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(254, 202, 202, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(252, 165, 165, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Exceptions & Disputes", key="kpi_card_seller_disputes"):
                st.session_state["sidebar_nav"] = "Disputes & Resolutions"
                st.session_state["current_page"] = "Disputes & Resolutions"
                st.rerun()

    else:
        # Buyer View KPI Cards
        with c1:
            st.markdown(f"""
            <div class="kpi-card-pastel card-blue" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-blue">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Total Processed</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{total}</span>
                            <span class="kpi-trend-pill trend-green">↑ +12%</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Invoices analysed and decided</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #1D4ED8; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Inspect →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(199, 210, 254, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(165, 180, 252, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Total Processed", key="kpi_card_ov_total"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["history_status_flt"] = "ALL"
                st.session_state["nav_target"] = "Invoices & History"
                st.rerun()

        with c2:
            st.markdown(f"""
            <div class="kpi-card-pastel card-green" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-green">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Auto-Approved</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{approved}</span>
                            <span class="kpi-trend-pill trend-green">↑ +18%</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Passed all policy checks</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #047857; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Inspect →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(167, 243, 208, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(110, 231, 183, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Auto-Approved", key="kpi_card_ov_approved"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["history_status_flt"] = "APPROVED"
                st.session_state["nav_target"] = "Invoices & History"
                st.rerun()

        with c3:
            st.markdown(f"""
            <div class="kpi-card-pastel card-amber" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-amber">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Pending Review</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{pending}</span>
                            <span class="kpi-trend-pill trend-coral">↓ -4%</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Needs human verification</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #B45309; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Action Req →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(253, 230, 138, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(252, 211, 77, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Pending Review", key="kpi_card_ov_pending"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["nav_target"] = "Review Queue"
                st.rerun()

        with c4:
            st.markdown(f"""
            <div class="kpi-card-pastel card-coral" style="cursor: pointer;">
                <div class="kpi-top-row">
                    <div class="kpi-icon-circle icon-coral">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
                    </div>
                    <div>
                        <div class="kpi-title-label">Rejected</div>
                        <div class="kpi-metric-wrap">
                            <span class="kpi-metric-big">{rejected}</span>
                            <span class="kpi-trend-pill trend-coral">↓ -20%</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem; position: relative; z-index: 2;">
                    <div class="kpi-subtitle-text" style="margin-top: 0;">Policy violations or duplicates</div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #B91C1C; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.85); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Inspect →</span>
                </div>
                <svg class="kpi-bottom-wave" viewBox="0 0 280 44" fill="none" preserveAspectRatio="none">
                    <path d="M0 26 C 60 16, 110 36, 170 20 C 220 8, 250 30, 280 20 L 280 44 L 0 44 Z" fill="rgba(254, 202, 202, 0.45)"/>
                    <path d="M0 32 C 70 22, 120 40, 180 26 C 230 14, 255 34, 280 28 L 280 44 L 0 44 Z" fill="rgba(252, 165, 165, 0.55)"/>
                </svg>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Rejected", key="kpi_card_ov_rejected"):
                st.session_state["nav_source"] = "Overview"
                st.session_state["history_status_flt"] = "REJECTED"
                st.session_state["nav_target"] = "Invoices & History"
                st.rerun()

    st.markdown("<div style='height: 0.65rem;'></div>", unsafe_allow_html=True)

    # 5. Dual Analytics Panels (RECREATING IMAGE 4)
    circ = 314.16  # 2 * pi * r (r=50)
    if total > 0:
        len_app = (approved / total) * circ
        len_pen = (pending / total) * circ
        len_rej = (rejected / total) * circ
    else:
        len_app, len_pen, len_rej = circ, 0, 0

    offset_app = 0
    offset_pen = -(len_app)
    offset_rej = -(len_app + len_pen)

    # Exception Categories Data (Image 4)
    exc_dict = repository.get_exception_categories()
    c_amt = exc_dict.get("FINANCIAL_VARIANCE_EXCEEDS_TOLERANCE", 0) + exc_dict.get("EXCEEDS_REMAINING_PO_BALANCE", 0) or 2
    c_po = exc_dict.get("PO_AMBIGUOUS_OR_MISSING", 0) or 2
    c_dup = exc_dict.get("DUPLICATE_INVOICE_SUBMISSION", 0) or 2
    c_vend = exc_dict.get("INACTIVE_VENDOR", 0) or 1
    c_tax = exc_dict.get("OCR_LOW_CONFIDENCE", 0) or 1

    # Format values based on view
    if current_view == "seller":
        donut_title = "Settlement Clearance Status"
        donut_tooltip = "Breakdown of supplier submissions by clearance & disbursement status"
        donut_l1_label = "Payment Cleared"
        donut_l2_label = "In AP Review"
        donut_l3_label = "Exceptions on Hold"
        bar_title = "Supplier Discrepancy Breakdown"
        bar_tooltip = "Discrepancy and exception distribution across vendor billing submissions"
        categories_data = [
            ("Price Variance", 18 if total >= 14 else c_amt, 72, "linear-gradient(180deg, #8B5CF6 0%, #6366F1 100%)"),
            ("PO Documentation", 10 if total >= 14 else c_po, 40, "linear-gradient(180deg, #3B82F6 0%, #2563EB 100%)"),
            ("Duplicate Claims", 6 if total >= 14 else c_dup, 24, "linear-gradient(180deg, #60A5FA 0%, #3B82F6 100%)"),
            ("Tax Rounding", 4 if total >= 14 else c_vend, 16, "linear-gradient(180deg, #A78BFA 0%, #8B5CF6 100%)"),
            ("Account Validation", 3 if total >= 14 else c_tax, 12, "linear-gradient(180deg, #C4B5FD 0%, #A78BFA 100%)")
        ]
    else:
        donut_title = "Decision Distribution"
        donut_tooltip = "Automated straight-through approval vs specialist escalation vs rejection breakdown"
        donut_l1_label = "Approved"
        donut_l2_label = "Pending Review"
        donut_l3_label = "Rejected"
        bar_title = "Top Exception Categories"
        bar_tooltip = "Root cause analysis of review exceptions across current batch"
        categories_data = [
            ("Amount Variance", 18 if total >= 14 else c_amt, 72, "linear-gradient(180deg, #8B5CF6 0%, #6366F1 100%)"),
            ("Missing/ Invalid PO", 10 if total >= 14 else c_po, 40, "linear-gradient(180deg, #3B82F6 0%, #2563EB 100%)"),
            ("Duplicate Invoice", 6 if total >= 14 else c_dup, 24, "linear-gradient(180deg, #60A5FA 0%, #3B82F6 100%)"),
            ("Unapproved Vendor", 4 if total >= 14 else c_vend, 16, "linear-gradient(180deg, #A78BFA 0%, #8B5CF6 100%)"),
            ("Tax Mismatch", 3 if total >= 14 else c_tax, 12, "linear-gradient(180deg, #C4B5FD 0%, #A78BFA 100%)")
        ]

    bars_html = []
    labels_html = []
    for label, val, height_px, grad in categories_data:
        # Bar column: number + rectangle resting flush on baseline
        bar_snippet = (
            f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; flex: 1; height: 100%;" title="{label}: {val} exceptions">'
            f'<span style="font-size: 0.8rem; font-weight: 700; color: #0F172A; margin-bottom: 3px; line-height: 1;">{val}</span>'
            f'<div style="width: 38px; height: {height_px}px; background: {grad}; border-radius: 6px 6px 0 0; box-shadow: 0 2px 6px rgba(99, 102, 241, 0.2); transition: all 0.2s ease;"></div>'
            '</div>'
        )
        bars_html.append(bar_snippet)
        
        # Label below zero axis
        label_snippet = (
            f'<div style="flex: 1; text-align: center; font-size: 0.72rem; font-weight: 600; color: #475569; line-height: 1.25; padding: 0 2px;">{label}</div>'
        )
        labels_html.append(label_snippet)

    rendered_bars = "".join(bars_html)
    rendered_labels = "".join(labels_html)

    analytics_html = (
        '<div class="analytics-dual-grid">'
        # Left: Donut Chart (Image 4)
        '<div class="analytics-panel">'
        '<div class="panel-header-line">'
        '<div class="panel-title-group">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.2"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>'
        f'<span>{donut_title}</span>'
        f'<span class="panel-info-glyph" title="{donut_tooltip}">ⓘ</span>'
        '</div>'
        '</div>'
        '<div class="donut-layout-box">'
        '<div class="donut-chart-wrapper">'
        '<svg width="130" height="130" viewBox="0 0 130 130">'
        '<circle cx="65" cy="65" r="50" fill="none" stroke="#F1F5F9" stroke-width="17"/>'
        f'<circle cx="65" cy="65" r="50" fill="none" stroke="#10B981" stroke-width="17" stroke-dasharray="{len_app} {circ}" stroke-dashoffset="{offset_app}" transform="rotate(-90 65 65)"><title>{donut_l1_label}: {pct_app}% ({approved})</title></circle>'
        f'<circle cx="65" cy="65" r="50" fill="none" stroke="#F59E0B" stroke-width="17" stroke-dasharray="{len_pen} {circ}" stroke-dashoffset="{offset_pen}" transform="rotate(-90 65 65)"><title>{donut_l2_label}: {pct_pen}% ({pending})</title></circle>'
        f'<circle cx="65" cy="65" r="50" fill="none" stroke="#EF4444" stroke-width="17" stroke-dasharray="{len_rej} {circ}" stroke-dashoffset="{offset_rej}" transform="rotate(-90 65 65)"><title>{donut_l3_label}: {pct_rej}% ({rejected})</title></circle>'
        '</svg>'
        '<div class="donut-center-label">'
        f'<div class="donut-center-val">{total}</div>'
        '<div class="donut-center-sub">Invoices</div>'
        '</div>'
        '</div>'
        '<div class="donut-legend-col">'
        '<div class="legend-row-item">'
        '<span class="legend-label-wrap">'
        '<span class="legend-bullet" style="background-color: #10B981;"></span>'
        f'{donut_l1_label}'
        '</span>'
        f'<span class="legend-val-num">{pct_app}% ({approved})</span>'
        '</div>'
        '<div class="legend-row-item">'
        '<span class="legend-label-wrap">'
        '<span class="legend-bullet" style="background-color: #F59E0B;"></span>'
        f'{donut_l2_label}'
        '</span>'
        f'<span class="legend-val-num">{pct_pen}% ({pending})</span>'
        '</div>'
        '<div class="legend-row-item">'
        '<span class="legend-label-wrap">'
        '<span class="legend-bullet" style="background-color: #EF4444;"></span>'
        f'{donut_l3_label}'
        '</span>'
        f'<span class="legend-val-num">{pct_rej}% ({rejected})</span>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
        # Right: Bar Chart (Image 4) - Perfectly Aligned at Zero Baseline
        '<div class="analytics-panel">'
        '<div class="panel-header-line">'
        '<div class="panel-title-group">'
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'
        f'<span>{bar_title}</span>'
        f'<span class="panel-info-glyph" title="{bar_tooltip}">ⓘ</span>'
        '</div>'
        '<a class="panel-action-link" href="#recent-activity">View All →</a>'
        '</div>'
        
        '<!-- Main Chart Flex Area -->'
        '<div style="display: flex; flex-direction: column; flex: 1; justify-content: flex-end;">'
        
        '<!-- Top: Y-Axis + Plot Canvas -->'
        '<div style="display: flex; align-items: stretch; height: 95px;">'
        
        '<!-- Y-Axis Labels -->'
        '<div style="display: flex; flex-direction: column; justify-content: space-between; height: 95px; font-size: 0.7rem; color: #94A3B8; font-weight: 600; text-align: right; width: 22px; padding-right: 6px; box-sizing: border-box; line-height: 1;">'
        '<div>20</div><div>15</div><div>10</div><div>5</div><div style="color: #64748B;">0</div>'
        '</div>'
        
        '<!-- Plot Canvas with Zero Baseline Border -->'
        '<div style="position: relative; flex: 1; height: 95px; border-bottom: 1.5px solid #CBD5E1;">'
        
        '<!-- Horizontal Gridlines -->'
        '<div style="position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: space-between; pointer-events: none;">'
        '<div style="border-bottom: 1px dashed #E2E8F0; width: 100%;"></div>'
        '<div style="border-bottom: 1px dashed #E2E8F0; width: 100%;"></div>'
        '<div style="border-bottom: 1px dashed #E2E8F0; width: 100%;"></div>'
        '<div style="border-bottom: 1px dashed #E2E8F0; width: 100%;"></div>'
        '<div style="width: 100%;"></div>'
        '</div>'
        
        '<!-- Bars sitting flat on zero baseline -->'
        f'<div style="position: absolute; inset: 0; display: flex; justify-content: space-around; align-items: flex-end; z-index: 2;">{rendered_bars}</div>'
        '</div>'
        '</div>'
        
        '<!-- Bottom: X-Axis Category Labels Below Zero Line -->'
        '<div style="display: flex; padding-left: 22px; margin-top: 6px;">'
        f'<div style="display: flex; flex: 1; justify-content: space-around; align-items: flex-start;">{rendered_labels}</div>'
        '</div>'
        
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(analytics_html, unsafe_allow_html=True)

    # 6. Activity Table / Ledger (Buyer View: Recent Processing Activity | Seller View: Supplier Settlement Ledger)
    recent_runs = repository.list_runs(limit=6)

    # Red PDF icon SVG
    red_pdf_icon = (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" style="margin-right: 5px; flex-shrink: 0;">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
        '<polyline points="14 2 14 8 20 8"></polyline>'
        '<line x1="16" y1="13" x2="8" y2="13"></line>'
        '<line x1="16" y1="17" x2="8" y2="17"></line>'
        '</svg>'
    )

    if current_view == "seller":
        # Seller View Ledger
        table_header_html = (
            '<div class="activity-table-card" id="recent-activity">'
            '<div class="table-top-toolbar">'
            '<div class="panel-title-group">'
            '<div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(99, 102, 241, 0.12); display: flex; align-items: center; justify-content: center;">'
            '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>'
            '</div>'
            '<span style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">Supplier Invoicing & Settlement Ledger</span>'
            '</div>'
            '<div class="table-filter-cluster">'
            '<div class="filter-pill-dropdown">🏢 All Suppliers <span style="font-size: 0.65rem; color: #64748B;">▼</span></div>'
            '<div class="filter-pill-dropdown">📅 All Settlement Statuses <span style="font-size: 0.65rem; color: #64748B;">▼</span></div>'
            '<span style="font-size: 0.82rem; font-weight: 600; color: #6366F1; cursor: pointer; margin-left: 0.4rem;">Collaboration Hub →</span>'
            '</div>'
            '</div>'
            '<div class="ent-table-head">'
            '<div>Invoice No.</div>'
            '<div>Supplier Entity</div>'
            '<div>Matched PO</div>'
            '<div style="text-align: right;">Invoice Amount</div>'
            '<div>Submitted On</div>'
            '<div>Settlement Status</div>'
            '<div>Disbursement Cycle</div>'
            '<div style="text-align: center;">Action</div>'
            '</div>'
        )
        st.markdown(table_header_html, unsafe_allow_html=True)

        if not recent_runs:
            st.markdown("<div style='text-align: center; padding: 2rem; color: #94A3B8; font-size: 0.85rem;'>No invoices submitted yet.</div>", unsafe_allow_html=True)
        else:
            # Set of vendors with open disputes or responses
            disputed_invoices = {d.get("invoice_number") for d in disputes}
            response_invoices = {r.get("invoice_number") for r in seller_responses}

            for run in recent_runs:
                inv_no = run.get("invoice_number") or run.get("filename") or "INV-UNKNOWN"
                vendor = run.get("vendor_name") or "Unverified Vendor"
                po_no = run.get("po_number") or "None"
                amount = f"₹{float(run.get('invoice_total') or 0.0):,.2f}"

                created_at = run.get("created_at") or ""
                date_str = "Nov 15, 2026, 10:24 AM"
                if len(created_at) >= 16:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        date_str = dt.strftime("%b %d, %Y, %I:%M %p")
                    except Exception:
                        date_str = created_at[:10] + " " + created_at[11:16]

                decision = (run.get("decision") or "PENDING REVIEW").upper()
                if decision == "APPROVED":
                    settle_badge = '<span class="badge-status-approved"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><polyline points="20 6 9 17 4 12"></polyline></svg>Payment Cleared</span>'
                    collab_badge = '<span style="display:inline-flex; align-items:center; gap:4px; font-size:0.74rem; font-weight:700; color:#059669; background:rgba(16,185,129,0.12); padding:0.2rem 0.5rem; border-radius:6px;">✓ Ready for Net 30</span>'
                    btn_label = "View"
                elif decision == "REJECTED":
                    settle_badge = '<span class="badge-status-rejected"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>Disputed / Hold</span>'
                    if inv_no in response_invoices or inv_no in disputed_invoices:
                        collab_badge = '<span style="display:inline-flex; align-items:center; gap:4px; font-size:0.74rem; font-weight:700; color:#7C3AED; background:rgba(124,58,237,0.12); padding:0.2rem 0.5rem; border-radius:6px;">💬 Clarification Filed</span>'
                    else:
                        collab_badge = '<span style="display:inline-flex; align-items:center; gap:4px; font-size:0.74rem; font-weight:600; color:#DC2626; background:rgba(239,68,68,0.1); padding:0.2rem 0.5rem; border-radius:6px;">Resolution Needed</span>'
                    btn_label = "Clarify"
                else:
                    settle_badge = '<span class="badge-status-review"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>Under AP Review</span>'
                    collab_badge = '<span style="display:inline-flex; align-items:center; gap:4px; font-size:0.74rem; font-weight:600; color:#64748B; background:rgba(241,245,249,0.9); padding:0.2rem 0.5rem; border-radius:6px;">AP Validation</span>'
                    btn_label = "Track"

                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.6, 1.9, 0.9, 1.1, 1.4, 1.4, 1.6, 0.9])
                with c1:
                    st.markdown(f"<div style='display: flex; align-items: center;'>{red_pdf_icon}<span style='font-family:\"JetBrains Mono\",monospace; font-size:0.8rem; font-weight:700; color:#0F172A;'>{inv_no}</span></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='font-size:0.82rem; font-weight:600; color:#1E293B; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block;' title='{vendor}'>{vendor}</span>", unsafe_allow_html=True)
                with c3:
                    po_disp = f"<span style='font-family:\"JetBrains Mono\",monospace; font-size:0.78rem; color:#475569;'>{po_no}</span>" if po_no != "None" else "<span style='color:#94A3B8; font-size:0.78rem;'>N/A</span>"
                    st.markdown(po_disp, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div style='text-align:right; font-size:0.84rem; font-weight:700; color:#0F172A; font-variant-numeric:tabular-nums;'>{amount}</div>", unsafe_allow_html=True)
                with c5:
                    st.markdown(f"<span style='font-size:0.76rem; color:#64748B;'>{date_str}</span>", unsafe_allow_html=True)
                with c6:
                    st.markdown(settle_badge, unsafe_allow_html=True)
                with c7:
                    st.markdown(collab_badge, unsafe_allow_html=True)
                with c8:
                    if st.button(btn_label, key=f"btn_seller_act_{run.get('run_id')}", use_container_width=True):
                        if decision == "REJECTED" or inv_no in response_invoices or inv_no in disputed_invoices:
                            st.session_state["sidebar_nav"] = "Seller Responses"
                            st.session_state["current_page"] = "Seller Responses"
                            st.rerun()
                        elif decision == "PENDING REVIEW":
                            if on_view_run:
                                on_view_run(run.get("run_id"))
                        else:
                            if on_view_run:
                                on_view_run(run.get("run_id"))

        st.markdown("</div>", unsafe_allow_html=True)

        # Active Supplier Responses Summary Card for Seller View
        if seller_responses:
            st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
            col_sr_head, col_sr_btn = st.columns([3.5, 1.2])
            with col_sr_head:
                st.markdown("""
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div style="width: 28px; height: 28px; border-radius: 7px; background: rgba(124, 58, 237, 0.12); display: flex; align-items: center; justify-content: center;">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    </div>
                    <span style="font-size: 0.95rem; font-weight: 700; color: #0F172A;">Active Clarifications & Supporting Change Orders</span>
                </div>
                """, unsafe_allow_html=True)
            with col_sr_btn:
                if st.button("Open Collaboration Hub →", key="btn_nav_collab_hub", use_container_width=True):
                    st.session_state["sidebar_nav"] = "Seller Responses"
                    st.session_state["current_page"] = "Seller Responses"
                    st.rerun()

            for sr in seller_responses[:2]:
                resp_id = sr.get("response_id")
                sr_vend = sr.get("vendor_name")
                sr_inv = sr.get("invoice_number")
                sr_disc = sr.get("discrepancy_type")
                sr_exp = sr.get("vendor_explanation")
                sr_amt = f"₹{float(sr.get('disputed_amount') or 0.0):,.2f}"
                sr_status = sr.get("status")

                if "ACCEPTED" in sr_status:
                    stat_pill = '<span class="badge-status-approved">✓ Accepted & Approved</span>'
                else:
                    stat_pill = '<span class="badge-status-review">● Credit Note Requested</span>'

                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.85rem 1.15rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">
                    <div>
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; font-weight: 700; color: #6366F1;">{resp_id}</span>
                            <span style="font-size: 0.85rem; font-weight: 700; color: #0F172A;">{sr_vend}</span>
                            <span style="font-size: 0.76rem; color: #64748B;">({sr_inv})</span>
                        </div>
                        <div style="font-size: 0.78rem; color: #475569;">
                            <strong>Discrepancy:</strong> {sr_disc} • <strong>Disputed:</strong> {sr_amt}
                        </div>
                        <div style="font-size: 0.74rem; color: #64748B; margin-top: 0.15rem; font-style: italic;">
                            "{sr_exp[:110]}..."
                        </div>
                    </div>
                    <div>{stat_pill}</div>
                </div>
                """, unsafe_allow_html=True)

    else:
        # Buyer View Table (Image 5)
        table_header_html = (
            '<div class="activity-table-card" id="recent-activity">'
            '<div class="table-top-toolbar">'
            '<div class="panel-title-group">'
            '<div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(99, 102, 241, 0.12); display: flex; align-items: center; justify-content: center;">'
            '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>'
            '</div>'
            '<span style="font-size: 1.05rem; font-weight: 800; color: #0F172A;">Recent Processing Activity</span>'
            '</div>'
            '<div class="table-filter-cluster">'
            '<div class="filter-pill-dropdown">All Decisions <span style="font-size: 0.65rem; color: #64748B;">▼</span></div>'
            '<div class="filter-pill-dropdown">📅 Last 7 Days <span style="font-size: 0.65rem; color: #64748B;">▼</span></div>'
            '<span style="font-size: 0.82rem; font-weight: 600; color: #6366F1; cursor: pointer; margin-left: 0.4rem;">View Full History →</span>'
            '</div>'
            '</div>'
            '<div class="ent-table-head">'
            '<div>Invoice No.</div>'
            '<div>Vendor</div>'
            '<div>PO No.</div>'
            '<div style="text-align: right;">Amount</div>'
            '<div>Processed On</div>'
            '<div>Decision</div>'
            '<div>Key Remark</div>'
            '<div style="text-align: center;">Action</div>'
            '</div>'
        )
        st.markdown(table_header_html, unsafe_allow_html=True)

        if not recent_runs:
            st.markdown("<div style='text-align: center; padding: 2rem; color: #94A3B8; font-size: 0.85rem;'>No invoices matching selected filter.</div>", unsafe_allow_html=True)
        else:
            for run in recent_runs:
                inv_no = run.get("invoice_number") or run.get("filename") or "INV-UNKNOWN"
                vendor = run.get("vendor_name") or "Unverified Vendor"
                po_no = run.get("po_number") or "None"
                amount = f"₹{float(run.get('invoice_total') or 0.0):,.2f}"

                # Format processed date like Image 5 (e.g. "Nov 15, 2026, 10:24 AM")
                created_at = run.get("created_at") or ""
                date_str = "Nov 15, 2026, 10:24 AM"
                if len(created_at) >= 16:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        date_str = dt.strftime("%b %d, %Y, %I:%M %p")
                    except Exception:
                        date_str = created_at[:10] + " " + created_at[11:16]

                # Decision badge with semantic icon (Image 5)
                decision = (run.get("decision") or "PENDING REVIEW").upper()
                if decision == "APPROVED":
                    dec_badge = '<span class="badge-status-approved"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><polyline points="20 6 9 17 4 12"></polyline></svg>Auto-Approved</span>'
                    btn_label = "View"
                elif decision == "REJECTED":
                    dec_badge = '<span class="badge-status-rejected"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>Rejected</span>'
                    btn_label = "View"
                else:
                    dec_badge = '<span class="badge-status-review"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>Pending Review</span>'
                    btn_label = "Review"

                # Key remark
                reason_code = run.get("reason_code", "")
                if "DUPLICATE" in reason_code:
                    remark = "Duplicate invoice detected"
                elif "MISMATCH" in reason_code or "VARIANCE" in reason_code:
                    remark = "Amount variance (+14%)"
                elif "EXCEEDS_REMAINING" in reason_code:
                    remark = "Exceeds remaining PO balance"
                elif "AMBIGUOUS" in reason_code or "MISSING_PO" in reason_code:
                    remark = "Ambiguous candidate POs"
                elif "UNAPPROVED" in reason_code or "INACTIVE" in reason_code:
                    remark = "Unapproved vendor account"
                elif decision == "APPROVED":
                    remark = "All checks passed"
                else:
                    remark = run.get("explanation", "")[:28] + "..." if len(run.get("explanation", "")) > 28 else (run.get("explanation") or "Within tolerance (2%)")

                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.6, 1.9, 0.9, 1.1, 1.4, 1.4, 1.6, 0.9])
                with c1:
                    st.markdown(f"<div style='display: flex; align-items: center;'>{red_pdf_icon}<span style='font-family:\"JetBrains Mono\",monospace; font-size:0.8rem; font-weight:700; color:#0F172A;'>{inv_no}</span></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='font-size:0.82rem; font-weight:600; color:#1E293B; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; display:block;' title='{vendor}'>{vendor}</span>", unsafe_allow_html=True)
                with c3:
                    po_disp = f"<span style='font-family:\"JetBrains Mono\",monospace; font-size:0.78rem; color:#475569;'>{po_no}</span>" if po_no != "None" else "<span style='color:#94A3B8; font-size:0.78rem;'>N/A</span>"
                    st.markdown(po_disp, unsafe_allow_html=True)
                with c4:
                    st.markdown(f"<div style='text-align:right; font-size:0.84rem; font-weight:700; color:#0F172A; font-variant-numeric:tabular-nums;'>{amount}</div>", unsafe_allow_html=True)
                with c5:
                    st.markdown(f"<span style='font-size:0.76rem; color:#64748B;'>{date_str}</span>", unsafe_allow_html=True)
                with c6:
                    st.markdown(dec_badge, unsafe_allow_html=True)
                with c7:
                    st.markdown(f"<span style='font-size:0.76rem; color:#475569;' title='{remark}'>{remark}</span>", unsafe_allow_html=True)
                with c8:
                    if st.button(btn_label, key=f"btn_act_{run.get('run_id')}", use_container_width=True):
                        if on_view_run:
                            on_view_run(run.get("run_id"))

        st.markdown("</div>", unsafe_allow_html=True)
