from flask import Flask, session
from flask_mail import Mail
import os

# Claves de seguridad locales (reCAPTCHA + SECRET_KEY de la app)
import claveApi

app = Flask(__name__, template_folder='vista')
application = app

# Clave secreta de la aplicación (protección de sesiones / CSRF).
# Generada y almacenada localmente en claveApi.py (práctica de producción).
app.secret_key = claveApi.SECRET_KEY

# ============================================
# CONFIGURACIÓN DE FLASK-MAIL (Sin usar ninguna CDN como nos pidieron)
# Según las indicaciones del Prof. Escalona
# ============================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# IMPORTANTE MUCHACHOS: Hay que usar variables de entorno o configuración segura
# Para Gmail, necesitas una "Contraseña de aplicación"
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'tu-correo@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'tu-contraseña-de-aplicacion')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'tu-correo@gmail.com')

# Inicializar Flask-Mail
mail = Mail(app)

# Import routers to register routes and blueprints on app startup
from routers.router_login import *
from routers.router_home import *
from routers.router_respaldo import *
from routers.router_page_not_found import *

# Registrar blueprints
app.register_blueprint(login_bp)
app.register_blueprint(respaldo_bp)

# ============================================
# datos del perfil del usuario
# Inyecta el avatar y el nombre en TODAS las plantillas
# ============================================
@app.context_processor
def inject_perfil_usuario():
    from controllers.funciones_login import info_perfil_session
    datos = {
        'perfil_avatar': 'assets/img/avatars/1.png',
        'perfil_nombre': session.get('name_surname', 'Usuario'),
        'perfil_correo': session.get('email_user', '')
    }
    try:
        perfiles = info_perfil_session()
        if perfiles:
            p = perfiles[0]
            datos['perfil_avatar'] = p.get('avatar') or datos['perfil_avatar']
            datos['perfil_nombre'] = p.get('nombre') or datos['perfil_nombre']
            datos['perfil_correo'] = p.get('correo') or datos['perfil_correo']
    except Exception:
        pass
    return dict(perfil=datos)