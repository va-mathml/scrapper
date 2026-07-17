import os

scrapers = [
    'ciencuadras_scraper.py',
    'arriendo_com_scraper.py',
    'metrocuadrado_scraper.py',
    'elpais_scraper.py',
    'puntopropiedad_scraper.py',
    'rentola_scraper.py'
]

for filename in scrapers:
    if not os.path.exists(filename):
        continue
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    target = "if omitir:\n                    continue"
    replacement = """if omitir:
                    continue
                    
                # Filtro Estricto Adicional: Piscina, Unidad Residencial y Apartamento
                try:
                    full_text = text_clean if 'text_clean' in locals() or 'text_clean' in globals() else clean_text(card.get_text(separator=' ', strip=True))
                except NameError:
                    try:
                        full_text = text_clean
                    except:
                        try:
                            full_text = clean_text(card.get_text(separator=' ', strip=True))
                        except:
                            try:
                                full_text = clean_text(link.get_text(separator=' ', strip=True))
                            except:
                                full_text = ""
                                
                if 'piscina' not in full_text:
                    continue
                if 'unidad' not in full_text and 'conjunto' not in full_text:
                    continue
                if 'apartamento' not in full_text and 'apto' not in full_text:
                    continue"""
                    
    # Let's do a simpler static replacement
    if filename == 'arriendo_com_scraper.py':
        replacement = """if omitir:
                    continue
                    
                # Filtro Estricto Adicional: Piscina, Unidad Residencial y Apartamento
                full_text = clean_text(card.get_text(separator=' ', strip=True))
                if 'piscina' not in full_text:
                    continue
                if 'unidad' not in full_text and 'conjunto' not in full_text:
                    continue
                if 'apartamento' not in full_text and 'apto' not in full_text:
                    continue"""
    else:
        replacement = """if omitir:
                    continue
                    
                # Filtro Estricto Adicional: Piscina, Unidad Residencial y Apartamento
                if 'piscina' not in text_clean:
                    continue
                if 'unidad' not in text_clean and 'conjunto' not in text_clean:
                    continue
                if 'apartamento' not in text_clean and 'apto' not in text_clean:
                    continue"""

    if target in content and "# Filtro Estricto Adicional" not in content:
        content = content.replace(target, replacement)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {filename}")
    else:
        print(f"Skipped {filename} (target not found or already patched)")
