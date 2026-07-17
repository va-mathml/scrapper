import os
import glob

scrapers = glob.glob('*_scraper.py')

for filename in scrapers:
    if not os.path.exists(filename):
        continue
        
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # The block currently has something like this (depending on how many times we touched it):
    #                 # Filtro Estricto Adicional: Piscina, Unidad Residencial y Apartamento
    #                 if 'piscina' not in text_clean:
    #                     continue
    #                 if 'apartamento' not in text_clean and 'apto' not in text_clean:
    #                     continue
    
    # We will strip out the whole section completely, and then inject the correct one.
    # To be safe, we split by "# Filtro Estricto Adicional"
    
    if "# Filtro Estricto" in content:
        parts = content.split("# Filtro Estricto Adicional")
        before = parts[0]
        # Find where the filter block ends. Usually it ends where "2. Recomendados" starts.
        # So we look for "# 2. Recomendados" or something else in the second part.
        after_block = parts[1]
        
        if "# 2. Recomendados" in after_block:
            after = "# 2. Recomendados" + after_block.split("# 2. Recomendados")[1]
            
            # Reconstruct the file with the new logic
            # Note: For arriendo_com, it might not have 'text_clean', it has 'full_text' from the older patch
            if filename == 'arriendo_com_scraper.py':
                new_filter = """# Filtro Estricto Adicional
                full_text = clean_text(card.get_text(separator=' ', strip=True)) if 'card' in locals() else ""
                if 'unidad' not in full_text and 'conjunto' not in full_text and 'residencia' not in full_text:
                    continue
                if 'apartamento' not in full_text and 'apto' not in full_text:
                    continue
                    
                """
            else:
                new_filter = """# Filtro Estricto Adicional
                if 'unidad' not in text_clean and 'conjunto' not in text_clean and 'residencia' not in text_clean:
                    continue
                if 'apartamento' not in text_clean and 'apto' not in text_clean:
                    continue
                    
                """
                
            content = before + new_filter + after
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched {filename}")
        else:
            print(f"Skipped {filename}, couldn't find # 2. Recomendados")
