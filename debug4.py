from playwright.sync_api import sync_playwright

def test():
    url = "https://www.fincaraiz.com.co/arriendo/apartamentos/cali?precioDesde=600000&precioHasta=1100000"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        # Buscar un link válido de apartamento
        link = page.locator('a[href*="apartamento-en-arriendo-en-"]').first
        
        # Obtener el contenedor padre que parezca una tarjeta (a, div, article)
        html = link.evaluate("node => { let curr = node; while(curr && curr.tagName !== 'BODY') { if(curr.innerText.includes('$')) return curr.outerHTML; curr = curr.parentElement; } return 'nada'; }")
        
        with open("tarjeta.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        browser.close()

if __name__ == "__main__":
    test()
