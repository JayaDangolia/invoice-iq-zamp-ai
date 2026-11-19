"""Premium Enterprise Fintech Design System for InvoiceIQ.
Pixel-perfect recreation of desired AP & Vendor Hub design (Image 7 target, Images 2-6 components).
"""

def get_custom_css() -> str:
    return """
    <style>
    /* -------------------------------------------------------------
       1. GLOBAL DESIGN TOKENS & RESET (IMAGE 7)
       ------------------------------------------------------------- */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --color-sidebar-bg: #090C1A;
        --color-sidebar-surface: #12162B;
        --color-sidebar-border: rgba(255, 255, 255, 0.08);
        --color-sidebar-text: #94A3B8;
        --color-sidebar-active: #6366F1;
        --bg-app: #F4F6FC;
        --surface-white: #FFFFFF;
        --text-dark: #0F172A;
        --text-heading: #1E293B;
        --text-muted: #64748B;
        --text-subtle: #94A3B8;
        --border-card: #E2E8F0;
        --border-subtle: #EDF2F7;
        
        --color-primary-indigo: #4F46E5;
        --color-primary-purple: #6366F1;
        --color-primary-violet: #8B5CF6;
        --color-primary-blue: #3B82F6;

        --font-sans: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
    }

    html, body, [class*="css"], .stApp {
        font-family: var(--font-sans) !important;
        background-color: var(--bg-app) !important;
        background: var(--bg-app) !important;
        color: var(--text-dark) !important;
        -webkit-font-smoothing: antialiased;
    }

    /* Seamless lavender-to-white background with subtle ambient glows (Image 3 & 7) */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main,
    [data-testid="stAppViewBlockContainer"] {
        background-color: #F4F6FC !important;
        background: 
            radial-gradient(ellipse 65% 50% at 75% 0%, rgba(196, 181, 253, 0.4) 0%, rgba(224, 231, 255, 0.25) 40%, transparent 70%),
            radial-gradient(circle at 10% 12%, rgba(238, 242, 255, 0.6) 0%, transparent 45%),
            linear-gradient(180deg, #F6F8FE 0%, #EEF2FB 100%) !important;
    }

    /* Streamlit padding overrides (Optimized for 1440x900 viewport) */
    .block-container {
        padding-top: 1.15rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1440px !important;
    }

    /* Hide Streamlit default chrome & decoration */
    #MainMenu, footer, header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* -------------------------------------------------------------
       2. REFINED DARK NAVY SIDEBAR (IMAGE 6)
       ------------------------------------------------------------- */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] > div:first-child {
        background-color: var(--color-sidebar-bg) !important;
        background: linear-gradient(180deg, #090C1A 0%, #10142A 50%, #0B0E20 100%) !important;
        border-right: 1px solid var(--color-sidebar-border) !important;
        width: 295px !important;
    }
    [data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] > div {
        padding-top: 1.15rem !important;
        padding-left: 1.15rem !important;
        padding-right: 1.15rem !important;
        box-sizing: border-box !important;
    }

    /* Hide Streamlit Radio Default Label */
    [data-testid="stRadio"] [data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Sidebar Radio Button Restyling into High-End Navigation Items (IMAGE 6) */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 0.2rem !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"] {
        width: 100% !important;
        padding: 0.6rem 0.9rem !important;
        border-radius: 12px !important;
        background-color: transparent !important;
        transition: all 0.18s ease !important;
        cursor: pointer !important;
        margin-bottom: 0 !important;
        border: none !important;
        display: flex !important;
        align-items: center !important;
        box-sizing: border-box !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"]:hover {
        background-color: rgba(255, 255, 255, 0.06) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"]:hover p {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] {
        background: linear-gradient(135deg, #4338CA 0%, #6366F1 50%, #4F46E5 100%) !important;
        box-shadow: 0 4px 16px rgba(99, 102, 241, 0.45) !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stRadioOption"] label {
        width: 100% !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadioOption"] p {
        color: #94A3B8 !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        margin: 0 !important;
        line-height: 1.2 !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* Seamless Click & Invisible Radio Control */
    [data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child,
    [data-testid="stSidebar"] [data-testid="stRadioOption"] div[class*="ex50key4"],
    [data-testid="stSidebar"] [data-testid="stRadioOption"] div[data-testid="stRadioControl"],
    [data-testid="stSidebar"] [data-testid="stRadioOption"] input[type="radio"] {
        position: absolute !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadioOption"] {
        user-select: none !important;
        -webkit-user-select: none !important;
    }

    /* Clean Vector Icons for Sidebar Options (Image 6) */
    /* 1. Overview Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(1) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23CBD5E1' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'%3E%3C/path%3E%3Cpolyline points='9 22 9 12 15 12 15 22'%3E%3C/polyline%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(1) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'%3E%3C/path%3E%3Cpolyline points='9 22 9 12 15 12 15 22'%3E%3C/polyline%3E%3C/svg%3E");
    }

    /* 2. Process Invoice Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(2) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'%3E%3C/path%3E%3Cpolyline points='17 8 12 3 7 8'%3E%3C/polyline%3E%3Cline x1='12' y1='3' x2='12' y2='15'%3E%3C/line%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(2) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'%3E%3C/path%3E%3Cpolyline points='17 8 12 3 7 8'%3E%3C/polyline%3E%3Cline x1='12' y1='3' x2='12' y2='15'%3E%3C/line%3E%3C/svg%3E");
    }

    /* 3. Review Queue Icon + Circular Orange Badge (Image 6) */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'%3E%3C/rect%3E%3Cline x1='9' y1='9' x2='15' y2='9'%3E%3C/line%3E%3Cline x1='9' y1='13' x2='15' y2='13'%3E%3C/line%3E%3Cline x1='9' y1='17' x2='11' y2='17'%3E%3C/line%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'%3E%3C/rect%3E%3Cline x1='9' y1='9' x2='15' y2='9'%3E%3C/line%3E%3Cline x1='9' y1='13' x2='15' y2='13'%3E%3C/line%3E%3Cline x1='9' y1='17' x2='11' y2='17'%3E%3C/line%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(3) [data-testid="stRadioOption"] p::after {
        content: "3";
        margin-left: auto;
        background: #F59E0B;
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
        box-shadow: 0 2px 5px rgba(245, 158, 11, 0.4);
    }

    /* 4. Invoices & History Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(4) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'%3E%3C/path%3E%3Cpolyline points='14 2 14 8 20 8'%3E%3C/polyline%3E%3Cline x1='16' y1='13' x2='8' y2='13'%3E%3C/line%3E%3Cline x1='16' y1='17' x2='8' y2='17'%3E%3C/line%3E%3Cline x1='10' y1='9' x2='8' y2='9'%3E%3C/line%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(4) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'%3E%3C/path%3E%3Cpolyline points='14 2 14 8 20 8'%3E%3C/polyline%3E%3Cline x1='16' y1='13' x2='8' y2='13'%3E%3C/line%3E%3Cline x1='16' y1='17' x2='8' y2='17'%3E%3C/line%3E%3Cline x1='10' y1='9' x2='8' y2='9'%3E%3C/line%3E%3C/svg%3E");
    }

    /* 5. Vendor Network Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(5) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'%3E%3C/path%3E%3Ccircle cx='9' cy='7' r='4'%3E%3C/circle%3E%3Cpath d='M23 21v-2a4 4 0 0 0-3-3.87'%3E%3C/path%3E%3Cpath d='M16 3.13a4 4 0 0 1 0 7.75'%3E%3C/path%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(5) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2'%3E%3C/path%3E%3Ccircle cx='9' cy='7' r='4'%3E%3C/circle%3E%3Cpath d='M23 21v-2a4 4 0 0 0-3-3.87'%3E%3C/path%3E%3Cpath d='M16 3.13a4 4 0 0 1 0 7.75'%3E%3C/path%3E%3C/svg%3E");
    }

    /* 6. PO Management Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(6) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z'%3E%3C/path%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(6) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z'%3E%3C/path%3E%3C/svg%3E");
    }

    /* 7. Policies & Master Data Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(7) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'%3E%3C/circle%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'%3E%3C/path%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(7) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='3'%3E%3C/circle%3E%3Cpath d='M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z'%3E%3C/path%3E%3C/svg%3E");
    }

    /* 8. Collaboration Header above item 8 */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(8)::before {
        content: "COLLABORATION";
        display: block;
        font-size: 0.68rem;
        font-weight: 700;
        color: #64748B;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 1.15rem 0 0.45rem 0.4rem;
    }

    /* 8. Seller Responses Icon + Purple Badge 2 */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(8) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'%3E%3C/path%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(8) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'%3E%3C/path%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(8) [data-testid="stRadioOption"] p::after {
        content: "2";
        margin-left: auto;
        background: #8B5CF6;
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        line-height: 1;
        box-shadow: 0 2px 5px rgba(139, 92, 246, 0.4);
    }

    /* 9. Disputes & Resolutions Icon */
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(9) [data-testid="stRadioOption"] p::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 12px;
        flex-shrink: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v1'%3E%3C/path%3E%3Cpath d='M18 8h4a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-4'%3E%3C/path%3E%3Cpath d='M7 11h6'%3E%3C/path%3E%3Cpath d='M7 15h4'%3E%3C/path%3E%3C/svg%3E") no-repeat center;
        background-size: contain;
    }
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div:nth-child(9) [data-testid="stRadioOption"][data-selected="true"] p::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23FFFFFF' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v1'%3E%3C/path%3E%3Cpath d='M18 8h4a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-4'%3E%3C/path%3E%3Cpath d='M7 11h6'%3E%3C/path%3E%3Cpath d='M7 15h4'%3E%3C/path%3E%3C/svg%3E");
    }


    /* Sidebar Collaboration section styling (Image 6) */
    .sidebar-section-heading {
        font-size: 0.68rem;
        font-weight: 700;
        color: #64748B;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin: 1.15rem 0 0.45rem 0.4rem;
    }
    .sidebar-collab-row {
        box-sizing: border-box !important;
        width: 100% !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.55rem 0.65rem;
        border-radius: 10px;
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.15s ease;
        margin-bottom: 0.2rem;
    }
    .sidebar-collab-row:hover {
        background-color: rgba(255, 255, 255, 0.05);
        color: #FFFFFF;
    }
    .badge-pill-purple {
        background: #8B5CF6;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.72rem;
        font-weight: 700;
        box-shadow: 0 2px 5px rgba(139, 92, 246, 0.4);
    }

    /* AI Document Engine Box (Image 6) */
    .ai-engine-box {
        box-sizing: border-box !important;
        width: 100% !important;
        background: linear-gradient(135deg, #151833 0%, #1c2042 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 14px;
        padding: 0.85rem 0.95rem;
        margin-top: 1rem;
        position: relative;
    }
    .ai-engine-list {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
    }
    .ai-engine-item {
        font-size: 0.72rem;
        color: #CBD5E1;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .ai-check {
        color: #10B981;
        font-weight: 700;
    }

    /* System Operational Footer with Equalizer Waveform (Image 6) */
    .sidebar-system-status {
        box-sizing: border-box !important;
        width: 100% !important;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-top: 1.15rem;
        padding: 0.75rem 0.2rem 0 0.2rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .status-dot-green {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
        display: inline-block;
    }
    .equalizer-waveform {
        display: flex;
        gap: 2.5px;
        align-items: flex-end;
        height: 16px;
    }
    .eq-bar {
        width: 3px;
        background: #10B981;
        border-radius: 1px;
    }
    .eq-1 { height: 6px; }
    .eq-2 { height: 14px; }
    .eq-3 { height: 9px; }
    .eq-4 { height: 16px; }

    /* -------------------------------------------------------------
       3. TOP DASHBOARD BANNER & CONTROLS (IMAGE 3)
       ------------------------------------------------------------- */
    .dashboard-header-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.65rem;
        position: relative;
    }
    .header-ambient-wave {
        position: absolute;
        top: -15px;
        right: 0;
        width: 480px;
        height: 140px;
        pointer-events: none;
        z-index: 0;
    }
    .greeting-line {
        font-size: 0.95rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.15rem;
        position: relative;
        z-index: 1;
    }
    .headline-main {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.5px;
        line-height: 1.15;
        margin-bottom: 0.15rem;
        position: relative;
        z-index: 1;
    }
    .gradient-purple-text {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .subtext-line {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    .top-meta-controls {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        position: relative;
        z-index: 2;
    }
    .date-pill-badge {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(226, 232, 240, 0.9);
        border-radius: 10px;
        padding: 0.45rem 0.85rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: #334155;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }
    .icon-circle-button {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(226, 232, 240, 0.9);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #475569;
        position: relative;
        cursor: pointer;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
    }
    .icon-notif-dot {
        position: absolute;
        top: 6px;
        right: 6px;
        width: 7px;
        height: 7px;
        background-color: #EF4444;
        border-radius: 50%;
        border: 1.5px solid #FFFFFF;
    }
    .avatar-circle {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #A855F7 0%, #8B5CF6 100%);
        color: #FFFFFF;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.95rem;
        box-shadow: 0 2px 8px rgba(168, 85, 247, 0.3);
    }

    /* Sub-Header Actions: Buyer/Seller view toggles & Process Button (Image 3) */
    .view-switchers {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 0.65rem;
    }
    .view-pill-active {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 9px;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.45rem 1rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        box-sizing: border-box;
        gap: 0.45rem;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.35);
    }
    .view-pill-inactive {
        background: rgba(255, 255, 255, 0.7);
        color: #475569;
        border: 1px solid rgba(203, 213, 225, 0.7);
        border-radius: 9px;
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.45rem 1rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        box-sizing: border-box;
        gap: 0.45rem;
    }

    /* Clickable View Switchers */
    div[data-testid="stColumn"]:has(div[class*="st-key-btn_view_"]) {
        position: relative !important;
        cursor: pointer !important;
    }
    div[data-testid="stColumn"]:has(div[class*="st-key-btn_view_"]) div[data-testid="stMarkdownContainer"],
    div[data-testid="stColumn"]:has(div[class*="st-key-btn_view_"]) .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-btn_view_"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 25 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-btn_view_"] button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        border: none !important;
        background: transparent !important;
        cursor: pointer !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    .view-pill-active, .view-pill-inactive {
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        user-select: none !important;
        -webkit-user-select: none !important;
    }
    div[data-testid="stColumn"]:has(div[class*="st-key-btn_view_"]):hover .view-pill-inactive {
        background: rgba(255, 255, 255, 0.95) !important;
        border-color: #818CF8 !important;
        color: #4338CA !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.15) !important;
        transform: translateY(-1px) !important;
    }
    div[data-testid="stColumn"]:has(div[class*="st-key-btn_view_"]):hover .view-pill-active {
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* -------------------------------------------------------------
       4. FOUR PASTEL KPI CARDS WITH FLOWING WAVES (IMAGE 2)
       ------------------------------------------------------------- */
    .kpi-deck-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.85rem;
        margin-bottom: 0.85rem;
    }
    .kpi-card-pastel {
        border-radius: 16px;
        padding: 1.15rem 1.15rem 1rem 1.15rem;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 130px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .kpi-card-pastel:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }
    .kpi-card-pastel.card-blue {
        background: linear-gradient(180deg, #EFF6FF 0%, #F5F9FF 60%, #DBEAFE 100%);
        border: 1.5px solid #BFDBFE;
    }
    .kpi-card-pastel.card-green {
        background: linear-gradient(180deg, #ECFDF5 0%, #F4FDF8 60%, #D1FAE5 100%);
        border: 1.5px solid #A7F3D0;
    }
    .kpi-card-pastel.card-amber {
        background: linear-gradient(180deg, #FFFBEB 0%, #FFFDF5 60%, #FEF3C7 100%);
        border: 1.5px solid #FDE68A;
    }
    .kpi-card-pastel.card-coral {
        background: linear-gradient(180deg, #FEF2F2 0%, #FFF5F5 60%, #FEE2E2 100%);
        border: 1.5px solid #FECACA;
    }
    .kpi-card-pastel.card-purple {
        background: linear-gradient(180deg, #F5F3FF 0%, #FAF7FF 60%, #EDE9FE 100%);
        border: 1.5px solid #DDD6FE;
    }
    .kpi-card-pastel.card-indigo {
        background: linear-gradient(180deg, #EEF2FF 0%, #F5F7FF 60%, #E0E7FF 100%);
        border: 1.5px solid #C7D2FE;
    }

    .kpi-top-row {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        margin-bottom: 0.4rem;
        position: relative;
        z-index: 2;
    }
    .kpi-icon-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    }
    .kpi-icon-circle.icon-blue { background: #DBEAFE; color: #2563EB; }
    .kpi-icon-circle.icon-green { background: #D1FAE5; color: #059669; }
    .kpi-icon-circle.icon-amber { background: #FEF3C7; color: #D97706; }
    .kpi-icon-circle.icon-coral { background: #FEE2E2; color: #DC2626; }
    .kpi-icon-circle.icon-purple { background: #EDE9FE; color: #7C3AED; }
    .kpi-icon-circle.icon-indigo { background: #E0E7FF; color: #4F46E5; }

    .kpi-title-label {
        font-size: 0.88rem;
        font-weight: 700;
        color: #1E293B;
        line-height: 1.2;
    }
    .kpi-metric-wrap {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-top: 0.15rem;
        position: relative;
        z-index: 2;
    }
    .kpi-metric-big {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1;
        letter-spacing: -0.6px;
        font-variant-numeric: tabular-nums;
    }
    .kpi-trend-pill {
        font-size: 0.74rem;
        font-weight: 700;
        border-radius: 9999px;
        padding: 0.18rem 0.55rem;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        line-height: 1;
    }
    .trend-green { background: #D1FAE5; color: #047857; }
    .trend-coral { background: #FEE2E2; color: #B91C1C; }
    .trend-amber { background: #FEF3C7; color: #B45309; }
    .trend-blue { background: #DBEAFE; color: #1D4ED8; }
    .trend-purple { background: #EDE9FE; color: #6D28D9; }

    .kpi-subtitle-text {
        font-size: 0.78rem;
        color: #64748B;
        font-weight: 500;
        margin-top: 0.45rem;
        position: relative;
        z-index: 2;
    }

    .kpi-bottom-wave {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 48px;
        pointer-events: none;
        border-radius: 0 0 16px 16px;
        overflow: hidden;
        z-index: 1;
    }

    /* -------------------------------------------------------------
       Clickable KPI Card Container & Transparent Overlay Button
       ------------------------------------------------------------- */
    div[data-testid="stColumn"]:has(div[class*="st-key-kpi_card_"]) {
        position: relative !important;
        cursor: pointer !important;
    }
    div[data-testid="stColumn"]:has(div[class*="st-key-kpi_card_"]) div[data-testid="stVerticalBlock"] {
        position: relative !important;
    }
    div[class*="st-key-kpi_card_"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 25 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-kpi_card_"] .stButton {
        width: 100% !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-kpi_card_"] button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        border: none !important;
        background: transparent !important;
        cursor: pointer !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    div[data-testid="stColumn"]:has(div[class*="st-key-kpi_card_"]):hover .kpi-card-pastel {
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 28px -4px rgba(79, 70, 229, 0.16), 0 4px 10px -2px rgba(0, 0, 0, 0.06) !important;
        border-color: #818CF8 !important;
    }

    /* Sidebar Brand Block Logo Clickable Overlay */
    .st-key-btn_logo_home,
    [data-testid="stSidebar"] div[class*="st-key-btn_logo_home"],
    section[data-testid="stSidebar"] div[class*="st-key-btn_logo_home"] {
        position: absolute !important;
        top: 18px !important;
        left: 18px !important;
        width: 255px !important;
        height: 62px !important;
        z-index: 100 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .st-key-btn_logo_home button,
    [data-testid="stSidebar"] div[class*="st-key-btn_logo_home"] button,
    section[data-testid="stSidebar"] div[class*="st-key-btn_logo_home"] button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        border: none !important;
        background: transparent !important;
        cursor: pointer !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }
    .sidebar-brand-block {
        cursor: pointer !important;
        transition: transform 0.15s ease, opacity 0.15s ease !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"]:has(div[class*="st-key-btn_logo_home"]):hover .sidebar-brand-block {
        opacity: 0.9 !important;
        transform: translateX(2px) !important;
    }

    /* Overview Header Logo Clickable Overlay */
    div[data-testid="stColumn"]:has(div[class*="st-key-btn_ov_header_logo"]) {
        position: relative !important;
    }
    div[class*="st-key-btn_ov_header_logo"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 25 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[class*="st-key-btn_ov_header_logo"] button {
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        border: none !important;
        background: transparent !important;
        cursor: pointer !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }

    /* Prominent Back Navigation Buttons */
    div[class*="st-key-btn_back_"] button {
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 0.84rem !important;
        border-radius: 10px !important;
        padding: 0.45rem 1rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.18s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.4rem !important;
    }
    div[class*="st-key-btn_back_"] button:hover {
        background: #F8FAFC !important;
        border-color: #6366F1 !important;
        color: #4F46E5 !important;
        transform: translateX(-2px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
    }

    /* -------------------------------------------------------------
       5. ANALYTICS DUAL CARDS (IMAGE 4)
       ------------------------------------------------------------- */
    .analytics-dual-grid {
        display: grid;
        grid-template-columns: 1fr 1.35fr;
        gap: 0.85rem;
        margin-bottom: 0.85rem;
    }
    .analytics-panel {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        display: flex;
        flex-direction: column;
        height: 220px;
    }
    .panel-header-line {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }
    .panel-title-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
        font-weight: 700;
        color: #0F172A;
    }
    .panel-info-glyph {
        color: #94A3B8;
        font-size: 0.82rem;
        cursor: pointer;
    }
    .panel-action-link {
        font-size: 0.82rem;
        font-weight: 600;
        color: #6366F1;
        text-decoration: none;
        cursor: pointer;
    }
    .panel-action-link:hover {
        text-decoration: underline;
    }

    /* Donut Layout (Image 4) */
    .donut-layout-box {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.4rem;
        padding: 0.2rem 0;
        height: 100%;
    }
    .donut-chart-wrapper {
        position: relative;
        width: 130px;
        height: 130px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .donut-chart-wrapper circle {
        transition: stroke-width 0.2s ease, filter 0.2s ease;
        cursor: pointer;
    }
    .donut-chart-wrapper circle:hover {
        stroke-width: 20;
        filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.15));
    }
    .donut-center-label {
        position: absolute;
        text-align: center;
        pointer-events: none;
    }
    .donut-center-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1;
        letter-spacing: -0.5px;
        font-variant-numeric: tabular-nums;
    }
    .donut-center-sub {
        font-size: 0.74rem;
        color: #64748B;
        font-weight: 600;
        margin-top: 2px;
    }
    .donut-legend-col {
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
        flex: 1;
    }
    .legend-row-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.84rem;
        padding: 0.2rem 0.4rem;
        border-radius: 6px;
        transition: background-color 0.12s ease;
    }
    .legend-row-item:hover {
        background-color: #F8FAFC;
    }
    .legend-label-wrap {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #334155;
        font-weight: 500;
    }
    .legend-bullet {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }
    .legend-val-num {
        font-weight: 700;
        color: #0F172A;
        font-variant-numeric: tabular-nums;
    }

    /* -------------------------------------------------------------
       6. RECENT PROCESSING ACTIVITY (IMAGE 5)
       ------------------------------------------------------------- */
    .activity-table-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        margin-top: 0.85rem;
    }
    .table-top-toolbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.85rem;
    }
    .table-filter-cluster {
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .filter-pill-dropdown {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 0.35rem 0.8rem;
        font-size: 0.78rem;
        font-weight: 500;
        color: #334155;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        cursor: pointer;
    }

    /* Activity Table Grid (Image 5) */
    .ent-table-head {
        display: grid;
        grid-template-columns: 1.6fr 1.9fr 0.9fr 1.1fr 1.4fr 1.4fr 1.6fr 0.9fr;
        gap: 0.5rem;
        padding: 0.55rem 0.75rem;
        background: #F8FAFC;
        border: 1px solid #EDF2F7;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 0.35rem;
    }

    /* Row Styling for Streamlit Columns (Image 5) */
    div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-btn_act_"]) {
        padding: 0.35rem 0.6rem !important;
        border-bottom: 1px solid #F1F5F9 !important;
        border-radius: 8px !important;
        align-items: center !important;
        min-height: 42px !important;
        margin-bottom: 0 !important;
        transition: background-color 0.12s ease !important;
    }
    div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-btn_act_"]):hover {
        background-color: #F8FAFC !important;
    }
    div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-btn_act_"]) div[data-testid="stColumn"]:last-child {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Table Action Buttons: Outlined Purple Pill (Image 5) */
    div[class*="st-key-btn_act_"] button {
        height: 28px !important;
        min-height: 28px !important;
        padding: 0 16px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        line-height: 1 !important;
        border-radius: 8px !important;
        border: 1.5px solid #6366F1 !important;
        background: transparent !important;
        background-color: transparent !important;
        color: #6366F1 !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }
    div[class*="st-key-btn_act_"] button p,
    div[class*="st-key-btn_act_"] button span,
    div[class*="st-key-btn_act_"] button div {
        color: #6366F1 !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
    }
    div[class*="st-key-btn_act_"] button:hover {
        border-color: #6366F1 !important;
        color: #FFFFFF !important;
        background: #6366F1 !important;
        background-color: #6366F1 !important;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.35) !important;
    }
    div[class*="st-key-btn_act_"] button:hover p,
    div[class*="st-key-btn_act_"] button:hover span,
    div[class*="st-key-btn_act_"] button:hover div {
        color: #FFFFFF !important;
    }

    /* Status Pills with Icons (Image 5) */
    .badge-status-approved {
        background: #D1FAE5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    .badge-status-review {
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FDE68A;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }
    .badge-status-rejected {
        background: #FEE2E2;
        color: #B91C1C;
        border: 1px solid #FECACA;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* -------------------------------------------------------------
       7. BUTTONS & CONTROLS REFINEMENT
       ------------------------------------------------------------- */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
        transform: translateY(-1px);
    }

    /* -------------------------------------------------------------
       8. GLOBAL WORKSPACE HEADERS & STEPPER (ENTERPRISE FINTECH)
       ------------------------------------------------------------- */
    .app-header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0.25rem 0.75rem 0.25rem;
        border-bottom: 1px solid rgba(226, 232, 240, 0.7);
        margin-bottom: 0.85rem;
    }
    .header-breadcrumb {
        font-size: 0.82rem;
        display: flex;
        align-items: center;
        letter-spacing: 0.2px;
    }
    .crumb-active {
        color: #4F46E5 !important;
        font-weight: 700 !important;
    }
    .header-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(240, 253, 244, 0.9);
        border: 1px solid #BBF7D0;
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
    }
    .status-dot-pulse {
        width: 7px;
        height: 7px;
        background-color: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }

    .page-title-container {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1.15rem;
    }
    .page-headline-wrap {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }
    .page-headline {
        font-size: 1.55rem !important;
        font-weight: 800 !important;
        color: #0F172A !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -0.4px !important;
        line-height: 1.2 !important;
    }
    .page-title-badge {
        background: #EEF2FF;
        color: #4338CA;
        border: 1px solid #C7D2FE;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }
    .page-subtext {
        font-size: 0.82rem;
        color: #64748B;
        margin-top: 0.2rem;
    }

    /* 4-Phase Stepper Funnel (Image 7 & Process Invoice) */
    .stepper-phase-container {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 0.85rem !important;
        margin-bottom: 1.25rem !important;
    }
    .stepper-phase-card {
        border-radius: 14px;
        padding: 0.95rem 1.05rem;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
        transition: all 0.15s ease;
    }
    .stepper-phase-card.phase-1 {
        background: linear-gradient(180deg, #EFF6FF 0%, #F5F9FF 60%, #DBEAFE 100%);
        border: 1.5px solid #BFDBFE;
    }
    .stepper-phase-card.phase-2 {
        background: linear-gradient(180deg, #F5F3FF 0%, #FAF7FF 60%, #EDE9FE 100%);
        border: 1.5px solid #DDD6FE;
    }
    .stepper-phase-card.phase-3 {
        background: linear-gradient(180deg, #ECFDF5 0%, #F4FDF8 60%, #D1FAE5 100%);
        border: 1.5px solid #A7F3D0;
    }
    .stepper-phase-card.phase-4 {
        background: linear-gradient(180deg, #FFFBEB 0%, #FFFDF5 60%, #FEF3C7 100%);
        border: 1.5px solid #FDE68A;
    }
    .stepper-phase-card.status-active {
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.2) !important;
        transform: translateY(-2px);
    }
    .stepper-phase-card.status-success {
        border-color: #10B981 !important;
    }
    .stepper-phase-card.status-warning {
        border-color: #F59E0B !important;
    }
    .stepper-phase-card.status-danger {
        border-color: #EF4444 !important;
    }

    .badge-status-neutral {
        background: #F1F5F9;
        color: #64748B;
        border: 1px solid #E2E8F0;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 0.2rem 0.65rem;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    .empty-state-card {
        background: #FFFFFF;
        border: 1.5px dashed #CBD5E1;
        border-radius: 14px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .empty-state-icon {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: #EEF2FF;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.85rem auto;
    }
    .empty-state-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.25rem;
    }
    .empty-state-desc {
        font-size: 0.84rem;
        color: #64748B;
        max-width: 420px;
        margin: 0 auto;
    }

    /* -------------------------------------------------------------
       9. ENHANCED FILE UPLOADER (EASY & HASSLE-FREE DRAG & DROP)
       ------------------------------------------------------------- */
    [data-testid="stFileUploader"] {
        width: 100% !important;
        margin: 0 auto !important;
    }
    [data-testid="stFileUploader"] section {
        border: 2px dashed #A5B4FC !important;
        border-radius: 14px !important;
        background: #F8FAFC !important;
        padding: 1.25rem 1rem !important;
        transition: all 0.2s ease !important;
        text-align: center !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #6366F1 !important;
        background: #EEF2FF !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.12) !important;
    }
    [data-testid="stFileUploader"] section button {
        background: #FFFFFF !important;
        border: 1.5px solid #6366F1 !important;
        color: #4F46E5 !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        border-radius: 8px !important;
        padding: 0.35rem 0.95rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stFileUploader"] section button:hover {
        background: #6366F1 !important;
        color: #FFFFFF !important;
        box-shadow: 0 3px 8px rgba(99, 102, 241, 0.3) !important;
    }
    </style>
    """
