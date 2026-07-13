from playwright.sync_api import sync_playwright

def test_fincaraiz():
    url = "https://www.fincaraiz.com.co/arriendo/apartamentos/cali?precioDesde=600000&precioHasta=1100000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        links = page.locator('a').all()
        print(f"Se encontraron {len(links)} links.")
        
        for idx, link in enumerate(links):
            href = link.get_attribute('href')
            text = link.inner_text().strip()
            if text and len(text) > 20: # Only print links that have some descriptive text
                print(f"[{idx}] HREF: {href} | TEXT: {text[:50]}...")
                
        browser.close()

if __name__ == "__main__":
    test_fincaraiz()
