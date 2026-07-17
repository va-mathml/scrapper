from bs4 import BeautifulSoup

def main():
    with open('debug_punto.html', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try different tags: div with a specific class or article
    # PuntoPropiedad often uses specific divs for property cards
    cards = soup.find_all('div', attrs={'data-id': True})
    
    if not cards:
        # Fallback to finding links and getting parents
        links = soup.find_all('a')
        cards = []
        seen = set()
        for a in links:
            href = a.get('href', '')
            if '/propiedad/' in href and href not in seen:
                seen.add(href)
                parent = a.parent
                for _ in range(3):
                    if parent and '$' in parent.text:
                        cards.append((href, parent))
                        break
                    parent = parent.parent if parent else None
                    
        print(f"Found {len(cards)} cards by link inference")
        for href, card in cards[:3]:
            print("---")
            print("HREF:", href)
            print("TEXT:", card.text.strip().replace('\n', ' ')[:200])
    else:
        print(f"Found {len(cards)} cards by data-id")
        for card in cards[:3]:
            print("---")
            print("ID:", card.get('data-id'))
            print("TEXT:", card.text.strip().replace('\n', ' ')[:200])
            link = card.find('a')
            if link:
                print("HREF:", link.get('href'))

if __name__ == "__main__":
    main()
