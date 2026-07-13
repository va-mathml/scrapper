from playwright.sync_api import sync_playwright

def debug():
    url = "https://www.fincaraiz.com.co/arriendo/apartamentos/cali"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(8000)
        
        html = page.content()
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        browser.close()
        
if __name__ == "__main__":
    debug()
