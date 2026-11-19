from playwright.sync_api import sync_playwright
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOT_PATH = Path("screenshots/IMAGE1_REPLICA_VERIFICATION.png")

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    
    # Check computed styles
    sidebar_bg = page.locator("section[data-testid='stSidebar']").evaluate("el => window.getComputedStyle(el).backgroundColor")
    app_bg = page.locator(".stApp").evaluate("el => window.getComputedStyle(el).backgroundColor")
    print("sidebar_bg:", sidebar_bg)
    print("app_bg:", app_bg)
    
    # Save full page screenshot
    page.screenshot(path=str(SHOT_PATH), full_page=True)
    print(f"Full page screenshot saved to {SHOT_PATH} ({SHOT_PATH.stat().st_size:,} bytes)")
    
    # Save exact 1440x900 viewport screenshot
    viewport_shot = Path("screenshots/IMAGE1_VIEWPORT_1440x900.png")
    page.screenshot(path=str(viewport_shot), full_page=False)
    print(f"Viewport screenshot saved to {viewport_shot} ({viewport_shot.stat().st_size:,} bytes)")

    # Scroll down to reveal full table rows and capture scrolled table view
    page.evaluate("() => { const el = document.querySelector('#stMain') || document.querySelector('main'); if (el) el.scrollTop = 380; }")
    page.wait_for_timeout(1000)
    scrolled_shot = Path("screenshots/IMAGE1_TABLE_SCROLLED.png")
    page.screenshot(path=str(scrolled_shot), full_page=False)
    print(f"Scrolled table screenshot saved to {scrolled_shot} ({scrolled_shot.stat().st_size:,} bytes)")
    browser.close()
