import sqlite3
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

DB_NAME = 'inmuebles.db'
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error inicializando Supabase: {e}")

def init_db():
    # SQLite local
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inmuebles (
            id TEXT PRIMARY KEY,
            title TEXT,
            price TEXT,
            url TEXT,
            phone TEXT,
            is_agency BOOLEAN,
            notified BOOLEAN DEFAULT 0,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

    # Si hay Supabase, intentamos verificar si la tabla existe o si podemos conectarnos.
    # Asumimos que tú crearás la tabla 'inmuebles' en Supabase a través del panel de Supabase.
    if supabase:
        print("Conectado a Supabase correctamente.")

def is_inmueble_notified(inmueble_id):
    if supabase:
        try:
            response = supabase.table('inmuebles').select('notified').eq('id', inmueble_id).execute()
            if response.data and len(response.data) > 0:
                return True
            return False
        except Exception as e:
            print(f"Error consultando Supabase: {e}")
            
    # Fallback a SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT notified FROM inmuebles WHERE id = ?', (inmueble_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_inmueble(inmueble):
    if supabase:
        try:
            data = {
                'id': inmueble['id'],
                'title': inmueble['title'],
                'price': inmueble['price'],
                'url': inmueble['url'],
                'phone': inmueble.get('phone', ''),
                'is_agency': inmueble.get('is_agency', False),
                'notified': True
            }
            supabase.table('inmuebles').upsert(data).execute()
        except Exception as e:
            print(f"Error guardando en Supabase: {e}")

    # Fallback local siempre
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO inmuebles (id, title, price, url, phone, is_agency, notified)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (
        inmueble['id'],
        inmueble['title'],
        inmueble['price'],
        inmueble['url'],
        inmueble.get('phone', ''),
        inmueble.get('is_agency', False)
    ))
    conn.commit()
    conn.close()
