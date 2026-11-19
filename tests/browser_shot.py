import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def test_screenshot():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        page = browser.new_page(viewport={"width": 1366, "height": 900})
        page.goto("http://localhost:8501", wait_until="networkidle")
        page.wait_for_timeout(3000)
        shot_path = SCREENSHOTS_DIR / "01_executive_dashboard.png"
        page.screenshot(path=str(shot_path), full_page=True)
        print(f"Captured: {shot_path} ({shot_path.stat().st_size} bytes)")
        browser.close()

if __name__ == "__main__":
    test_screenshot()
