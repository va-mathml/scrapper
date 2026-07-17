import os

scrapers = [
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
        
    # We want to find the end of the `es_recomendado` loop and insert the strict mode check.
    # The loop usually ends with `break` inside the `if es_recomendado:` check.
    
    # We can look for the title construction which usually follows the check.
    # Usually: `# 3. Título limpio` or `# 7. Generar ID único` or `# 8. Construir título`
    # A safer way is to just inject after `break` if it's the `for recomendado` loop,
    # but the indentation must be correct.
    # Actually, we can replace:
    # "if es_recomendado:\n                    titulo = f"
    # But wait, we want to skip earlier!
    # Let's just find the loop:
    # for recomendado in filtros['barrios_recomendados']:
    # ...
    # break
    
    # A robust string replacement:
    if "# MODO ESTRICTO" in content:
        continue
        
    if "titulo = f\"Apto en {barrio_encontrado}" in content:
        content = content.replace(
            "titulo = f\"Apto en {barrio_encontrado}",
            "if not es_recomendado:\n                    continue\n                    \n                titulo = f\"Apto en {barrio_encontrado}"
        )
    elif "titulo = f\"{tipo_inm} en {barrio}\"" in content: # arriendo_com
        content = content.replace(
            "titulo = f\"{tipo_inm} en {barrio}\"",
            "if not es_recomendado:\n                    continue\n                \n                titulo = f\"{tipo_inm} en {barrio}\""
        )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Patched {filename}")
