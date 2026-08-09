import sys
import pkgutil
import importlib.util

def _get_loader(name):
    if name == '__main__':
        mod = sys.modules.get('__main__')
        return getattr(mod, '__loader__', None)
    try:
        spec = importlib.util.find_spec(name)
        return spec.loader if spec else None
    except (ImportError, AttributeError, ValueError):
        return None

pkgutil.get_loader = _get_loader

from flask import Flask, session
from flask_mail import Mail
import os

# Claves de seguridad locales (reCAPTCHA + SECRET_KEY de la app)
import claveApi

app = Flask(__name__, template_folder='vista', instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'))
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
# Notificaciones de cercanía de fecha de culminación (al iniciar la app)
# ============================================
try:
    from services.notificacion_vencimiento_service import notificar_obras_por_vencer
    notificar_obras_por_vencer(dias_ventana=7)
except Exception as e:
    print(f"[app] No se pudieron generar notificaciones de vencimiento: {e}")

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


# ============================================
# Permisos por rol del usuario
# Inyecta en TODAS las plantillas la función tiene_permiso(modulo)
# y el rol/permisos del usuario autenticado (para filtrar el menú lateral)
# ============================================
@app.context_processor
def inject_permisos_usuario():
    from controllers.UserController import verificar_permiso, PERMISOS
    rol = session.get('rol', 'Usuario')
    return {
        'tiene_permiso': verificar_permiso,
        'rol_usuario': rol,
        'permisos_usuario': PERMISOS.get(rol, [])
    }


# ============================================
# Conteo de notificaciones no leídas (badge del campanita)
# ============================================
@app.context_processor
def inject_notificaciones():
    from models.model_notificacion import NotificacionModel
    if 'conectado' in session:
        try:
            uid = session.get('id')
            return {'notificaciones_no_leidas': NotificacionModel().contar_no_leidas(uid)}
        except Exception:
            return {'notificaciones_no_leidas': 0}
    return {'notificaciones_no_leidas': 0}


# ============================================
# Auditoría global: la bitácora registra TODAS las acciones del sistema.
# Se ejecuta en cada petición autenticada que aún no haya sido registrada
# manualmente por el controlador (evita duplicados).
# ============================================
@app.teardown_request
def auditar_todas_acciones(excepcion):
    try:
        from flask import g, request
        from services.bitacora_service import BitacoraService

        # Solo usuarios autenticados
        if 'conectado' not in session:
            return

        # Si el controlador ya registró la acción, no duplicar
        if getattr(g, 'bitacora_logged', False):
            return

        path = request.path or ''
        # Ignorar recursos estáticos, notificaciones y favicon
        if (path.startswith('/static')
                or path.startswith('/notificaciones')
                or path.startswith('/api/obtener-bitacora')
                or path in ('/favicon.ico',)):
            return

        metodo = (request.method or 'GET').upper()
        if metodo in ('HEAD', 'OPTIONS'):
            return

        accion = {
            'GET': 'VER',
            'POST': 'CREAR',
            'PUT': 'EDITAR',
            'PATCH': 'EDITAR',
            'DELETE': 'ELIMINAR'
        }.get(metodo, metodo)

        modulo = BitacoraService.mapear_modulo(request.endpoint, path)
        descripcion = f'{metodo} {path}'

        BitacoraService.registrar_accion(session, modulo, accion, descripcion)
    except Exception as e:
        print(f"[auditar_todas_acciones] Error: {e}")