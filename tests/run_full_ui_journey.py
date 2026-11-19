import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_invoices"

def run_ui_journey():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME_PATH, headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 950})

        print("1. Loading Accounts Payable Overview...", flush=True)
        page.goto("http://localhost:8501", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        shot_dash = SCREENSHOTS_DIR / "01_executive_dashboard.png"
        page.screenshot(path=str(shot_dash), full_page=True)
        print(f"   Saved: {shot_dash.name} ({shot_dash.stat().st_size:,} bytes)", flush=True)

        # Navigate to Process Invoice
        print("2. Navigating to 'Process Invoice'...", flush=True)
        page.locator("label:has-text('Process Invoice')").click()
        page.wait_for_timeout(2000)

        # Helper to process a file via file uploader
        def process_invoice(file_name, output_shot_name):
            print(f"   Processing {file_name}...")
            # If an "Upload Another Invoice" button is present, click it first
            another_btn = page.locator("button:has-text('Upload Another Invoice')")
            if another_btn.is_visible():
                another_btn.click()
                page.wait_for_timeout(1500)

            # Upload the file
            pdf_path = SAMPLE_DIR / file_name
            file_input = page.locator("input[type='file']")
            file_input.set_input_files(str(pdf_path))
            page.wait_for_timeout(1500)

            # Click Start processing
            start_btn = page.locator("button:has-text('Start processing')")
            if not start_btn.is_visible():
                start_btn = page.locator("button:has-text('Start Pipeline Processing')")
            start_btn.click()
            page.wait_for_timeout(4500)

            # Capture screenshot of decision report
            shot = SCREENSHOTS_DIR / output_shot_name
            page.screenshot(path=str(shot), full_page=True)
            print(f"   Saved: {shot.name} ({shot.stat().st_size:,} bytes)")

        # [A] Happy Path
        process_invoice("invoice_101_techcorp_happy_path.pdf", "02_happy_path_report.png")

        # [B] Edge Case 1: Original
        process_invoice("invoice_102_greenlogistics_original.pdf", "03_duplicate_original_report.png")

        # [C] Edge Case 1: Duplicate Renamed
        process_invoice("invoice_102_greenlogistics_duplicate_renamed.pdf", "04_duplicate_rejected_report.png")

        # [D] Edge Case 2: Amount Mismatch
        process_invoice("invoice_103_apex_amount_mismatch.pdf", "05_amount_mismatch_report.png")

        # [E] Edge Case 3: Missing Information
        process_invoice("invoice_104_techcorp_missing_po.pdf", "06_missing_po_report.png")

        # [F] Edge Case 4: Scanned OCR
        process_invoice("invoice_105_bharat_scanned.pdf", "07_scanned_ocr_report.png")

        # [G] Unapproved Vendor Rejection
        process_invoice("invoice_107_quantum_unapproved_vendor.pdf", "08_unapproved_vendor_report.png")

        # 3. Navigate to Review Queue
        print("3. Navigating to 'Review Queue'...")
        page.locator("label:has-text('Review Queue')").click()
        page.wait_for_timeout(2500)
        shot_queue = SCREENSHOTS_DIR / "09_human_review_queue.png"
        page.screenshot(path=str(shot_queue), full_page=True)
        print(f"   Saved: {shot_queue.name} ({shot_queue.stat().st_size:,} bytes)")

        # Open the Review Workspace on the first item
        inspect_buttons = page.locator("button:has-text('Inspect')")
        if inspect_buttons.count() == 0:
            inspect_buttons = page.locator("button:has-text('Review')")
        if inspect_buttons.count() > 0:
            print("   Opening item in Review Workspace...")
            inspect_buttons.first.click()
            page.wait_for_timeout(2500)
            
            # Fill notes and approve
            notes_box = page.locator("textarea")
            if notes_box.is_visible():
                notes_box.fill("Verified emergency compute expansion with Engineering Director. Approved under change order.")
                page.wait_for_timeout(500)
                approve_btn = page.locator("button:has-text('Approve Invoice')")
                if not approve_btn.is_visible():
                    approve_btn = page.locator("button:has-text('Manually Approve')")
                approve_btn.click()
                page.wait_for_timeout(3000)

            shot_reviewed = SCREENSHOTS_DIR / "10_review_workspace_approved.png"
            page.screenshot(path=str(shot_reviewed), full_page=True)
            print(f"   Saved: {shot_reviewed.name} ({shot_reviewed.stat().st_size:,} bytes)")

        # 4. Navigate to Processing History
        print("4. Navigating to 'Processing History'...")
        page.locator("label:has-text('Processing History')").click()
        page.wait_for_timeout(2500)
        # Expand first run in history
        expander = page.locator("div[data-testid='stExpander']").first
        if expander.is_visible():
            expander.click()
            page.wait_for_timeout(1000)
        shot_hist = SCREENSHOTS_DIR / "11_processing_history_audit.png"
        page.screenshot(path=str(shot_hist), full_page=True)
        print(f"   Saved: {shot_hist.name} ({shot_hist.stat().st_size:,} bytes)")

        # 5. Navigate to Policy & Master Data
        print("5. Navigating to 'Policy & Master Data'...")
        page.locator("label").filter(has_text="Policy & Master Data").click()
        page.wait_for_timeout(2500)
        shot_policy = SCREENSHOTS_DIR / "12_policy_master_reference.png"
        page.screenshot(path=str(shot_policy), full_page=True)
        print(f"   Saved: {shot_policy.name} ({shot_policy.stat().st_size:,} bytes)")

        # 6. Final Dashboard Refresh
        print("6. Returning to Overview with updated KPIs...")
        page.locator("label:has-text('Overview')").click()
        page.wait_for_timeout(2500)
        shot_dash_final = SCREENSHOTS_DIR / "13_dashboard_updated.png"
        page.screenshot(path=str(shot_dash_final), full_page=True)
        print(f"   Saved: {shot_dash_final.name} ({shot_dash_final.stat().st_size:,} bytes)")

        browser.close()
        print("\nAll UI screenshots captured successfully!")

if __name__ == "__main__":
    run_ui_journey()
