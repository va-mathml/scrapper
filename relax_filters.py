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

    # Reemplazamos la línea estricta de unidad/conjunto por nada, para relajar el filtro
    target_line1 = "if 'unidad' not in text_clean and 'conjunto' not in text_clean:\n                    continue\n"
    target_line2 = "if 'unidad' not in full_text and 'conjunto' not in full_text:\n                    continue\n"
    
    if target_line1 in content:
        content = content.replace(target_line1, "")
        print(f"Relaxed {filename}")
    if target_line2 in content:
        content = content.replace(target_line2, "")
        print(f"Relaxed {filename}")
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

print("Listo, filtros relajados.")
