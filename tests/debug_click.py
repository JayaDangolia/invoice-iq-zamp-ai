from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, channel="msedge")
    page = b.new_page()
    page.goto("http://localhost:8501")
    page.wait_for_selector('[data-testid="stSidebar"]')
    time.sleep(2)

    btn = page.locator('div[class*="st-key-kpi_card_ov_pending"] button')
    print("Button count:", btn.count())
    print("Button box:", btn.bounding_box())
    print("Button is visible:", btn.is_visible())
    print("Button text:", btn.text_content())

    # Try clicking
    print("Attempting click...")
    btn.click(force=True)
    time.sleep(3)

    # Check page state
    header = page.locator('h1').text_content()
    print("Current page h1:", header)
    selected = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"]')
    print("Selected nav:", selected.text_content().strip())

    b.close()
