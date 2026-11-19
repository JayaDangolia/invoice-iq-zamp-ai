import sys
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501", wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    options = page.locator("section[data-testid='stSidebar'] [data-testid='stRadioOption']").all()
    print("Options count:", len(options))
    for i, opt in enumerate(options):
        print(f"Option {i}: {repr(opt.inner_text())}")

    print("\nClicking Option 6 (Policies & Master Data)...")
    options[6].click()
    page.wait_for_timeout(2500)
    print("Headings after click:", page.locator("h1").all_inner_texts())
    page.screenshot(path="screenshots/CLICK_POLICIES_RESULT.png")
    browser.close()
