import time
from playwright.sync_api import sync_playwright

def test_buyer_seller_toggle():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
        
        print("1. Navigating to http://localhost:8501 ...")
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        page.wait_for_selector(".dashboard-header-container", timeout=15000)
        time.sleep(1)

        # Confirm default view: Buyer View
        print("2. Verifying initial Buyer View state...")
        headline = page.locator(".headline-main").text_content()
        print(f"   Headline: {headline}")
        assert "Accounts Payable" in headline, f"Expected 'Accounts Payable' in headline, got: {headline}"

        buyer_pill = page.locator(".view-pill-active")
        assert "Buyer View" in buyer_pill.text_content(), f"Expected active pill to be 'Buyer View', got: {buyer_pill.text_content()}"
        print("   Confirmed: Buyer View is active.")

        page.screenshot(path="tests/screenshots/verified_buyer_view.png", full_page=True)
        print("   Saved screenshot: tests/screenshots/verified_buyer_view.png")

        # Click Seller View
        print("3. Clicking 'Seller View' toggle button...")
        seller_btn = page.locator("div[class*='st-key-btn_view_seller'] button")
        seller_btn.click()
        time.sleep(1.5)
        page.wait_for_selector(".dashboard-header-container", timeout=10000)

        # Verify Seller View
        print("4. Verifying Seller View state...")
        headline_seller = page.locator(".headline-main").text_content()
        print(f"   Headline: {headline_seller}")
        assert "Vendor Settlement" in headline_seller, f"Expected 'Vendor Settlement' in headline, got: {headline_seller}"

        seller_pill = page.locator(".view-pill-active")
        print(f"   Active Pill: {seller_pill.text_content()}")
        assert "Seller View" in seller_pill.text_content(), f"Expected active pill to be 'Seller View', got: {seller_pill.text_content()}"

        # Verify Seller View metrics & sections
        page_text = page.locator("body").text_content()
        assert "Total Submissions" in page_text, "Missing 'Total Submissions' in Seller View"
        assert "Payment Cleared" in page_text, "Missing 'Payment Cleared' in Seller View"
        assert "Under AP Review" in page_text, "Missing 'Under AP Review' in Seller View"
        assert "Supplier Invoicing & Settlement Ledger" in page_text, "Missing 'Supplier Invoicing & Settlement Ledger'"
        assert "Settlement Clearance Status" in page_text, "Missing 'Settlement Clearance Status'"
        assert "Active Clarifications" in page_text, "Missing 'Active Clarifications'"
        print("   Confirmed: All Seller View metrics and sections are properly displayed.")

        page.screenshot(path="tests/screenshots/verified_seller_view.png", full_page=True)
        print("   Saved screenshot: tests/screenshots/verified_seller_view.png")

        # Click Buyer View to switch back
        print("5. Clicking 'Buyer View' toggle button to switch back...")
        buyer_btn = page.locator("div[class*='st-key-btn_view_buyer'] button")
        buyer_btn.click()
        time.sleep(1.5)
        page.wait_for_selector(".dashboard-header-container", timeout=10000)

        # Verify switch back
        headline_back = page.locator(".headline-main").text_content()
        print(f"   Headline after switch back: {headline_back}")
        assert "Accounts Payable" in headline_back, f"Expected 'Accounts Payable' in headline, got: {headline_back}"

        buyer_pill_back = page.locator(".view-pill-active")
        assert "Buyer View" in buyer_pill_back.text_content(), f"Expected active pill to be 'Buyer View', got: {buyer_pill_back.text_content()}"
        print("   Confirmed: Successfully returned to Buyer View.")

        page.screenshot(path="tests/screenshots/verified_buyer_view_returned.png", full_page=True)
        print("   Saved screenshot: tests/screenshots/verified_buyer_view_returned.png")

        browser.close()
        print("\nALL BUYER/SELLER VIEW TOGGLE TESTS PASSED PERFECTLY!")

if __name__ == "__main__":
    test_buyer_seller_toggle()
