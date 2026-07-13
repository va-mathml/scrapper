from playwright.sync_api import sync_playwright
import re

def test_fincaraiz():
    url = "https://www.fincaraiz.com.co/arriendo/apartamentos/cali?precioDesde=600000&precioHasta=1100000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        # Buscar enlaces que contengan /inmueble/
        links = page.locator('a[href*="/inmueble/"]').all()
        print(f"Se encontraron {len(links)} links de inmuebles.")
        
        for idx, link in enumerate(links[:3]):
            href = link.get_attribute('href')
            print(f"\\n--- LINK {idx}: {href} ---")
            
            # Subir en el DOM hasta encontrar un contenedor con mucho texto
            try:
                card = link.locator("xpath=ancestor::div[string-length(normalize-space(.)) > 50][1]")
                text = card.inner_text()
                print(f"TEXTO TARJETA:\\n{text[:200]}...")
            except Exception as e:
                print("Error obteniendo texto:", e)
                
        browser.close()

if __name__ == "__main__":
    test_fincaraiz()
