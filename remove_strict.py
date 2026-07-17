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
        
    # Remove the strict mode block
    strict_blocks = [
        "if not es_recomendado:\n                    continue\n                    \n                ",
        "if not es_recomendado:\n                    continue\n                \n                ",
        "# MODO ESTRICTO: Descartar si no es un barrio recomendado\n                if not es_recomendado:\n                    continue\n                        \n                "
    ]
    
    for block in strict_blocks:
        content = content.replace(block, "")
        
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Removed strict mode from {filename}")
