import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path("C:/Users/Jaya Dangolia/.gemini/antigravity/brain/fd692549-e959-4276-9648-75d4823dab7a/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("Overview", "PAGE_01_OVERVIEW.png"),
    ("Process Invoice", "PAGE_02_PROCESS_INVOICE.png"),
    ("Review Queue", "PAGE_03_REVIEW_QUEUE.png"),
    ("Invoices & History", "PAGE_04_HISTORY.png"),
    ("Vendor Network", "PAGE_05_VENDOR_NETWORK.png"),
    ("PO Management", "PAGE_06_PO_MANAGEMENT.png"),
    ("Policies & Master Data", "PAGE_07_POLICIES.png"),
    ("Seller Responses", "PAGE_08_SELLER_RESPONSES.png"),
    ("Disputes & Resolutions", "PAGE_09_DISPUTES.png"),
]

def capture_clean():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        
        for nav_name, filename in PAGES:
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            page.goto("http://localhost:8501", timeout=30000)
            page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
            time.sleep(3)
            
            print(f"Navigating cleanly to: '{nav_name}'...")
            opt = page.locator(f'[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("{nav_name}")')
            if opt.count() > 0:
                opt.click()
                time.sleep(4)
                
                # Check selected
                sel = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"]')
                sel_text = sel.text_content().strip() if sel.count() > 0 else "NONE"
                print(f"Selected: '{sel_text}'")
                
                shot_path = SCREENSHOTS_DIR / filename
                page.screenshot(path=str(shot_path), full_page=False)
                print(f"Captured: {filename}")
            else:
                print(f"ERROR: Option '{nav_name}' not found!")
                
            page.close()
            
        browser.close()
        print("\nALL 9 PAGES CAPTURED CLEANLY!")

if __name__ == "__main__":
    capture_clean()
