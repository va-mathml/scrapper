from database import init_db, is_inmueble_notified, save_inmueble
from notifier import notify_new_inmueble
from ciencuadras_scraper import scrape_ciencuadras
from arriendo_com_scraper import scrape_arriendo_com
from metrocuadrado_scraper import scrape_metrocuadrado
from elpais_scraper import scrape_elpais
from puntopropiedad_scraper import scrape_puntopropiedad
from rentola_scraper import scrape_rentola
import time
import os

def main():
    print("Inicializando base de datos...")
    init_db()
    
    filtros = {
        'precio_min': int(os.getenv('PRECIO_MIN', 700000)),
        'precio_max': int(os.getenv('PRECIO_MAX', 1200000)),
        'barrios_recomendados': [],
        'barrios_excluidos': [
            'Aguablanca', 'Suroriente', 'Ciudad Cordoba', 'Mariano Ramos', 'Manuela Beltran', 
            'Mojica', 'El Vallado', 'El Retiro', 'El Vergel', 'Comuneros', 'Pizamos', 
            'Potrero Grande', 'Decepaz', 'Calimio', 'Llano Verde', 'Marroquin', 'Los Lagos', 
            'El Poblado', 'Diamante', 'Republica de Israel', 'Union de Vivienda', 'Charco Azul', 
            'Alfonso Bonilla Aragon', 'Puerto Mallarino', 'Andres Sanin', 'Siete de Agosto',
            'Siloe', 'Terron Colorado', 'Melendez', 'Ciudad Pacifica'
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

    # ── Fuente 3: MetroCuadrado ──
    print("\n" + "="*50)
    print("[+] Fuente 3: MetroCuadrado")
    print("="*50)
    inmuebles_metrocuadrado = scrape_metrocuadrado(filtros)
    
    # ── Fuente 4: El Pais ──
    print("\n" + "="*50)
    print("[+] Fuente 4: El Pais")
    print("="*50)
    inmuebles_elpais = scrape_elpais(filtros)

    # ── Fuente 5: Punto Propiedad ──
    print("\n" + "="*50)
    print("[+] Fuente 5: Punto Propiedad")
    print("="*50)
    inmuebles_puntopropiedad = scrape_puntopropiedad(filtros)

    # ── Fuente 6: Rentola ──
    print("\n" + "="*50)
    print("[+] Fuente 6: Rentola")
    print("="*50)
    inmuebles_rentola = scrape_rentola(filtros)
    
    # ── Combinar resultados ──
    inmuebles_encontrados = inmuebles_ciencuadras + inmuebles_arriendo + inmuebles_metrocuadrado + inmuebles_elpais + inmuebles_puntopropiedad + inmuebles_rentola
    
    print(f"\n{'='*50}")
    print(f"Total: {len(inmuebles_encontrados)} inmuebles")
    print(f"   CienCuadras: {len(inmuebles_ciencuadras)}")
    print(f"   Arriendo.com: {len(inmuebles_arriendo)}")
    print(f"   MetroCuadrado: {len(inmuebles_metrocuadrado)}")
    print(f"   El Pais: {len(inmuebles_elpais)}")
    print(f"   Punto Propiedad: {len(inmuebles_puntopropiedad)}")
    print(f"   Rentola: {len(inmuebles_rentola)}")
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
