# Usar la imagen oficial de Microsoft Playwright basada en Python (Ubuntu Jammy)
# Esto ya incluye Chromium, WebKit y Firefox a nivel de sistema operativo
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar el archivo de dependencias
COPY requirements.txt .

# Instalar las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# El comando por defecto cuando la máquina encienda será correr el bot
CMD ["python", "main.py"]
