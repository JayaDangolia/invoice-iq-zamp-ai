import time
from pathlib import Path
from playwright.sync_api import sync_playwright

shot_path = Path("C:/Users/Jaya Dangolia/.gemini/antigravity/brain/fd692549-e959-4276-9648-75d4823dab7a/screenshots/PAGE_05_VENDOR_NETWORK.png")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, channel="msedge")
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501", timeout=30000)
    page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
    time.sleep(3)
    opt = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("Vendor Network")')
    opt.click()
    time.sleep(4)
    page.screenshot(path=str(shot_path), full_page=False)
    browser.close()
    print("SUCCESS: Vendor Network captured to", shot_path)
