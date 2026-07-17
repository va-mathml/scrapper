import time
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip().lower()

def clean_price(price_str):
    numbers = re.sub(r'[^\d]', '', price_str)
    return int(numbers) if numbers else 0

def scrape_arriendo_com(filtros):
    """
    Scraper para arriendo.com - Apartamentos en arriendo en Cali.
    
    La estructura DOM usa <article class="arx-card"> con:
      - data-url: enlace directo al inmueble
      - arx-card__type: tipo de inmueble
      - arx-card__location: barrio, ciudad
      - es-price: precio
      - arx-card__features / es-listing__meta: habitaciones, baños, m2
    """
    url = "https://arriendo.com/co/apartamentos/cali"
    
    inmuebles = []
    
    print(f"Iniciando scraper para Arriendo.com: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-CO,es;q=0.9',
        })
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(7)  # Dar tiempo a que cargue
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar todas las tarjetas de propiedades
            cards = soup.find_all('article', class_='arx-card')
            print(f"  Arriendo.com: {len(cards)} tarjetas encontradas")
            
            for card in cards:
                if len(inmuebles) >= 25:  # Límite por ejecución
                    break
                
                # 1. Extraer URL del inmueble (atributo data-url)
                data_url = card.get('data-url', '')
                if not data_url:
                    # Buscar enlace alternativo dentro de la tarjeta
                    link_tag = card.find('a', href=True)
                    if link_tag:
                        data_url = link_tag['href']
                    else:
                        continue
                
                if not data_url.startswith('http'):
                    data_url = 'https://arriendo.com' + data_url
                
                # 2. Extraer precio
                price_tag = card.find('span', class_='es-price')
                if not price_tag:
                    continue
                    
                precio_str = price_tag.get_text(strip=True)
                precio_num = clean_price(precio_str)
                
                # Filtrar por precio
                if precio_num == 0 or precio_num < filtros['precio_min'] or precio_num > filtros['precio_max']:
                    continue
                
                # 3. Extraer tipo de inmueble
                type_tag = card.find('div', class_='arx-card__type')
                tipo_text = type_tag.get_text(strip=True) if type_tag else ''
                tipo_clean = clean_text(tipo_text)
                
                # Filtro de tipo: solo apartamentos, casas, apartaestudios
                if 'apartamento' not in tipo_clean and 'casa' not in tipo_clean and 'apartaestudio' not in tipo_clean:
                    continue
                if 'local' in tipo_clean or 'oficina' in tipo_clean or 'bodega' in tipo_clean:
                    continue
                
                # Determinar tipo normalizado
                tipo_inm = "Apartamento"
                if 'casa' in tipo_clean:
                    tipo_inm = "Casa"
                elif 'apartaestudio' in tipo_clean:
                    tipo_inm = "Apartaestudio"
                
                # 4. Extraer ubicación / barrio
                loc_tag = card.find('div', class_='arx-card__location')
                barrio = "No especificado"
                if loc_tag:
                    loc_text = loc_tag.get_text(strip=True)
                    # Formato típico: "Barrio, cali"
                    parts = loc_text.split(',')
                    if parts:
                        barrio = parts[0].strip().title()
                
                # Extraer barrio también de la URL como fallback
                if barrio == "No especificado" and '/cali/' in data_url:
                    url_parts = data_url.split('/cali/')
                    if len(url_parts) > 1:
                        barrio_slug = url_parts[1].split('/')[0]
                        barrio = barrio_slug.replace('-', ' ').title()
                
                # 5. Filtro de barrios excluidos
                text_all = clean_text(f"{tipo_text} {barrio} {data_url}")
                omitir = False
                for excluido in filtros['barrios_excluidos']:
                    excluido_norm = clean_text(excluido)
                    if excluido_norm in text_all or excluido_norm.replace(' ', '-') in data_url.lower():
                        omitir = True
                        break
                if omitir:
                    continue
                    
                # Filtro Estricto Adicional: Piscina, Unidad Residencial y Apartamento
                full_text = clean_text(card.get_text(separator=' ', strip=True))
                if 'piscina' not in full_text:
                    continue
                                if 'apartamento' not in full_text and 'apto' not in full_text:
                    continue
                
                # 6. Verificar si es barrio recomendado
                es_recomendado = False
                for recomendado in filtros['barrios_recomendados']:
                    recomendado_norm = clean_text(recomendado)
                    if recomendado_norm in clean_text(barrio) or recomendado_norm.replace(' ', '-') in data_url.lower():
                        es_recomendado = True
                        barrio = recomendado  # Usar el nombre bonito
                        break
                
                # 7. Generar ID único
                # El data-url tiene formato: .../AR-469068/
                id_match = re.search(r'AR-(\d+)', data_url)
                if id_match:
                    id_inmueble = id_match.group(0)
                else:
                    id_inmueble = data_url.rstrip('/').split('/')[-1]
                
                # 8. Construir título
                titulo = f"{tipo_inm} en {barrio}"
                if es_recomendado:
                    titulo = f"⭐ {titulo}"
                
                inmuebles.append({
                    'id': f"ar-{id_inmueble}",
                    'title': titulo,
                    'price': precio_str,
                    'url': data_url,
                    'tipo': tipo_inm,
                    'barrio': barrio,
                    'source': 'Arriendo.com',
                    'is_agency': True,
                    'phone': 'Ver link'
                })
                
        except Exception as e:
            print(f"Error scraping Arriendo.com: {e}")
        finally:
            browser.close()
    
    print(f"  Arriendo.com: {len(inmuebles)} inmuebles pasaron los filtros")
    return inmuebles
