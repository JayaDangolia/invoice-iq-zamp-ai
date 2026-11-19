from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1200})
    page.goto("http://localhost:8501", wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    
    # Check rows rendered
    rows = page.locator("button:has-text('Review'), button:has-text('View')").all()
    print("Action buttons count:", len(rows))
    
    # Scroll down and screenshot
    page.screenshot(path="screenshots/scroll_table_check.png", full_page=True)
    browser.close()
