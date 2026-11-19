from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8501", wait_until="networkidle")
    
    # Check if custom style tag exists
    style_tags = page.locator("style").all_inner_texts()
    custom_found = any("--color-navy" in s for s in style_tags)
    print("Has --color-navy in style tags:", custom_found)
    
    # Find what rule sets sidebar background
    rules = page.evaluate("""() => {
        const el = document.querySelector('section[data-testid="stSidebar"]');
        return el ? el.className : 'NOT FOUND';
    }""")
    print("sidebar className:", rules)
    
    # Check CSS rules applied to sidebar
    matched = page.evaluate("""() => {
        const el = document.querySelector('section[data-testid="stSidebar"]');
        const sheets = Array.from(document.styleSheets);
        const results = [];
        for (const sheet of sheets) {
            try {
                for (const rule of sheet.cssRules) {
                    if (rule.selectorText && rule.selectorText.includes('stSidebar')) {
                        results.push(rule.selectorText + ' -> ' + rule.style.cssText);
                    }
                }
            } catch(e) {}
        }
        return results;
    }""")
    for m in matched[:10]:
        print("Rule:", m)
    browser.close()
