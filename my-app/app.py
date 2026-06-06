from flask import Flask

app = Flask(__name__, template_folder='vista')
application = app
app.secret_key = '97110c78ae51a45af397b6534caef90ebb9b1dcb3380f008f90b23a5d1616bf1bc29098105da20fe'

# Import routers to register routes and blueprints on app startup
from routers.router_login import *
from routers.router_home import *
from routers.router_page_not_found import *

# Registrar blueprint de login si está disponible
try:
	app.register_blueprint(login_bp)
except NameError:
	pass
