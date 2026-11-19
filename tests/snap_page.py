import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS = Path("screenshots")

def snap(nav_name, filename):
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto("http://localhost:8501", wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # Find option matching nav_name
        opt = page.locator(f"section[data-testid='stSidebar'] label:has-text('{nav_name}')")
        opt.scroll_into_view_if_needed()
        opt.click()
        page.wait_for_timeout(3000)

        page.screenshot(path=str(SHOTS / filename), full_page=False)
        print(f"Captured {filename} for {nav_name} -> Headings: {page.locator('h1').all_inner_texts()}")
        browser.close()

if __name__ == "__main__":
    snap("Review Queue", "03_review_queue_page.png")
    snap("Invoices & History", "04_history_audit_page.png")
    snap("Policies & Master Data", "05_policies_page.png")
