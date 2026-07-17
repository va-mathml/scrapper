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

    # The block we injected:
    #                 # Filtro Estricto Adicional: Piscina, Unidad Residencial y Apartamento
    #                 if 'piscina' not in text_clean:
    #                     continue
    #                 if 'unidad' not in text_clean and 'conjunto' not in text_clean:
    #                     continue
    #                 if 'apartamento' not in text_clean and 'apto' not in text_clean:
    #                     continue

    # We want to remove the 'unidad' lines
    content = content.replace("                if 'unidad' not in text_clean and 'conjunto' not in text_clean:\n                    continue\n", "")
    content = content.replace("                if 'unidad' not in full_text and 'conjunto' not in full_text:\n                    continue\n", "")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
