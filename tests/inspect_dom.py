from playwright.sync_api import sync_playwright

def inspect():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, channel="msedge")
        page = b.new_page()
        page.goto("http://localhost:8501")
        page.wait_for_selector('[data-testid="stSidebar"]')
        
        # Check classes on btn_logo_home
        logo_btn_el = page.locator('button:has-text("InvoiceIQ Home")')
        if logo_btn_el.count() > 0:
            parent = logo_btn_el.locator('xpath=..')
            parent2 = parent.locator('xpath=..')
            print("button parent:", parent.get_attribute("class"))
            print("button parent2:", parent2.get_attribute("class"))
            print("button parent2 tag and testid:", parent2.evaluate("el => el.tagName + ' ' + el.getAttribute('data-testid')"))

        # Check KPI card overlay button
        kpi_ov = page.locator('div[class*="st-key-kpi_card_ov_"]')
        print("KPI overlay count:", kpi_ov.count())
        if kpi_ov.count() > 0:
            print("KPI overlay class:", kpi_ov.first.get_attribute("class"))
            print("KPI overlay parent:", kpi_ov.first.locator('xpath=..').get_attribute("class"))

        b.close()

if __name__ == "__main__":
    inspect()
