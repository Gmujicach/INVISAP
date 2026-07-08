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

# ---- Claves de la API de Google reCAPTCHA v2 (checkbox) ----
# Clave del sitio: se usa en el frontend (HTML) para pintar el widget.
RECAPTCHA_SITE_KEY = "6LdbmUktAAAAAFDMm066Jn94Be8B9uWe2kpbDURo"

# Clave secreta: se usa en el servidor para verificar la respuesta.
RECAPTCHA_SECRET_KEY = "6LdbmUktAAAAALzTEslJCQaLp3O0Hl4Kz5okNVgq"

# Endpoint de verificación de Google (no requiere CDN de terceros)
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

# ---- Clave secreta de la aplicación Flask ----
# Cadena aleatoria generada localmente y almacenada de forma segura.
# Protege las sesiones y ayuda contra ataques CSRF / falsificación
# de solicitudes entre sitios. NO compartir ni subir a repositorios.
SECRET_KEY = "b8f4c2a9e7d1f3c6a0b5e2d8c4f7a19b3e6d0c5a8f2b7e1d4c9a6f3b0e5d2c8a1"
