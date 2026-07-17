# 📓 Scrapper Inmuebles - Journal & Architectural Lessons

Este documento sirve como un registro teórico y arquitectónico de lo que hemos construido. Su objetivo es permitir la reconstrucción mental del sistema desde cero y documentar las lecciones aprendidas al usar desarrollo iterativo asistido por IA.

## 1. La Filosofía del Desarrollo Iterativo (¿Por qué no se previó todo desde el inicio?)

Es natural preguntarse por qué problemas como el *Log Buffering* de Python, los fallos de selectores HTML o la lógica de los filtros no se planearon perfectamente desde el minuto cero. La respuesta radica en la naturaleza de la ingeniería de software y cómo la IA cambia el paradigma:

* **El Mundo Real es Caótico:** No importa qué tan perfecto sea el código inicial, dependemos de factores externos (páginas web que cambian su HTML, Cloudflare bloqueando bots, portales que no ponen el barrio en el título, etc.). 
* **Velocidad vs. Previsión (El efecto IA):** Un humano se tomaría semanas en codificar 6 scrapers distintos; durante ese tiempo, descubriría los errores poco a poco. La IA puede generar la estructura en minutos, lo que hace que choquemos contra la pared de los "casos borde" del mundo real casi inmediatamente. 
* **Desarrollo Empírico:** El código asistido por IA fomenta construir un Prototipo Rápido (MVP), lanzarlo al mundo real, observar cómo falla (ej. *Railway se queda sin memoria* o *Python no escupe los logs*) y ajustar. Es una evolución darwiniana del código.

---

## 2. Arquitectura del Sistema

El proyecto evolucionó de un simple script a un sistema distribuido con 4 capas principales:

### A. Capa de Extracción (Scraping Layer)
* **Tecnología:** Python + Playwright.
* **Lección Aprendida (Playwright vs. Requests):** Los portales inmobiliarios modernos cargan sus datos usando JavaScript (React/Angular). Una petición HTTP simple (Requests/BeautifulSoup) falla porque el HTML viene vacío. Playwright levanta un "Chromium" real que ejecuta el JS, permitiéndonos leer el DOM final.
* **Tolerancia a fallos:** Cada scraper (`scrape_ciencuadras`, `scrape_rentola`, etc.) está aislado en un bloque `try/except`. Si FincaRaíz cambia su diseño y su scraper se rompe, el sistema general no colapsa y los otros 5 portales siguen entregando datos.

### B. Capa de Datos (Database Layer)
* **Tecnología:** Supabase (PostgreSQL).
* **Lección Aprendida (Estado y Anti-Spam):** Al principio, el bot podía enviar el mismo apartamento varias veces si se corría de nuevo. Supabase actúa como nuestra "Memoria a largo plazo". Al guardar el `id` único de cada inmueble, logramos construir una función `is_inmueble_notified()` que garantiza que nunca haya spam, cruzando la información antes de enviarla.

### C. Capa de Notificación (Alerting Layer)
* **Tecnología:** Telegram Bot API.
* **Diseño:** Es un sistema *Push*. En lugar de tener que entrar a buscar, el sistema empuja la información prioritaria directamente al bolsillo del usuario en tiempo real.

### D. Capa de Visualización (Dashboard UI)
* **Tecnología:** Vanilla HTML/CSS/JS desplegado (o accesible de forma estática).
* **Diseño:** Un tablero de control (Control Panel) que consume directamente la API REST de Supabase. Permite ver fotos grandes, descartar inmuebles y acceder a los enlaces originales, separando el ruido (Telegram) del análisis profundo (Dashboard).

---

## 3. Lecciones Técnicas Clave para Recordar

### 3.1. Precision vs. Recall (El dilema del Modo Estricto)
* **Problema:** En la primera versión (Modo Estricto), solo guardábamos apartamentos si el texto decía explícitamente "Juanambú", "Centenario", etc. (Precisión alta).
* **Descubrimiento:** Las inmobiliarias rara vez escriben el barrio correctamente. A veces no lo ponen, a veces dicen "Oeste", a veces se equivocan. 
* **Solución:** Cambiar a un modelo de exclusión (Recall alto). Aceptamos todo *excepto* la lista roja (Aguablanca, Siloé, etc.). Es preferible que el usuario descarte 5 apartamentos feos en el dashboard, a perderse la oportunidad de oro porque la inmobiliaria olvidó escribir el nombre del barrio.

### 3.2. Expresiones Regulares (Regex) en el Mundo Real
* Extraer el precio de un texto "Arriendo: $1.200.000 COP (Incluye admon)" es un infierno lógico.
* **Lección:** Las Regex deben ser defensivas. Aprendimos a buscar patrones de `\d{5,}` (números de más de 5 dígitos) y limpiar caracteres como `$`, `.`, `,` y `COP` en lugar de confiar en una estructura fija de DOM (porque los programadores web cambian las clases CSS constantemente).

### 3.3. Infraestructura en la Nube y DevOps (Railway)
* **Log Buffering de Python:** En un entorno local, el terminal imprime en tiempo real. En un contenedor de Docker en la nube, el sistema operativo hace un "buffer" (guarda los prints en memoria) para ahorrar recursos. Esto nos cegó al debuggear tareas largas. **Solución:** Usar `python -u` (Unbuffered) en el Dockerfile.
* **Asignación de Recursos:** Chromium consume mucha RAM. Al correr 6 scrapers en un cron job, la máquina virtual sufre. El diseño secuencial (uno tras otro cerrando el navegador con `browser.close()`) es la única forma de evitar un colapso de memoria en servidores baratos.

---

## 4. Próximos Pasos & Escalabilidad (A futuro)
Si alguna vez este proyecto debe crecer, estas son las rutas a tomar:
1. **Scraping Asíncrono (`asyncio` + `async_playwright`):** En lugar de hacer 1 portal a la vez (15 minutos), levantar 6 navegadores en paralelo (3 minutos). *Requiere un servidor con 4GB+ de RAM*.
2. **Uso de Proxies:** Si los portales empiezan a bloquear la IP de Railway, se debe implementar una rotación de proxies residenciales en Playwright.
3. **Mapeo Geoespacial (Google Maps API):** En lugar de filtrar por nombres de barrios (que fallan), pedir la latitud/longitud y calcular el radio en kilómetros desde tu oficina o punto de interés.

### 3.4. Falsos Positivos de Seguridad en GitHub (Exposición de Secretos)
* **Incidente:** GitHub envió una alerta de seguridad ("Please resolve these alerts") advirtiendo de una "Google API Key" expuesta en el commit, específicamente en el archivo `debug.html`.
* **Análisis:** El archivo `debug.html` (y otros similares) se usaban para guardar el código HTML descargado de los portales inmobiliarios (como Fincaraiz) durante el desarrollo para analizar la estructura. Estas páginas legítimas contienen *sus propias* llaves de API de Google Maps en su código fuente público. Al nosotros hacer commit de ese archivo HTML a nuestro repositorio, GitHub detectó la llave y disparó una falsa alarma, creyendo que la llave era nuestra y la estábamos filtrando.
* **Solución:** Untrackear (`git rm --cached`) todos los archivos `*.html` de depuración (`debug.html`, `mc.html`, `tarjeta.html`) y agregarlos al `.gitignore` para que las llaves de terceros en el HTML descargado no causen ruido en nuestras alertas de seguridad. Ninguna llave del usuario fue expuesta porque no utilizamos ninguna en este proyecto.

### 2026-07-16: Filtrado Estricto y Ejecución Programada Local

* **Contexto:** Se necesitaba refinar las búsquedas para traer de manera muy estricta únicamente **apartamentos en unidades residenciales o conjuntos, y que incluyeran piscina** en Cali, excluyendo la zona de "Ciudad Pacífica", además de programar una ejecución diferida para la misma noche (8:00 PM).
* **Problema con los Filtros Complejos:** Los scrapers extraen los listados a nivel de tarjeta de pre-visualización. No todos los portales exponen la palabra "piscina" en este nivel inicial de detalle. Si el filtro es demasiado estricto a nivel de texto, se omitirán resultados válidos que solo mencionan las amenidades dentro del enlace de detalle.
* **Implementación:**
  1. Se actualizó `main.py` para inyectar "Ciudad Pacifica" en el set de `barrios_excluidos`.
  2. Se creó e inyectó de forma automatizada mediante un script (`apply_filters.py`) un bloque de filtrado estricto en los 6 scrapers. Este filtro valida la presencia de palabras clave (`'piscina'`, `'unidad' o 'conjunto'`, y `'apartamento' o 'apto'`) en el texto procesado por cada plataforma, descartando todo lo que no concuerde con la solicitud del usuario.
  3. Se diseñó el script `run_at_8.py`, el cual corre como tarea en segundo plano e introduce un `time.sleep()` dinámico calculando la diferencia en segundos entre el tiempo actual y las 20:00 (8:00 PM), ejecutando `main.py` de forma controlada sin perder el historial almacenado en `inmuebles.db`.


### 3.5. El Peligro de los Filtros de Texto Estrictos en Tarjetas de Resumen
* **Problema:** Se intentó filtrar inmuebles exigiendo que la palabra 'piscina' o 'unidad/conjunto' estuviera presente en el texto extraído por los scrapers. Esto resultó en **0 inmuebles encontrados**.
* **Análisis:** Los scrapers operan sobre las 'tarjetas de resumen' o pre-visualizaciones en las páginas de búsqueda, no sobre el detalle completo del inmueble. Las inmobiliarias rara vez incluyen palabras específicas de amenidades (como 'piscina' o 'conjunto') en la descripción corta (ej. 'Hermoso apto al sur, 3 habs, 2 baños'). Exigir estas palabras descarta el 100% de los resultados válidos que solo revelan sus características al dar clic.
* **Solución:** Relajar los filtros. Eliminar requerimientos de palabras clave específicas y depender únicamente del precio, la ubicación (barrios) y el escrutinio visual humano posterior. Un modelo de *alto recall* es preferible en estas etapas iniciales del scraping, dejando la precisión fina al usuario o a scrapers más profundos (y lentos).