import time
from playwright.sync_api import sync_playwright

def test_interactive_navigation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="msedge")
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("1. Opening app at http://localhost:8501...")
        page.goto("http://localhost:8501", timeout=30000)
        page.wait_for_selector('[data-testid="stSidebar"]', timeout=15000)
        time.sleep(2)
        
        # Take screenshot of Overview with clickable cards
        page.screenshot(path="tests/test_ov_cards.png")
        print("Captured tests/test_ov_cards.png")

        # 2. Test clicking on KPI Card 3 (Pending Review) on Overview
        print("\n2. Clicking on 'Pending Review' KPI card box...")
        kpi_card_rev = page.locator('div[class*="st-key-kpi_card_ov_pending"] button')
        assert kpi_card_rev.count() > 0, "KPI card pending review overlay button not found!"
        kpi_card_rev.click()
        time.sleep(2)

        # Verify we navigated to Review Queue
        selected_nav = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"]')
        print("Active sidebar page after clicking KPI card:", selected_nav.text_content().strip())
        assert "Review Queue" in selected_nav.text_content().strip()

        # Check for presence of '← Back to Overview' button
        back_btn = page.locator('div[class*="st-key-btn_back_to_ov_"] button')
        print("Back to Overview button found:", back_btn.count() > 0)
        assert back_btn.count() > 0, "Back to Overview button not displayed!"

        # 3. Click '← Back to Overview'
        print("\n3. Clicking '← Back to Overview' button...")
        back_btn.first.click()
        time.sleep(2)
        selected_nav = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"]')
        print("Active sidebar page after clicking Back button:", selected_nav.text_content().strip())
        assert "Overview" in selected_nav.text_content().strip()

        # 4. Navigate to Vendor Network and test clicking KPI cards
        print("\n4. Navigating to Vendor Network...")
        opt_vendor = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"]:has-text("Vendor Network")')
        opt_vendor.click()
        time.sleep(2)

        # Test clicking 'Active & Approved' card
        print("Clicking 'Active & Approved' KPI card box...")
        kpi_vnd_act = page.locator('div[class*="st-key-kpi_card_vendor_act"] button')
        assert kpi_vnd_act.count() > 0, "KPI card vendor active button not found!"
        kpi_vnd_act.click()
        time.sleep(1.5)
        print("Active & Approved filter clicked successfully!")

        # 5. Test clicking the InvoiceIQ main logo in sidebar
        print("\n5. Testing sidebar InvoiceIQ main logo click...")
        logo_btn = page.locator('div[class*="st-key-btn_logo_home"] button')
        assert logo_btn.count() > 0, "Sidebar logo button overlay not found!"
        logo_btn.click()
        time.sleep(2)

        selected_nav = page.locator('[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"]')
        print("Active sidebar page after clicking Main Logo:", selected_nav.text_content().strip())
        assert "Overview" in selected_nav.text_content().strip(), f"Expected 'Overview', got '{selected_nav.text_content()}'"

        print("\nSUCCESS: All KPI card clicks, back navigation, and Main Logo navigation verified 100% working!")
        browser.close()

if __name__ == "__main__":
    test_interactive_navigation()
