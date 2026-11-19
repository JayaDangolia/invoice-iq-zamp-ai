import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS = Path("screenshots")
SHOTS.mkdir(exist_ok=True)

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Loading live application at http://localhost:8501 ...")
        page.goto("http://localhost:8501", wait_until="domcontentloaded")
        page.wait_for_timeout(3500)
        
        # Viewport screenshot at 1440x900
        shot_vp = SHOTS / "FINAL_IMAGE7_DASHBOARD_1440x900.png"
        page.screenshot(path=str(shot_vp), full_page=False)
        print(f"Captured viewport screenshot: {shot_vp}")

        # Full page screenshot
        shot_fp = SHOTS / "FINAL_IMAGE7_DASHBOARD_FULLPAGE.png"
        page.screenshot(path=str(shot_fp), full_page=True)
        print(f"Captured fullpage screenshot: {shot_fp}")

        # Sidebar close-up
        sidebar = page.locator("section[data-testid='stSidebar']")
        if sidebar.is_visible():
            sidebar.screenshot(path=str(SHOTS / "FINAL_SIDEBAR_IMAGE6.png"))
            print("Captured sidebar close-up: FINAL_SIDEBAR_IMAGE6.png")

        # KPI cards close-up
        kpi_deck = page.locator(".kpi-deck-grid")
        if kpi_deck.is_visible():
            kpi_deck.screenshot(path=str(SHOTS / "FINAL_KPIS_IMAGE2.png"))
            print("Captured KPI close-up: FINAL_KPIS_IMAGE2.png")

        # Charts close-up
        charts = page.locator(".analytics-dual-grid")
        if charts.is_visible():
            charts.screenshot(path=str(SHOTS / "FINAL_CHARTS_IMAGE4.png"))
            print("Captured charts close-up: FINAL_CHARTS_IMAGE4.png")

        # Activity table close-up
        table = page.locator(".activity-table-card")
        if table.is_visible():
            table.screenshot(path=str(SHOTS / "FINAL_TABLE_IMAGE5.png"))
            print("Captured table close-up: FINAL_TABLE_IMAGE5.png")

        browser.close()
        print("All visual captures complete!")

if __name__ == "__main__":
    capture()
