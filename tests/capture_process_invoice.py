import time
from pathlib import Path
from playwright.sync_api import sync_playwright

shot_path = Path("C:/Users/Jaya Dangolia/.gemini/antigravity/brain/fd692549-e959-4276-9648-75d4823dab7a/screenshots/PAGE_02_PROCESS_INVOICE.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501", timeout=30000)
    page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
    time.sleep(2)

    # Click Process Invoice
    opt = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("Process Invoice")')
    opt.click()
    time.sleep(3)

    page.screenshot(path=str(shot_path), full_page=False)
    print("CAPTURED: PAGE_02_PROCESS_INVOICE.png to", shot_path)
    browser.close()
