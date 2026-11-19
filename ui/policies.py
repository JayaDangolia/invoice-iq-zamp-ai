"""Policies & Master Data Page Module for InvoiceIQ.
Provides financial tolerance configuration, decision precedence hierarchy,
and rule engine schemas.
"""

import json
from typing import Any, Dict
import pandas as pd
import streamlit as st
import yaml
from config.settings import RULES
from ui.components import (
    render_app_header,
    render_page_heading,
    render_summary_kpi_card,
    render_metric_card
)


def render_policies_page() -> None:
    """Render the Policies & Master Data configuration page."""
    render_app_header("Policies & Master Data")

    # 1. Page Heading
    render_page_heading(
        title="Policies & Master Data",
        subtitle="Automated matching tolerances, decision precedence hierarchy, and compliance thresholds.",
        badge="Engine v2.4 Active"
    )

    tols = RULES.get("tolerances", {})
    dup_policy = RULES.get("duplicate_policy", {})

    tab1, tab2, tab3 = st.tabs([
        "Financial Tolerances & Thresholds",
        "Decision Precedence Hierarchy",
        "Mandatory Schema & YAML Rules"
    ])

    with tab1:
        st.markdown("<div style='font-weight: 700; font-size: 1.05rem; color: #0F172A; margin: 0.5rem 0 0.85rem 0;'>Configured AP Matching Tolerances</div>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(render_summary_kpi_card(
                label="Amount Variance",
                value=f"±{tols.get('amount_percentage_tolerance', 0.5)}%",
                subtext=f"Max ₹{tols.get('amount_absolute_tolerance', 5.0):,.2f} buffer",
                theme="blue",
                trend_badge="BOUNDED",
                icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>'
            ), unsafe_allow_html=True)
        with c2:
            st.markdown(render_summary_kpi_card(
                label="Tax Discrepancy",
                value=f"₹{tols.get('tax_variance_tolerance', 2.0):,.2f}",
                subtext="Rounding tolerance",
                theme="green",
                trend_badge="ROUNDING",
                icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
            ), unsafe_allow_html=True)
        with c3:
            st.markdown(render_summary_kpi_card(
                label="Duplicate Window",
                value=f"{dup_policy.get('window_days', 90)} Days",
                subtext="SHA-256 & identity match",
                theme="purple",
                trend_badge="90 DAYS",
                icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>'
            ), unsafe_allow_html=True)
        with c4:
            st.markdown(render_summary_kpi_card(
                label="Aging Threshold",
                value="180 Days",
                subtext="Invoice date validation",
                theme="coral",
                trend_badge="STALE LIMIT",
                icon_svg='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#DC2626" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>'
            ), unsafe_allow_html=True)

        st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="table-container-card" style="padding: 1.25rem 1.5rem;">
            <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A; margin-bottom: 0.5rem;">Tolerance Logic & Mathematical Bounds</div>
            <div style="font-size: 0.85rem; color: #475569; line-height: 1.6;">
                InvoiceIQ evaluates invoices against procurement commitments using a dual-boundary tolerance model:
                <ul>
                    <li><b>Percentage Threshold (0.5%):</b> An invoice total variance within 0.5% of the matched PO total is accepted for auto-approval without human escalation.</li>
                    <li><b>Absolute Floor (₹5.00):</b> Small currency rounding differences up to ₹5.00 are treated as non-material rounding noise.</li>
                    <li><b>Tax Discrepancy Bound (₹2.00):</b> Calculated GST (line-by-line sum) vs extracted GST allows up to ₹2.00 variance to accommodate statutory rounding across state jurisdictions.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<div style='font-weight: 700; font-size: 1.05rem; color: #0F172A; margin: 0.5rem 0 0.85rem 0;'>Decision Precedence Architecture</div>", unsafe_allow_html=True)
        
        precedence_matrix = [
            {
                "Level": "1. Critical Integrity",
                "Rule Trigger": "Exact duplicate SHA-256 hash or invoice number collision within 90 days",
                "Decision": "REJECTED",
                "Policy Code": "DUPLICATE_INVOICE",
                "Action": "Reject immediately; prevent double payout"
            },
            {
                "Level": "2. Vendor Authorization",
                "Rule Trigger": "Vendor name, GSTIN, or domain not found in Authorized Vendor Master",
                "Decision": "PENDING REVIEW",
                "Policy Code": "UNAPPROVED_VENDOR",
                "Action": "Escalate to Procurement lead for vendor vetting"
            },
            {
                "Level": "3. Mandatory Fields",
                "Rule Trigger": "Missing invoice number, date, vendor entity, or total amount",
                "Decision": "REJECTED",
                "Policy Code": "MISSING_MANDATORY_FIELDS",
                "Action": "Reject to vendor with request for re-issue"
            },
            {
                "Level": "4. PO Reconciliation",
                "Rule Trigger": "Missing PO reference, price variance > 0.5%, or PO remaining balance exceeded",
                "Decision": "PENDING REVIEW",
                "Policy Code": "PO_AMOUNT_MISMATCH / PO_NOT_FOUND",
                "Action": "Route to AP Review Queue for 1-click PO linking or credit note"
            },
            {
                "Level": "5. Standard Approval",
                "Rule Trigger": "All 11 pipeline validation stages complete within tolerance bounds",
                "Decision": "APPROVED",
                "Policy Code": "ALL_CHECKS_PASSED",
                "Action": "Commit automated payout schedule (STP)"
            },
        ]
        
        st.markdown('<div class="table-container-card" style="padding: 1.25rem 1.5rem;">', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(precedence_matrix), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("<div style='font-weight: 700; font-size: 1.05rem; color: #0F172A; margin: 0.5rem 0 0.85rem 0;'>Mandatory Schema & System Rules Inspector</div>", unsafe_allow_html=True)
        
        col_mand, col_yaml = st.columns([1, 1.2])
        
        with col_mand:
            st.markdown("<div style='font-weight: 600; font-size: 0.9rem; color: #0F172A; margin-bottom: 0.5rem;'>Mandatory Metadata Schema</div>", unsafe_allow_html=True)
            mandatory = RULES.get("mandatory_fields", [])
            mand_rows = []
            for f in mandatory:
                mand_rows.append({
                    "Required Field": f,
                    "Validation Type": "Non-empty string",
                    "Severity": "Critical Reject"
                })
            st.dataframe(pd.DataFrame(mand_rows), use_container_width=True, hide_index=True)
            
        with col_yaml:
            st.markdown("<div style='font-weight: 600; font-size: 0.9rem; color: #0F172A; margin-bottom: 0.5rem;'>Runtime YAML Configuration</div>", unsafe_allow_html=True)
            yaml_str = yaml.dump(RULES, sort_keys=False)
            st.code(yaml_str, language="yaml")
