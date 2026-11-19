from pathlib import Path
from typing import Callable, Optional
import streamlit as st
from config.settings import SAMPLE_INVOICES_DIR
from services.pdf_reader import PDFReaderService
from ui.components import (
    render_app_header,
    render_page_heading,
    render_four_phase_stepper
)

def render_upload_page(
    on_start_processing: Callable[[bytes, str], None]
) -> None:
    # 1. Top Enterprise Breadcrumb Bar
    render_app_header("Process Invoice")

    # 2. Compact Page Heading (Zero Scroll Layout)
    render_page_heading(
        title="Process an Invoice",
        subtitle="Ingest vendor documents, run automated OCR & validation funnels, and generate audit-backed decisions.",
        badge="Funnel v2.4 Ready"
    )

    # 3. 4-Phase Stepper Overview (Compact Funnel)
    render_four_phase_stepper(
        phase1_status="pending",
        phase2_status="pending",
        phase3_status="pending",
        phase4_status="pending",
        phase1_meta="Text & Metadata Ingestion",
        phase2_meta="Vendor & Duplication Check",
        phase3_meta="PO Matching & Tolerance Reconciliation",
        phase4_meta="Statutory Policy Determination"
    )

    preset_options = [
        ("-- Upload Custom PDF Document Above --", None),
        ("Standard Approval — TechCorp Solutions (Clean 3-Way Match)", "invoice_101_techcorp_happy_path.pdf"),
        ("Duplicate Submission — GreenLogistics Global (Renamed Submission)", "invoice_102_greenlogistics_duplicate_renamed.pdf"),
        ("Tolerance Exceeded — Apex Cloud Infrastructure (14% Price Variance)", "invoice_103_apex_amount_mismatch.pdf"),
        ("Missing PO Reference — TechCorp Solutions (Omitted Purchase Order)", "invoice_104_techcorp_missing_po.pdf"),
        ("Scanned Bitmap OCR — Bharat Security Systems (Degraded Image Scan)", "invoice_105_bharat_scanned.pdf"),
        ("Split PO Milestone 1 — TechCorp Solutions (₹40k / ₹100k Commitment)", "invoice_201_techcorp_split_po_part1.pdf"),
        ("Split PO Milestone 2 — TechCorp Solutions (₹35k / ₹60k Remaining)", "invoice_202_techcorp_split_po_part2.pdf"),
        ("Split PO Milestone 3 — TechCorp Solutions (₹25k / ₹25k Remaining)", "invoice_203_techcorp_split_po_part3.pdf"),
        ("Split PO Balance Exceeded — TechCorp Solutions (₹15k > ₹0 Balance)", "invoice_204_techcorp_split_po_exceeded.pdf"),
        ("Ambiguous PO Surfaced — TechCorp Solutions (Candidate PO Routing)", "invoice_205_techcorp_ambiguous_po.pdf"),
        ("Multi-Line Consulting — Synergy Digital Labs (Itemized Timesheet)", "invoice_106_synergy_consulting.pdf"),
        ("Unapproved Vendor — Quantum Office Supplies (Inactive Master Account)", "invoice_107_quantum_unapproved_vendor.pdf"),
    ]

    file_bytes: Optional[bytes] = None
    filename: Optional[str] = None

    # Check if a custom file is already uploaded in session state
    if "active_uploaded_file" in st.session_state and st.session_state["active_uploaded_file"] is not None:
        file_bytes = st.session_state["active_uploaded_file"]["bytes"]
        filename = st.session_state["active_uploaded_file"]["name"]

    # 4. If No File Loaded Yet: Show Centered, Non-Scrolling Hero Upload Zone
    if not file_bytes:
        _, col_center, _ = st.columns([1, 4.2, 1])
        with col_center:
            st.markdown("""
            <div class="table-container-card" style="padding: 1.5rem 2rem 1.25rem 2rem; margin-top: 0.5rem; text-align: center;">
                <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%); display: flex; align-items: center; justify-content: center; margin: 0 auto 0.75rem auto;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4F46E5" stroke-width="2.2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                </div>
                <div style="font-weight: 800; font-size: 1.25rem; color: #0F172A; margin-bottom: 0.25rem;">Upload Vendor Invoice</div>
                <div style="font-size: 0.82rem; color: #64748B; margin-bottom: 1.15rem; max-width: 480px; margin-left: auto; margin-right: auto; line-height: 1.4;">
                    Drop any machine-readable or scanned PDF invoice to run automated OCR, 3-way reconciliation, and financial policy rules.
                </div>
            """, unsafe_allow_html=True)

            uploaded = st.file_uploader(
                "Upload a PDF invoice",
                type=["pdf"],
                label_visibility="collapsed",
                key="direct_center_uploader",
                help="PDF format supported (machine-readable or scanned images)"
            )
            if uploaded is not None:
                st.session_state["active_uploaded_file"] = {
                    "bytes": uploaded.read(),
                    "name": uploaded.name
                }
                st.rerun()

            st.markdown("""
                <div style="display: flex; align-items: center; gap: 0.75rem; margin: 1.15rem 0 0.85rem 0;">
                    <div style="flex: 1; height: 1px; background: #E2E8F0;"></div>
                    <span style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.5px;">OR SELECT A VERIFIED BENCHMARK SCENARIO</span>
                    <div style="flex: 1; height: 1px; background: #E2E8F0;"></div>
                </div>
            """, unsafe_allow_html=True)

            selected_label = st.selectbox(
                "Benchmark Ground-Truth Scenarios:",
                [opt[0] for opt in preset_options],
                index=0,
                label_visibility="collapsed",
                key="preset_selector"
            )

            if selected_label and selected_label != preset_options[0][0]:
                for opt in preset_options:
                    if opt[0] == selected_label and opt[1]:
                        preset_path = SAMPLE_INVOICES_DIR / opt[1]
                        if preset_path.exists():
                            st.session_state["active_uploaded_file"] = {
                                "bytes": preset_path.read_bytes(),
                                "name": opt[1]
                            }
                            st.rerun()

            st.markdown("""
                <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 1.15rem; flex-wrap: wrap;">
                    <span style="background: #F1F5F9; color: #475569; font-size: 0.72rem; font-weight: 600; padding: 0.25rem 0.65rem; border-radius: 9999px;">📄 Machine-Readable PDF</span>
                    <span style="background: #F1F5F9; color: #475569; font-size: 0.72rem; font-weight: 600; padding: 0.25rem 0.65rem; border-radius: 9999px;">🔍 Scanned OCR Fallback</span>
                    <span style="background: #F1F5F9; color: #475569; font-size: 0.72rem; font-weight: 600; padding: 0.25rem 0.65rem; border-radius: 9999px;">⚖️ Partial / Split PO</span>
                    <span style="background: #F1F5F9; color: #475569; font-size: 0.72rem; font-weight: 600; padding: 0.25rem 0.65rem; border-radius: 9999px;">🛡️ Duplicate Check</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 5. Document Loaded: Display Split Inspection Workspace
    else:
        col_b, _ = st.columns([1.8, 4.2])
        with col_b:
            if st.button("← Back to Upload Selection", key="btn_back_upload_sel", use_container_width=True):
                st.session_state["active_uploaded_file"] = None
                st.rerun()

        col_preview, col_controls = st.columns([1.1, 0.9])

        with col_preview:
            st.markdown(f"""
            <div class="table-container-card" style="padding: 1.15rem 1.35rem; min-height: 440px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.65rem;">
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">Document Visual Inspection</div>
                    <div style="font-size: 0.75rem; color: #64748B;">High-Resolution Preview</div>
                </div>
            """, unsafe_allow_html=True)

            try:
                reader = PDFReaderService()
                img_bytes = reader.render_page_image(file_bytes, page_number=0, dpi=130)
                st.image(img_bytes, caption=f"Document: {filename}", use_container_width=True)
            except Exception as e:
                st.warning(f"Preview unavailable: {str(e)}")

            st.markdown("</div>", unsafe_allow_html=True)

        with col_controls:
            st.markdown("""
            <div class="table-container-card" style="padding: 1.15rem 1.35rem; min-height: 440px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem; border-bottom: 1px solid #F1F5F9; padding-bottom: 0.65rem;">
                    <div style="font-weight: 700; font-size: 0.95rem; color: #0F172A;">Pre-Flight Metadata & Trigger</div>
                    <div style="font-size: 0.75rem; color: #059669; font-weight: 600;">● Ready to Ingest</div>
                </div>
            """, unsafe_allow_html=True)

            reader = PDFReaderService()
            file_hash = reader.calculate_file_hash(file_bytes)
            file_size_kb = len(file_bytes) / 1024
            
            try:
                info = reader.inspect_and_extract_text(file_bytes)
                page_count = info["page_count"]
                doc_type = "Scanned Bitmap Document (OCR Required)" if info["needs_ocr"] else "Machine-Readable PDF"
                badge_color = "#D97706" if info["needs_ocr"] else "#059669"
            except Exception:
                page_count = 1
                doc_type = "PDF Document"
                badge_color = "#4338CA"

            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 1.15rem; margin-bottom: 1.25rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.65rem; font-size: 0.84rem;">
                    <span style="color: #64748B; font-weight: 500;">Filename:</span>
                    <span style="font-weight: 700; color: #0F172A; text-align: right; max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{filename}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.65rem; font-size: 0.84rem;">
                    <span style="color: #64748B; font-weight: 500;">Detected Classification:</span>
                    <span style="font-weight: 700; color: {badge_color};">{doc_type}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.65rem; font-size: 0.84rem;">
                    <span style="color: #64748B; font-weight: 500;">File Size:</span>
                    <span style="font-weight: 600; color: #1E293B;">{file_size_kb:,.1f} KB</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.65rem; font-size: 0.84rem;">
                    <span style="color: #64748B; font-weight: 500;">Page Count:</span>
                    <span style="font-weight: 600; color: #1E293B;">{page_count} page(s)</span>
                </div>
                <div style="border-top: 1px solid #E2E8F0; padding-top: 0.65rem; margin-top: 0.65rem;">
                    <span style="color: #64748B; font-size: 0.74rem; font-weight: 500;">SHA-256 Digest:</span><br/>
                    <span style="font-family: monospace; font-size: 0.72rem; color: #475569; word-break: break-all;">{file_hash}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⚡ Start Processing Pipeline →", type="primary", use_container_width=True):
                # Clean up session state before launching
                st.session_state["active_uploaded_file"] = None
                on_start_processing(file_bytes, filename)

            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("← Choose Different Document", use_container_width=True):
                st.session_state["active_uploaded_file"] = None
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
