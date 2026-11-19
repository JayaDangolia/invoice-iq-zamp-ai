import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS = Path("screenshots")
SHOTS.mkdir(exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    
    # 1. Overview / Dashboard
    print("[1/5] Loading Overview Dashboard...")
    page.goto("http://localhost:8501", wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / "01_executive_dashboard_IMAGE1.png"), full_page=False)

    # 2. Process Invoice
    print("[2/5] Loading Process Invoice...")
    page.locator("section[data-testid='stSidebar'] [data-testid='stRadioOption']").nth(1).click()
    page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / "02_process_invoice_page.png"), full_page=False)

    # 3. Review Queue
    print("[3/5] Loading Review Queue...")
    page.locator("section[data-testid='stSidebar'] [data-testid='stRadioOption']").nth(2).click()
    page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / "03_review_queue_page.png"), full_page=False)

    # 4. History
    print("[4/5] Loading Invoices & History...")
    page.locator("section[data-testid='stSidebar'] [data-testid='stRadioOption']").nth(3).click()
    page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / "04_history_audit_page.png"), full_page=False)

    # 5. Policies
    print("[5/5] Loading Policies & Master Data...")
    page.locator("section[data-testid='stSidebar'] [data-testid='stRadioOption']").nth(6).click()
    page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / "05_policies_page.png"), full_page=False)

    browser.close()
    print("ALL 5 CORE WORKSPACE PAGES CAPTURED SUCCESSFULLY!")
