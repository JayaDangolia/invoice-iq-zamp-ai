import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import importlib
import ui.styles
import ui.dashboard
import ui.upload
import ui.review
import ui.history
import ui.vendors
import ui.purchase_orders
import ui.policies
import ui.seller_responses
import ui.disputes
import ui.components
import database.repository
importlib.reload(ui.styles)
importlib.reload(ui.dashboard)
importlib.reload(ui.upload)
importlib.reload(ui.review)
importlib.reload(ui.history)
importlib.reload(ui.vendors)
importlib.reload(ui.purchase_orders)
importlib.reload(ui.policies)
importlib.reload(ui.seller_responses)
importlib.reload(ui.disputes)
importlib.reload(ui.components)
importlib.reload(database.repository)

import streamlit as st
import pandas as pd
from database.db import init_db
from database.repository import InvoiceRepository
from core.workflow import WorkflowOrchestrator
from config.settings import RULES, VENDORS_CSV, PURCHASE_ORDERS_CSV, PO_LINE_ITEMS_CSV, SAMPLE_INVOICES_DIR
from ui.styles import get_custom_css
from ui.components import render_top_navbar, render_metric_card
from ui.dashboard import render_dashboard_page
from ui.upload import render_upload_page
from ui.live_run import execute_and_render_live_pipeline, render_decision_report
from ui.review import render_review_queue_page
from ui.history import render_history_page
from ui.vendors import render_vendors_page
from ui.purchase_orders import render_po_page
from ui.policies import render_policies_page
from ui.seller_responses import render_seller_responses_page
from ui.disputes import render_disputes_page

# 1. Page Configuration
st.set_page_config(
    page_title="InvoiceIQ — AI-Powered AP & Vendor Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Enterprise Custom Styling
st.markdown(get_custom_css(), unsafe_allow_html=True)

# 2. Initialize Database & Services
init_db()
repository = InvoiceRepository()
orchestrator = WorkflowOrchestrator(repository=repository)

# 3. Session State Initialization
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Dashboard"
if "active_run_id" not in st.session_state:
    st.session_state["active_run_id"] = None
if "pending_upload_bytes" not in st.session_state:
    st.session_state["pending_upload_bytes"] = None
if "pending_upload_filename" not in st.session_state:
    st.session_state["pending_upload_filename"] = None

# 4. Sidebar Navigation (RECREATING IMAGE 6 DESIGN)
with st.sidebar:
    # Logo & Brand Header (Interactive 1-Click to Overview)
    logo_wrap = st.container()
    with logo_wrap:
        st.markdown("""
        <div class="sidebar-brand-block" title="InvoiceIQ - Click to return to Overview" style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; padding-bottom: 0.95rem; border-bottom: 1px solid rgba(255, 255, 255, 0.08); cursor: pointer;">
            <div style="background: linear-gradient(135deg, #4F46E5 0%, #6366F1 50%, #3B82F6 100%); width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.45);">
                <div style="width: 20px; height: 20px; border: 2.5px solid #FFFFFF; border-radius: 6px; transform: rotate(8deg); background: rgba(255, 255, 255, 0.2);"></div>
            </div>
            <div>
                <div style="font-weight: 800; font-size: 1.3rem; color: #FFFFFF; line-height: 1.15; letter-spacing: -0.4px;">InvoiceIQ</div>
                <div style="font-size: 0.72rem; color: #94A3B8; font-weight: 500;">AI-Powered AP & Vendor Hub</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        def _on_logo_click():
            st.session_state["sidebar_nav"] = "Overview"
            st.session_state["current_page"] = "Dashboard"
            st.session_state["nav_source"] = None
            st.session_state["active_run_id"] = None
            st.session_state["selected_vendor_id"] = None
            st.session_state["selected_po_num"] = None
            st.session_state["reviewing_run_id"] = None

        st.button("InvoiceIQ Home", key="btn_logo_home", on_click=_on_logo_click)

    kpis = repository.get_kpis()
    pending_count = kpis.get("pending_review", 0)

    nav_options = [
        "Overview",
        "Process Invoice",
        "Review Queue",
        "Invoices & History",
        "Vendor Network",
        "PO Management",
        "Policies & Master Data",
        "Seller Responses",
        "Disputes & Resolutions"
    ]

    nav_to_page = {
        "Overview": "Dashboard",
        "Process Invoice": "Process Invoice",
        "Review Queue": "Review Queue",
        "Invoices & History": "History",
        "Vendor Network": "Vendor Network",
        "PO Management": "PO Management",
        "Policies & Master Data": "Policies & Master Data",
        "Seller Responses": "Seller Responses",
        "Disputes & Resolutions": "Disputes & Resolutions"
    }

    # Handle programmatic navigation target before st.radio instantiation
    if st.session_state.get("nav_target"):
        target_nav = st.session_state.pop("nav_target")
        st.session_state["sidebar_nav"] = target_nav
        st.session_state["current_page"] = nav_to_page.get(target_nav, "Dashboard")

    if "sidebar_nav" not in st.session_state:
        st.session_state["sidebar_nav"] = "Overview"

    selected_nav = st.radio(
        "Navigation",
        options=nav_options,
        key="sidebar_nav",
        label_visibility="collapsed"
    )

    st.session_state["current_page"] = nav_to_page.get(selected_nav, "Dashboard")

    # AI Document Engine Card with Floating Documents & Sparkles Illustration (IMAGE 6)
    st.markdown("""
    <div class="ai-engine-box">
        <div style="display: flex; justify-content: center; margin-bottom: 0.45rem;">
            <svg width="86" height="52" viewBox="0 0 86 52" fill="none">
                <!-- Sparkles -->
                <path d="M72 10 L73 7 L76 6 L73 5 L72 2 L71 5 L68 6 L71 7 Z" fill="#FDE047"/>
                <path d="M14 22 L15 19 L18 18 L15 17 L14 14 L13 17 L10 18 L13 19 Z" fill="#FCD34D"/>
                <path d="M78 36 L78.8 33.5 L81 33 L78.8 32.5 L78 30 L77.2 32.5 L75 33 L77.2 33.5 Z" fill="#DDD6FE"/>
                <!-- Sheet 1 (Lavender back) -->
                <g transform="translate(18, 6) rotate(-8)">
                    <rect width="36" height="42" rx="4" fill="#818CF8" fill-opacity="0.85"/>
                    <rect x="5" y="8" width="18" height="3" rx="1.5" fill="#FFFFFF" fill-opacity="0.9"/>
                    <rect x="5" y="15" width="26" height="2.5" rx="1" fill="#FFFFFF" fill-opacity="0.6"/>
                    <rect x="5" y="21" width="22" height="2.5" rx="1" fill="#FFFFFF" fill-opacity="0.6"/>
                    <rect x="5" y="27" width="24" height="2.5" rx="1" fill="#FFFFFF" fill-opacity="0.6"/>
                </g>
                <!-- Sheet 2 (Blue front with drop shadow) -->
                <g transform="translate(30, 8) rotate(7)">
                    <rect width="36" height="42" rx="4" fill="#38BDF8" filter="drop-shadow(0 4px 8px rgba(0,0,0,0.35))"/>
                    <rect x="5" y="8" width="16" height="3" rx="1.5" fill="#FFFFFF" fill-opacity="0.95"/>
                    <rect x="5" y="15" width="26" height="2.5" rx="1" fill="#FFFFFF" fill-opacity="0.75"/>
                    <rect x="5" y="21" width="20" height="2.5" rx="1" fill="#FFFFFF" fill-opacity="0.75"/>
                    <rect x="5" y="27" width="25" height="2.5" rx="1" fill="#FFFFFF" fill-opacity="0.75"/>
                </g>
            </svg>
        </div>
        <div style="font-size: 0.92rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.5rem; text-align: left;">AI Document Engine</div>
        <div class="ai-engine-list">
            <div class="ai-engine-item"><span class="ai-check">✔</span> OCR & Data Extraction</div>
            <div class="ai-engine-item"><span class="ai-check">✔</span> PO Matching <span style="color:#A78BFA; font-size:0.65rem; margin-left:auto;">✓</span></div>
            <div class="ai-engine-item"><span class="ai-check">✔</span> Tax & Discount Validation <span style="color:#A78BFA; font-size:0.65rem; margin-left:auto;">✓</span></div>
            <div class="ai-engine-item"><span class="ai-check">✔</span> Buyer–Seller Reconciliation <span style="color:#A78BFA; font-size:0.65rem; margin-left:auto;">✓</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # System Operational Status (IMAGE 6)
    st.markdown("""
    <div class="sidebar-system-status">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            <span class="status-dot-green"></span>
            <div>
                <div style="font-weight: 600; font-size: 0.78rem; color: #FFFFFF; line-height: 1.2;">System Operational</div>
                <div style="font-size: 0.68rem; color: #64748B;">Last sync: 2 min ago</div>
            </div>
        </div>
        <div class="equalizer-waveform">
            <span class="eq-bar eq-1"></span>
            <span class="eq-bar eq-2"></span>
            <span class="eq-bar eq-3"></span>
            <span class="eq-bar eq-4"></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 5. Page Routing
current = st.session_state["current_page"]

if current == "Dashboard":
    def _on_view_run(run_id: str):
        st.session_state["active_run_id"] = run_id
        st.session_state["current_page"] = "History"
        st.session_state["sidebar_nav"] = "Invoices & History"
        st.rerun()

    def _on_nav_process():
        st.session_state["current_page"] = "Process Invoice"
        st.session_state["sidebar_nav"] = "Process Invoice"
        st.rerun()

    def _on_nav_history():
        st.session_state["current_page"] = "History"
        st.session_state["sidebar_nav"] = "Invoices & History"
        st.rerun()

    render_dashboard_page(
        repository=repository,
        on_view_run=_on_view_run,
        on_navigate_process=_on_nav_process,
        on_navigate_history=_on_nav_history
    )

elif current == "Process Invoice":
    # Check if a processing run was triggered
    if st.session_state.get("pending_upload_bytes"):
        file_bytes = st.session_state["pending_upload_bytes"]
        filename = st.session_state["pending_upload_filename"]
        # Clear pending trigger
        st.session_state["pending_upload_bytes"] = None
        st.session_state["pending_upload_filename"] = None

        # Execute live pipeline
        run_record = execute_and_render_live_pipeline(
            file_bytes=file_bytes,
            filename=filename,
            orchestrator=orchestrator
        )
        st.session_state["last_completed_run"] = run_record

    if st.session_state.get("last_completed_run"):
        st.markdown("<hr style='margin: 1.25rem 0;'/>", unsafe_allow_html=True)
        col_back, _ = st.columns([1.5, 4])
        with col_back:
            if st.button("← Upload Another Invoice", use_container_width=True):
                st.session_state["last_completed_run"] = None
                st.rerun()
        render_decision_report(st.session_state["last_completed_run"])
    else:
        def _start_processing(b: bytes, name: str):
            st.session_state["pending_upload_bytes"] = b
            st.session_state["pending_upload_filename"] = name
            st.rerun()

        render_upload_page(on_start_processing=_start_processing)

elif current == "Review Queue":
    render_review_queue_page(
        repository=repository,
        selected_run_id=st.session_state.get("active_run_id")
    )

elif current == "History":
    render_history_page(
        repository=repository,
        selected_run_id=st.session_state.get("active_run_id")
    )

elif current == "Vendor Network":
    render_vendors_page(repository=repository)

elif current == "PO Management":
    render_po_page(repository=repository)

elif current == "Policies & Master Data":
    render_policies_page()

elif current == "Seller Responses":
    render_seller_responses_page(repository=repository)

elif current == "Disputes & Resolutions":
    render_disputes_page(repository=repository)
