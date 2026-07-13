import time
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip().lower()

def clean_price(price_str):
    numbers = re.sub(r'[^\d]', '', price_str)
    return int(numbers) if numbers else 0

def scrape_ciencuadras(filtros):
    # La URL ya tiene los filtros de precio incluidos para CienCuadras
    url = f"https://www.ciencuadras.com/arriendo/cali?precioDesde={filtros['precio_min']}&precioHasta={filtros['precio_max']}"
    
    inmuebles = []
    
    print(f"Iniciando scraper para CienCuadras: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(6) # Dar tiempo a que cargue
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscamos todos los enlaces de las propiedades
            links = soup.find_all('a')
            
            procesados = set()
            for link in links:
                if len(inmuebles) >= 20: # Límite MVP
                    break
                    
                href = link.get('href')
                if not href or '/inmueble/' not in href.lower():
                    continue
                    
                final_link = href if href.startswith('http') else 'https://www.ciencuadras.com' + href
                
                # Quitar parámetros de tracking para el procesados y el ID
                clean_href = final_link.split('?')[0]
                if clean_href in procesados:
                    continue
                    
                # Extraemos todo el texto
                text_content = link.get_text(separator=' ', strip=True)
                
                # Si el enlace es solo de imagen (sin $) buscamos el padre
                if '$' not in text_content:
                    parent = link.parent
                    levels = 0
                    while parent and parent.name != 'body' and levels < 5:
                        text_content = parent.get_text(separator=' ', strip=True)
                        if '$' in text_content:
                            break
                        parent = parent.parent
                        levels += 1
                        
                if '$' not in text_content:
                    continue
                    
                procesados.add(clean_href)
                
                precio_match = re.search(r'\$\s?[\d\.,]+', text_content)
                if not precio_match:
                    continue
                    
                precio_str = precio_match.group(0)
                precio_num = clean_price(precio_str)
                
                # Descartar lo que rompa el presupuesto (a veces meten sugeridos más caros)
                if precio_num == 0 or precio_num < filtros['precio_min'] or precio_num > filtros['precio_max']:
                    continue
                    
                text_clean = clean_text(text_content)
                href_lower = clean_href.lower()
                
                # 0. Filtro estricto de Tipo de Inmueble (Solo Aptos, Casas o Apartaestudios)
                if 'apartamento' not in text_clean and 'casa' not in text_clean and 'apartaestudio' not in text_clean:
                    continue
                if 'local' in text_clean or 'oficina' in text_clean or 'bodega' in text_clean:
                    continue
                
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
                barrio_encontrado = "No especificado"
                for recomendado in filtros['barrios_recomendados']:
                    recomendado_norm = clean_text(recomendado)
                    if recomendado_norm in text_clean or recomendado_norm.replace(' ', '-') in href_lower:
                        es_recomendado = True
                        barrio_encontrado = recomendado
                        break
                        
                # Inferir el barrio de la URL si no está en recomendados
                if barrio_encontrado == "No especificado" and '-en-' in clean_href:
                    partes_url = clean_href.split('-en-')[-1].split('-cali')[0]
                    barrio_encontrado = partes_url.replace('-', ' ').title()
                        
                # 3. Tipo de inmueble
                tipo_inm = "Apartamento"
                if 'casa' in text_clean:
                    tipo_inm = "Casa"
                elif 'apartaestudio' in text_clean:
                    tipo_inm = "Apartaestudio"
                
                titulo = f"{tipo_inm} en {barrio_encontrado}"
                if es_recomendado:
                    titulo = f"⭐ {titulo}"
                    
                id_inmueble = clean_href.split('-')[-1] if '-' in clean_href else clean_href.split('/')[-1]
                
                inmuebles.append({
                    'id': f"cc-{id_inmueble}",
                    'title': titulo,
                    'price': precio_str,
                    'url': final_link,
                    'tipo': tipo_inm,
                    'barrio': barrio_encontrado,
                    'source': 'CienCuadras',
                    'is_agency': True,
                    'phone': 'Ver link'
                })
                
        except Exception as e:
            print(f"Error scraping CienCuadras: {e}")
        finally:
            browser.close()
            
    return inmuebles
