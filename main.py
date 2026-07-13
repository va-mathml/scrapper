from database import init_db, is_inmueble_notified, save_inmueble
from notifier import notify_new_inmueble
from ciencuadras_scraper import scrape_ciencuadras
from arriendo_com_scraper import scrape_arriendo_com
import time
import os

def main():
    print("Inicializando base de datos...")
    init_db()
    
    # Filtros compartidos por todos los scrapers
    filtros = {
        'precio_min': int(os.getenv('PRECIO_MIN', 600000)),
        'precio_max': int(os.getenv('PRECIO_MAX', 1100000)),
        'barrios_recomendados': [
            'Juanambu', 'Centenario', 'Santa Monica Residencial', 'Santa Monica',
            'Prados del Norte', 'Versalles', 'Normandia', 'El Penon',
            'Aguatal', 'Santa Rita', 'Santa Teresita',
            'San Antonio', 'Cristales', 'Miraflores', 'Bellavista',
            'San Fernando Viejo', 'San Fernando Nuevo', 'San Fernando',
            'Tejares', 'Libertadores', 'Imbanco',
            'Cuarto de Legua', 'El Lido', 'Canaverralejo', 'Canaveralejo',
            'Pampalinda', 'Papalinda', 'Los Alcazares', 'Alcazares',
            'Torres de Comfandi', 'Nueva Tequendama', 'Camino Real',
            'Colseguros', 'Andes', 'San Fernando Sur',
        ],
        'barrios_excluidos': [
            'Aguablanca', 'Suroriente', 'Ciudad Cordoba', 
            'Mariano Ramos', 'Siloe', 'Melendez'
        ]
    }
    
    # ── Fuente 1: CienCuadras ──
    print("\n" + "="*50)
    print("[+] Fuente 1: CienCuadras")
    print("="*50)
    inmuebles_ciencuadras = scrape_ciencuadras(filtros)
    
    # ── Fuente 2: Arriendo.com ──
    print("\n" + "="*50)
    print("[+] Fuente 2: Arriendo.com")
    print("="*50)
    inmuebles_arriendo = scrape_arriendo_com(filtros)
    
    # ── Combinar resultados ──
    inmuebles_encontrados = inmuebles_ciencuadras + inmuebles_arriendo
    
    print(f"\n{'='*50}")
    print(f"Total: {len(inmuebles_encontrados)} inmuebles")
    print(f"   CienCuadras: {len(inmuebles_ciencuadras)}")
    print(f"   Arriendo.com: {len(inmuebles_arriendo)}")
    print(f"{'='*50}")
    
    nuevos = 0
    for inmueble in inmuebles_encontrados:
        if not is_inmueble_notified(inmueble['id']):
            print(f"Nuevo inmueble encontrado: {inmueble['title']} ({inmueble.get('source', '?')})")
            notify_new_inmueble(inmueble)
            save_inmueble(inmueble)
            nuevos += 1
            # Pausa para no saturar a Telegram
            time.sleep(2)
        else:
            print(f"Ignorando inmueble {inmueble['id']} (ya notificado).")
            
    print(f"\nFinalizado. Se notificaron {nuevos} apartamentos nuevos de {len(inmuebles_encontrados)} totales.")

if __name__ == "__main__":
    main()
