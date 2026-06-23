from flask import Flask
from flask_mail import Mail
import os

app = Flask(__name__, template_folder='vista')
application = app
app.secret_key = '97110c78ae51a45af397b6534caef90ebb9b1dcb3380f008f90b23a5d1616bf1bc29098105da20fe'

# ============================================
# CONFIGURACIÓN DE FLASK-MAIL (Local - Sin CDN)
# Según indicaciones del Prof. Escalona
# ============================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# IMPORTANTE: Usar variables de entorno o configuración segura
# Para Gmail, necesitas una "Contraseña de aplicación"
# https://myaccount.google.com/apppasswords
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'tu-correo@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'tu-contraseña-de-aplicacion')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'tu-correo@gmail.com')

# Inicializar Flask-Mail
mail = Mail(app)

# Import routers to register routes and blueprints on app startup
from routers.router_login import *
from routers.router_home import *
from routers.router_page_not_found import *

# Registrar blueprint de login si está disponible
try:
    app.register_blueprint(login_bp)
except NameError:
    pass