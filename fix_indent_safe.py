import os
import glob

scrapers = glob.glob('*_scraper.py')

for filename in scrapers:
    if not os.path.exists(filename):
        continue
        
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the indentation of the apartamento line
    content = content.replace("                                if 'apartamento'", "                if 'apartamento'")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
