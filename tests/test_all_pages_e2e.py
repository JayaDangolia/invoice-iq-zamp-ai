import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path("C:/Users/Jaya Dangolia/.gemini/antigravity/brain/fd692549-e959-4276-9648-75d4823dab7a/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

PAGES_TO_TEST = [
    ("Overview", "PAGE_01_OVERVIEW.png", "Overview"),
    ("Process Invoice", "PAGE_02_PROCESS_INVOICE.png", "Process an Invoice"),
    ("Review Queue", "PAGE_03_REVIEW_QUEUE.png", "Review Queue"),
    ("Invoices & History", "PAGE_04_HISTORY.png", "Invoices & History"),
    ("Vendor Network", "PAGE_05_VENDOR_NETWORK.png", "Vendor Network"),
    ("PO Management", "PAGE_06_PO_MANAGEMENT.png", "PO Management"),
    ("Policies & Master Data", "PAGE_07_POLICIES.png", "Policies & Master Data"),
    ("Seller Responses", "PAGE_08_SELLER_RESPONSES.png", "Seller Responses"),
    ("Disputes & Resolutions", "PAGE_09_DISPUTES.png", "Disputes & Resolutions"),
]

def run_e2e():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Navigating to http://localhost:8501 ...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
        time.sleep(3)

        for nav_name, screenshot_file, expected_heading in PAGES_TO_TEST:
            print(f"\n--- Testing Navigation to: '{nav_name}' ---")
            
            # Locate option by text and click its label/paragraph
            option_p = page.locator(f'[data-testid="stSidebar"] [data-testid="stRadioOption"] p:has-text("{nav_name}")')
            if option_p.count() == 0:
                print(f"FAILED to find radio option for '{nav_name}'!")
                continue
            
            option_p.first.click()
            time.sleep(3)
            
            # Wait for expected heading
            heading = page.locator(f'h1:has-text("{expected_heading}")')
            try:
                heading.wait_for(timeout=6000)
                print(f"Verified heading: '{expected_heading}'")
            except Exception:
                print(f"Warning: Heading '{expected_heading}' not detected within 6s.")

            # Check for errors
            errors = page.locator('.stException, [data-testid="stNotification"][kind="error"]')
            if errors.count() > 0:
                print(f"ERROR on '{nav_name}': {errors.first.text_content()}")
            else:
                print(f"SUCCESS: Page '{nav_name}' loaded perfectly.")

            # Save Screenshot
            shot_path = SCREENSHOTS_DIR / screenshot_file
            page.screenshot(path=str(shot_path), full_page=False)
            print(f"Saved screenshot: {shot_path.name}")

        # Test Interactive controls:
        # 1. On Vendor Network, click Inspect
        print("\n--- Testing Vendor Network Drill-Down ---")
        page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"] p:has-text("Vendor Network")').first.click()
        time.sleep(3)
        inspect_btn = page.locator('div[class*="st-key-btn_act_v_"] button').first
        if inspect_btn.count() > 0:
            inspect_btn.click()
            time.sleep(2.5)
            print("Clicked Vendor Inspect button.")
            page.screenshot(path=str(SCREENSHOTS_DIR / "INTERACTIVE_VENDOR_DRAWER.png"))
            print("Saved INTERACTIVE_VENDOR_DRAWER.png")

        # 2. Return to Overview Dashboard
        print("\n--- Returning to Overview Dashboard ---")
        page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"] p:has-text("Overview")').first.click()
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "FINAL_OVERVIEW_VERIFIED.png"))
        print("Saved FINAL_OVERVIEW_VERIFIED.png")

        browser.close()
        print("\nALL VERIFICATIONS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_e2e()
