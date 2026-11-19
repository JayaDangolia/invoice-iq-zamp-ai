"""Reusable Enterprise Fintech UI Components for InvoiceIQ.
Shared across all workspace pages to ensure a consistent, premium design system.
"""

from typing import Any, Dict, List, Optional
import streamlit as st


def render_app_header(page_title: str, subtext: Optional[str] = None, show_back: bool = False) -> None:
    """Render top enterprise breadcrumb bar with live system status badge and 1-click back navigation."""
    sub_crumb = f' <span style="color: #CBD5E1; margin: 0 4px;">/</span> <span class="crumb-active">{subtext}</span>' if subtext else ""
    active_cls = "crumb-active" if not subtext else ""
    
    col_left, col_right = st.columns([3.8, 1.2])
    with col_left:
        html = (
            '<div class="app-header-bar" style="border-bottom: none; padding-bottom: 0; margin-bottom: 0.25rem;">'
            '<div class="header-breadcrumb">'
            '<span style="font-weight: 700; color: #4338CA; cursor: pointer;">InvoiceIQ</span>'
            '<span style="color: #CBD5E1; margin: 0 6px;">/</span>'
            f'<span class="{active_cls}" style="color: #0F172A; font-weight: 600;">{page_title}</span>'
            f'{sub_crumb}'
            '</div>'
            '</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    with col_right:
        status_html = (
            '<div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">'
            '<div class="header-status-badge">'
            '<span class="status-dot-pulse"></span>'
            '<span style="font-weight: 600; font-size: 0.74rem; color: #047857;">System Operational · Live</span>'
            '</div>'
            '</div>'
        )
        st.markdown(status_html, unsafe_allow_html=True)

    # 1-Click Navigation Back to Overview if navigated from Overview or explicitly requested
    if st.session_state.get("nav_source") == "Overview" or show_back:
        b_key = f"btn_back_to_ov_{page_title.replace(' ', '_').replace('&', 'and')}"
        col_b, _ = st.columns([1.8, 4.2])
        with col_b:
            if st.button("← Back to Overview", key=b_key):
                st.session_state["nav_source"] = None
                st.session_state["nav_target"] = "Overview"
                st.session_state["active_run_id"] = None
                st.session_state["selected_vendor_id"] = None
                st.session_state["selected_po_num"] = None
                st.session_state["reviewing_run_id"] = None
                st.rerun()


def render_page_heading(
    title: str,
    subtitle: str,
    badge: Optional[str] = None,
    action_html: Optional[str] = None
) -> None:
    """Render unified page title banner with gradient typography and metadata badge."""
    badge_markup = f'<span class="page-title-badge">{badge}</span>' if badge else ""
    action_markup = f'<div>{action_html}</div>' if action_html else ""
    
    html = (
        '<div class="page-title-container">'
        '<div>'
        f'<div class="page-headline-wrap"><h1 class="page-headline">{title}</h1>{badge_markup}</div>'
        f'<div class="page-subtext">{subtitle}</div>'
        '</div>'
        f'{action_markup}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_summary_kpi_card(
    label: str,
    value: str,
    subtext: str,
    theme: str = "blue",
    trend_badge: Optional[str] = None,
    icon_svg: Optional[str] = None
) -> str:
    """Return HTML string for a unified pastel KPI summary card."""
    theme_cls = f"card-{theme}"
    icon_cls = f"icon-{theme}"
    
    trend_html = ""
    if trend_badge:
        tb_up = trend_badge.upper()
        if any(k in tb_up for k in ["+", "OK", "STP", "ACTIVE", "CLOSED", "SETTLED"]):
            trend_cls = "trend-green"
        elif any(k in tb_up for k in ["FLAG", "ATTENTION", "ACTION", "REQ", "FAIL", "EXHAUST"]):
            trend_cls = "trend-coral"
        elif any(k in tb_up for k in ["WARN", "PENDING", "HOLD"]):
            trend_cls = "trend-amber"
        elif any(k in tb_up for k in ["VERIF", "SYNC", "FAST", "90", "SCHEMA", "RULE"]):
            trend_cls = "trend-purple"
        elif theme in ("green", "coral", "amber", "purple", "blue"):
            trend_cls = f"trend-{theme}"
        else:
            trend_cls = "trend-blue"
        trend_html = f'<span class="kpi-trend-pill {trend_cls}">{trend_badge}</span>'

    default_icon = (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
        '<polyline points="14 2 14 8 20 8"></polyline>'
        '</svg>'
    )
    icon_content = icon_svg if icon_svg else default_icon

    return (
        f'<div class="kpi-card-pastel {theme_cls}">'
        '<div class="kpi-top-row">'
        f'<div class="kpi-icon-circle {icon_cls}">{icon_content}</div>'
        '<div>'
        f'<div class="kpi-title-label">{label}</div>'
        '<div class="kpi-metric-wrap">'
        f'<span class="kpi-metric-big">{value}</span>'
        f'{trend_html}'
        '</div>'
        '</div>'
        '</div>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.45rem;">'
        f'<div class="kpi-subtitle-text" style="margin-top: 0;">{subtext}</div>'
        '<span style="font-size: 0.72rem; font-weight: 700; color: #4F46E5; display: inline-flex; align-items: center; gap: 3px; background: rgba(255,255,255,0.75); padding: 0.15rem 0.45rem; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">Details →</span>'
        '</div>'
        '</div>'
    )


def render_status_pill(status: str) -> str:
    """Render a clean, semantic fintech status badge with vector icon."""
    s = (status or "PENDING REVIEW").upper().strip()
    if s in ("APPROVED", "ACTIVE", "RESOLVED", "VALIDATION_PASSED", "MANUALLY_APPROVED"):
        return (
            '<span class="badge-status-approved">'
            '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><polyline points="20 6 9 17 4 12"></polyline></svg>'
            f'{status}'
            '</span>'
        )
    elif s in ("REJECTED", "INACTIVE", "FAILED", "MANUALLY_REJECTED", "FLAGGED"):
        return (
            '<span class="badge-status-rejected">'
            '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
            f'{status}'
            '</span>'
        )
    elif s in ("PENDING REVIEW", "PENDING_REVIEW", "OPEN", "UNDER_REVIEW", "AWAITING_REVIEW"):
        return (
            '<span class="badge-status-review">'
            '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
            f'{status}'
            '</span>'
        )
    return f'<span class="badge-status-neutral">{status}</span>'


def render_decision_badge(decision: str) -> str:
    """Compatibility alias for render_status_pill."""
    return render_status_pill(decision)


def render_empty_state(title: str, description: str, action_text: Optional[str] = None) -> None:
    """Render a subtle, professional empty state container."""
    html = (
        '<div class="empty-state-card">'
        '<div class="empty-state-icon">'
        '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="1.8">'
        '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>'
        '<line x1="9" y1="9" x2="15" y2="9"></line>'
        '<line x1="9" y1="13" x2="15" y2="13"></line>'
        '<line x1="9" y1="17" x2="12" y2="17"></line>'
        '</svg>'
        '</div>'
        f'<div class="empty-state-title">{title}</div>'
        f'<div class="empty-state-desc">{description}</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, subtext: Optional[str] = None) -> None:
    """Render a standalone minimal metric card."""
    sub_html = f'<div class="kpi-subtitle-text">{subtext}</div>' if subtext else ""
    html = (
        '<div class="kpi-card-pastel card-blue" style="min-height: 90px; padding: 0.85rem 1rem;">'
        f'<div class="kpi-title-label">{label}</div>'
        f'<div class="kpi-metric-big" style="font-size: 1.5rem; margin-top: 0.2rem;">{value}</div>'
        f'{sub_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_top_navbar(current_page: str) -> None:
    """Top navigation bar rendering using render_app_header."""
    render_app_header(current_page)


def render_four_phase_stepper(
    phase1_status: str = "pending",
    phase2_status: str = "pending",
    phase3_status: str = "pending",
    phase4_status: str = "pending",
    phase1_meta: str = "Text & Metadata",
    phase2_meta: str = "Vendor & Duplicates",
    phase3_meta: str = "PO & Variance",
    phase4_meta: str = "Policy Decision"
) -> None:
    """Render the four business funnel phases: READ -> VERIFY -> RECONCILE -> DECIDE."""
    phases = [
        ("Phase 1 — Read", "READ", "Extract Text & OCR", phase1_meta, phase1_status, "#3B82F6"),
        ("Phase 2 — Verify", "VERIFY", "Vendor & Duplicates", phase2_meta, phase2_status, "#8B5CF6"),
        ("Phase 3 — Reconcile", "RECONCILE", "PO Match & Amounts", phase3_meta, phase3_status, "#10B981"),
        ("Phase 4 — Decide", "DECIDE", "Policy Determination", phase4_meta, phase4_status, "#F59E0B"),
    ]

    cols_html = []
    for idx, (phase_label, phase_action, title, meta, status, color) in enumerate(phases, 1):
        badge_text = "Pending"
        badge_cls = "badge-status-neutral"

        if status == "active":
            badge_text = "Processing..."
            badge_cls = "badge-status-review"
        elif status == "success":
            badge_text = "Passed"
            badge_cls = "badge-status-approved"
        elif status == "warning":
            badge_text = "Flagged"
            badge_cls = "badge-status-review"
        elif status == "danger":
            badge_text = "Failed"
            badge_cls = "badge-status-rejected"

        card = (
            f'<div class="stepper-phase-card phase-{idx} status-{status}">'
            '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">'
            f'<span style="font-size: 0.72rem; font-weight: 700; color: {color}; letter-spacing: 0.5px; text-transform: uppercase;">{phase_label}</span>'
            f'<span class="{badge_cls}">{badge_text}</span>'
            '</div>'
            f'<div style="font-size: 0.88rem; font-weight: 700; color: #0F172A; margin-bottom: 0.15rem;">{title}</div>'
            f'<div style="font-size: 0.74rem; color: #64748B;">{meta}</div>'
            '</div>'
        )
        cols_html.append(card)

    inner = "".join(cols_html)
    st.markdown(f'<div class="stepper-phase-container">{inner}</div>', unsafe_allow_html=True)


def render_decision_banner(
    decision: str,
    reason_code: str,
    explanation: str,
    action: str
) -> None:
    """Render authoritative outcome banner with fintech gradient border and action callout."""
    dec = (decision or "PENDING REVIEW").upper().strip()
    
    if "APPROV" in dec:
        bg = "#F0FDF4"
        border = "#86EFAC"
        accent = "#15803D"
        badge_bg = "#DCFCE7"
        badge_color = "#166534"
        title = "Automated Approval Granted"
        icon_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#15803D" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="16 10 11 15 8 12"></polyline></svg>'
    elif "REJECT" in dec:
        bg = "#FEF2F2"
        border = "#FCA5A5"
        accent = "#B91C1C"
        badge_bg = "#FEE2E2"
        badge_color = "#991B1B"
        title = "Automated Rejection Triggered"
        icon_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#B91C1C" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
    else:
        bg = "#FFFBEB"
        border = "#FDE68A"
        accent = "#B45309"
        badge_bg = "#FEF3C7"
        badge_color = "#92400E"
        title = "Routing to Review Queue"
        icon_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#B45309" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'

    html = (
        f'<div style="background: {bg}; border: 1.5px solid {border}; border-radius: 12px; padding: 1.15rem 1.35rem; margin-bottom: 1.5rem; box-shadow: 0 4px 12px -2px rgba(0,0,0,0.04);">'
        '<div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; margin-bottom: 0.75rem;">'
        '<div style="display: flex; align-items: center; gap: 0.75rem;">'
        f'{icon_svg}'
        '<div>'
        f'<div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">{title}</div>'
        f'<div style="font-size: 0.78rem; color: #64748B; font-family: monospace; margin-top: 0.15rem;">RULE TRIGGER: <b style="color: {accent};">{reason_code}</b></div>'
        '</div>'
        '</div>'
        f'<div style="background: {badge_bg}; color: {badge_color}; font-weight: 700; font-size: 0.8rem; padding: 0.35rem 0.85rem; border-radius: 9999px; letter-spacing: 0.4px;">{decision}</div>'
        '</div>'
        f'<div style="color: #334155; font-size: 0.88rem; line-height: 1.5; margin-bottom: 0.65rem; padding-left: 2.25rem;">{explanation}</div>'
        f'<div style="background: rgba(255,255,255,0.7); border-radius: 6px; padding: 0.55rem 0.85rem; font-size: 0.82rem; color: {accent}; font-weight: 600; margin-left: 2.25rem;">'
        f'Recommended Action: <span style="font-weight: 500; color: #1E293B;">{action}</span>'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

