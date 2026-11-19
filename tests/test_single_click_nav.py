import time
from playwright.sync_api import sync_playwright

NAV_ITEMS = [
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

def test_clicks():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
        time.sleep(2)

        print("\n--- TESTING SINGLE CLICK SIDEBAR NAVIGATION ---")
        for item in NAV_ITEMS:
            # Locate option
            opt = page.locator(f'[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("{item}")')
            assert opt.count() > 0, f"Option '{item}' not found!"
            
            # Click ONCE
            t0 = time.time()
            opt.click()
            time.sleep(1.5)  # wait for Streamlit smooth rerun
            
            # Verify which item is selected in DOM
            selected = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"]')
            selected_text = selected.text_content().strip() if selected.count() > 0 else "NONE"
            elapsed = time.time() - t0
            
            print(f"Clicked once on '{item}' -> Selected in DOM: '{selected_text}' ({elapsed:.2f}s)")
            assert item in selected_text, f"FAIL: Expected '{item}', got '{selected_text}'"

        print("\nALL 9 OPTIONS SWITCHED ON A SINGLE CLICK WITH ZERO JUMPING!")
        browser.close()

if __name__ == "__main__":
    test_clicks()
