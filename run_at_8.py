import datetime
import time
import subprocess
import sys

def main():
    now = datetime.datetime.now()
    target = now.replace(hour=20, minute=0, second=0, microsecond=0)
    
    if now > target:
        print("Ya pasaron las 8 PM de hoy. Ejecutando inmediatamente...")
        delay = 0
    else:
        delay = (target - now).total_seconds()
        print(f"Esperando {int(delay)} segundos hasta las 8:00 PM...")
        time.sleep(delay)
        
    print("Iniciando main.py...")
    subprocess.run([sys.executable, 'main.py'])

if __name__ == "__main__":
    main()
