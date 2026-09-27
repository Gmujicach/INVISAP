# ============================================================
# claveApi.py
# Archivo de configuración de seguridad (buena práctica de
# producción: las claves NO se hardcodean en el código fuente
# ni se exponen en el HTML del lado del cliente).
#
# Uso:  import claveApi
#       claveApi.RECAPTCHA_SITE_KEY
#       claveApi.RECAPTCHA_SECRET_KEY
# ============================================================

import os
import secrets


def _cargar_env_local():
	ruta_env = os.path.join(os.path.dirname(__file__), '.env')
	if not os.path.exists(ruta_env):
		return
	with open(ruta_env, 'r', encoding='utf-8') as archivo:
		for linea in archivo:
			linea = linea.strip()
			if not linea or linea.startswith('#') or '=' not in linea:
				continue
			clave, valor = linea.split('=', 1)
			os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


_cargar_env_local()

# ---- Claves de la API de Google reCAPTCHA v2 (checkbox) ----
# Clave del sitio: se usa en el frontend (HTML) para pintar el widget.
RECAPTCHA_SITE_KEY = "6LdbmUktAAAAAFDMm066Jn94Be8B9uWe2kpbDURo"

# Clave secreta: se usa en el servidor para verificar la respuesta.
RECAPTCHA_SECRET_KEY = os.getenv('RECAPTCHA_SECRET_KEY', '')

# Endpoint de verificación de Google (no requiere CDN de terceros)
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# ---- Clave secreta de la aplicación Flask ----
# Cadena aleatoria generada localmente y almacenada de forma segura.
# Protege las sesiones y ayuda contra ataques CSRF / falsificación
# de solicitudes entre sitios. NO compartir ni subir a repositorios.
SECRET_KEY = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)
