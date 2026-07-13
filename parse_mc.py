from bs4 import BeautifulSoup

def parse():
    with open("mc.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    
    for idx, link in enumerate(links):
        href = link.get('href')
        if href and ('arriendo' in href or 'inmueble' in href or '-' in href):
            text = link.get_text(strip=True)
            if len(text) > 10:
                print(f"[{idx}] {href} | {text[:100]}")

if __name__ == "__main__":
    parse()
