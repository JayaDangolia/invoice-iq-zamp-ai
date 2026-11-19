import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path("C:/Users/Jaya Dangolia/.gemini/antigravity/brain/fd692549-e959-4276-9648-75d4823dab7a/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501", timeout=30000)
    page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
    time.sleep(3)

    # 1. Capture Overview (Page 1)
    opt1 = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("Overview")')
    if opt1.count() > 0:
        opt1.click()
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "PAGE_01_OVERVIEW.png"), full_page=False)
        print("Captured PAGE_01_OVERVIEW.png")

    # 2. Capture Vendor Network (Page 5)
    opt5 = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("Vendor Network")')
    if opt5.count() > 0:
        opt5.click()
        time.sleep(3)
        page.screenshot(path=str(SCREENSHOTS_DIR / "PAGE_05_VENDOR_NETWORK.png"), full_page=False)
        print("Captured PAGE_05_VENDOR_NETWORK.png")

    browser.close()
    print("DONE CAPTURING BOTH PAGES!")
