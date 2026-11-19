from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, channel="msedge")
    page = b.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501")
    page.wait_for_selector('[data-testid="stSidebar"]')
    time.sleep(2)

    # Click KPI Card 3 (Pending Review)
    kpi_card_rev = page.locator('div[class*="st-key-kpi_card_ov_pending"] button')
    kpi_card_rev.click()
    time.sleep(2)

    page.screenshot(path="tests/test_rq_with_back.png")
    print("Captured tests/test_rq_with_back.png")
    b.close()
