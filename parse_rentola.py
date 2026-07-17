from bs4 import BeautifulSoup

def main():
    with open('debug_rentola.html', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try finding property divs or articles
    cards = soup.find_all('div', class_=lambda c: c and 'property' in c.lower())
    if not cards:
        links = soup.find_all('a')
        cards = []
        seen = set()
        for a in links:
            href = a.get('href', '')
            if '/listings/' in href and href not in seen:
                seen.add(href)
                parent = a.parent
                for _ in range(4):
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
        print(f"Found {len(cards)} cards by class")

if __name__ == "__main__":
    main()
