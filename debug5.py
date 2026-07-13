import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def test():
    url = "https://www.metrocuadrado.com/apartamento/arriendo/cali/?precio-desde=600000&precio-hasta=1100000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        page.goto(url, wait_until="domcontentloaded")
        time.sleep(6)
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        
        print(f"Buscando en {url}")
        print(f"Total links: {len(links)}")
        
        for link in links:
            href = link.get('href', '')
            if '/inmueble/' in href.lower():
                print("FOUND:", href)
                print("TEXT:", link.get_text(separator=' ', strip=True)[:100])
                
        browser.close()

if __name__ == "__main__":
    test()
