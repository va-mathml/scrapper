from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.metrocuadrado.com/apartamento/arriendo/cali/?precio-desde=600000&precio-hasta=1100000")
        page.wait_for_timeout(6000)
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        
        props = []
        for a in links:
            href = a.get('href')
            if href and '/inmueble/' in href:
                props.append(href)
        
        print(f"Total /inmueble/ links: {len(props)}")
        if props:
            print("Examples:")
            for p in props[:3]:
                print(p)
        browser.close()

if __name__ == "__main__":
    main()
