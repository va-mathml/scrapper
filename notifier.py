import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_telegram_message(text):
    if not TOKEN or not CHAT_ID:
        print("Telegram bot no configurado. El mensaje era:", text)
        return
        
    bot = Bot(token=TOKEN)
    try:
        await bot.send_message(
            chat_id=CHAT_ID, 
            text=text, 
            parse_mode='HTML', 
            disable_web_page_preview=True
        )
        print("Mensaje enviado a Telegram.")
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

def notify_new_inmueble(inmueble):
    # Valores por defecto por si faltan llaves en inmuebles antiguos
    tipo = inmueble.get('tipo', 'Inmueble')
    barrio = inmueble.get('barrio', 'Cali').capitalize()
    source = inmueble.get('source', 'CienCuadras')
    
    # Construcción del mensaje minimalista
    mensaje = f"<b>{inmueble['title']}</b>\n"
    if not inmueble['title'].startswith('⭐'):
        mensaje = f"<b>🏢 Tipo:</b> {tipo}\n"
    
    mensaje += f"<b>📍 Barrio:</b> {barrio}\n"
    mensaje += f"<b>💰 Precio:</b> {inmueble['price']}\n"
    mensaje += f"<b>🌐 Portal:</b> {source}\n\n"
    mensaje += f"<a href='{inmueble['url']}'>🔗 Ver Inmueble</a>"
    
    asyncio.run(send_telegram_message(mensaje))
