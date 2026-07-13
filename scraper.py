from playwright.sync_api import sync_playwright
import re
import time

def clean_price(price_str):
    numbers = re.sub(r'[^\d]', '', price_str)
    return int(numbers) if numbers else 0

def clean_text(text):
    return text.lower().strip() if text else ""

def scrape_fincaraiz(url, filtros):
    print(f"Iniciando scraper para {url}...")
    inmuebles = []
    
    with sync_playwright() as p:
        # Ponemos headless=False para que el navegador sea visible y FincaRaiz no nos bloquee creyendo que somos un robot maligno.
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # Evitar bloqueos básicos
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("Página cargada. Esperando resultados...")
            time.sleep(5) # Esperar renderizado de React/Angular
            
            # Buscar contenedores principales de inmuebles de forma dinámica
            cards = page.locator('.listingCard').all()
            print(f"Se encontraron {len(cards)} tarjetas de inmuebles en la página.")
            
            for card in cards:
                if len(inmuebles) >= 20: # Límite para MVP
                    break
                    
                try:
                    # Extraer precio exacto
                    precio_elem = card.locator('.main-price')
                    if precio_elem.count() == 0:
                        continue
                    precio_str = precio_elem.first.inner_text()
                    precio_num = clean_price(precio_str)
                    
                    if precio_num == 0 or precio_num < filtros['precio_min'] or precio_num > filtros['precio_max']:
                        continue
                        
                    # Extraer enlace
                    link_elem = card.locator('a.lc-data')
                    if link_elem.count() == 0:
                        continue
                    href = link_elem.first.get_attribute('href')
                    if not href or href == '#' or href.startswith('javascript'):
                        continue
                        
                    # Extraer título
                    titulo_elem = card.locator('.lc-title')
                    titulo = titulo_elem.first.inner_text() if titulo_elem.count() > 0 else "Apartamento en Arriendo"
                    
                    text_to_check = (href + " " + titulo).lower()
                    
                    # 1. Filtro: Zonas Excluidas
                    omitir = False
                    for excluido in filtros['barrios_excluidos']:
                        if excluido in text_to_check:
                            omitir = True
                            break
                    if omitir:
                        continue
                        
                    # 2. Resaltar Zonas Recomendadas
                    es_recomendado = any(recomendado in text_to_check for recomendado in filtros['barrios_recomendados'])
                    if es_recomendado:
                        titulo = f"⭐ [ZONA RECOMENDADA] {titulo}"
                        
                    # 3. Formatear URL final
                    link = href if href.startswith('http') else 'https://www.fincaraiz.com.co' + href
                        
                    id_inmueble = link.split('-')[-1].split('?')[0] if '-' in link else link.split('/')[-1]
                    
                    # 4. Validar anunciante
                    owner_elem = card.locator('.lc-owner-name')
                    owner_name = owner_elem.first.inner_text().lower() if owner_elem.count() > 0 else ""
                    is_agency = 'inmobiliaria' in owner_name or 'constructora' in owner_name
                    
                    inmuebles.append({
                        'id': f"fr-{id_inmueble}",
                        'title': titulo,
                        'price': precio_str,
                        'url': link,
                        'is_agency': is_agency,
                        'phone': 'Ver link' 
                    })
                except Exception as e:
                    print(f"Error parseando tarjeta: {e}")
                    continue
                
        except Exception as e:
            print(f"Error durante el scraping: {e}")
        finally:
            browser.close()
            
    return inmuebles
