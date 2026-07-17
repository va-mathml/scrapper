from bs4 import BeautifulSoup

def main():
    with open('debug_elpais.html', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')
    print(f"Found {len(articles)} articles")
    for article in articles[:3]:
        print("---")
        print("ARTICLE TEXT:", article.text.strip().replace('\n', ' '))
        link = article.find('a')
        if link:
            print("HREF:", link.get('href'))

if __name__ == "__main__":
    main()
