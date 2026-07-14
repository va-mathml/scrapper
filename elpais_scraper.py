import time
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip().lower()

def clean_price(price_str):
    numbers = re.sub(r'[^\d]', '', price_str)
    return int(numbers) if numbers else 0

def scrape_elpais(filtros):
    # Ya incluimos el filtro de la página (apartamentos en alquiler en Cali)
    # Lamentablemente, el filtro de precios de FincaRaiz El Pais podría requerir parámetros complejos o interactuar.
    # Por ahora, extraemos y filtramos en código.
    url = "https://fincaraiz.elpais.com.co/avisos/alquiler/apartamentos"
    
    inmuebles = []
    
    print(f"Iniciando scraper para El Pais: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(6) # Dar tiempo a que el framework renderice
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            articles = soup.find_all('article')
            
            procesados = set()
            for article in articles:
                if len(inmuebles) >= 20:
                    break
                    
                link = article.find('a')
                if not link:
                    continue
                    
                href = link.get('href')
                if not href or '/aviso/' not in href.lower():
                    continue
                    
                final_link = href if href.startswith('http') else 'https://fincaraiz.elpais.com.co' + href
                clean_href = final_link.split('?')[0]
                if clean_href in procesados:
                    continue
                    
                text_content = article.get_text(separator=' ', strip=True)
                if '$' not in text_content:
                    continue
                    
                procesados.add(clean_href)
                
                precio_match = re.search(r'\$\s?[\d\.,]+', text_content)
                if not precio_match:
                    continue
                    
                precio_str = precio_match.group(0)
                precio_num = clean_price(precio_str)
                
                # Descartar lo que rompa el presupuesto
                if precio_num == 0 or precio_num < filtros['precio_min'] or precio_num > filtros['precio_max']:
                    continue
                    
                text_clean = clean_text(text_content)
                href_lower = clean_href.lower()
                
                # 1. Filtro de exclusión
                omitir = False
                for excluido in filtros['barrios_excluidos']:
                    excluido_norm = clean_text(excluido)
                    if excluido_norm in text_clean or excluido_norm.replace(' ', '-') in href_lower:
                        omitir = True
                        break
                if omitir:
                    continue
                    
                # 2. Recomendados
                es_recomendado = False
                barrio_encontrado = ""
                for recomendado in filtros['barrios_recomendados']:
                    recomendado_norm = clean_text(recomendado)
                    if recomendado_norm in text_clean or recomendado_norm.replace(' ', '-') in href_lower:
                        es_recomendado = True
                        barrio_encontrado = recomendado
                        break
                        
                # 3. Título limpio
                titulo = f"Apto en {barrio_encontrado}" if barrio_encontrado else "Apartamento en Arriendo"
                if es_recomendado:
                    titulo = f"⭐ [ZONA RECOMENDADA] {titulo}"
                    
                id_inmueble = clean_href.split('-')[-1]
                
                inmuebles.append({
                    'id': f"elpais-{id_inmueble}",
                    'title': titulo,
                    'price': precio_str,
                    'url': final_link,
                    'source': 'El Pais',
                    'is_agency': 'inmobiliaria' in text_clean or 'constructora' in text_clean,
                    'phone': 'Ver link en El Pais'
                })
                
        except Exception as e:
            print(f"Error scraping El Pais: {e}")
        finally:
            browser.close()
            
    return inmuebles
