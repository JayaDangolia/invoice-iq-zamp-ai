import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS = Path("screenshots")
SHOTS.mkdir(exist_ok=True)

def verify():
    targets = [
        ("Process Invoice", "Process an invoice", "02_process_invoice_page.png"),
        ("Review Queue", "Review Queue", "03_review_queue_page.png"),
        ("Invoices & History", "Processing History", "04_history_audit_page.png"),
        ("Policies & Master Data", "Policy Configuration", "05_policies_page.png"),
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Checking Overview...")
        page.goto("http://localhost:8501", wait_until="domcontentloaded")
        page.wait_for_timeout(2500)
        assert page.locator("text=Accounts Payable").first.is_visible(), "Overview page failed"
        print("[OK] Overview verified")

        for nav_name, expected_text, shot_name in targets:
            print(f"Navigating to {nav_name}...")
            opt = page.locator(f"section[data-testid='stSidebar'] label:has-text('{nav_name}')")
            opt.scroll_into_view_if_needed()
            opt.click()
            page.wait_for_timeout(2500)
            page.screenshot(path=str(SHOTS / shot_name), full_page=False)
            assert page.locator(f"text={expected_text}").first.is_visible(), f"{nav_name} failed to load"
            print(f"[OK] {nav_name} verified")

        browser.close()
        print("\nALL WORKSPACE NAVIGATION PAGES VERIFIED AND FUNCTIONING FLAWLESSLY!")

if __name__ == "__main__":
    verify()
