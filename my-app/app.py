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

from flask import Flask, session, request, redirect, url_for
from flask_mail import Mail
import os

# Claves de seguridad locales (reCAPTCHA + SECRET_KEY de la app)
import claveApi

app = Flask(__name__, template_folder='vista', instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance'))
application = app

# Rutas protegidas incluso cuando el catálogo de módulos todavía no está
# disponible. Los prefijos cubren las vistas y sus endpoints del mismo módulo.
_RUTAS_POR_MODULO = {
    'solicitudes': ('/registrar-solicitud', '/lista-de-solicitudes', '/eliminar-solicitud', '/editar-solicitud', '/detalles-solicitud', '/update-solicitud', '/form-registrar-solicitud', '/api/solicitudes'),
    'gravedad': ('/gestionar-gravedad', '/api/gravedad'),
    'prioridad': ('/gestionar-prioridad', '/prioridad', '/api/prioridad'),
    'proyectos': ('/gestionar-proyectos', '/form-registrar-proyecto', '/editar-proyecto', '/actualizar-proyecto', '/eliminar-proyecto', '/api/proyecto', '/api/obtener-solicitudes'),
    'obras': ('/gestionar-obras', '/form-registrar-obra', '/editar-obra', '/form-editar-obra', '/obra', '/eliminar-obra', '/api/obra'),
    'maquinaria': ('/registrar-maquinaria', '/maquinaria', '/form-registrar-maquinaria', '/editar-maquinaria', '/actualizar-maquinaria', '/eliminar-maquinaria', '/api/maquinaria'),
    'contrataciones': ('/contratacion', '/contrataciones', '/form-contratacion', '/registrar-contratacion', '/procesar-actualizacion', '/eliminar-contratacion', '/api/obtener-empresas-json'),
    'empresas': ('/registrar-empresas', '/lista-empresas', '/edi-empresas', '/form-registrar-empresas', '/update-empresa', '/eliminar-empresa', '/marcar-cumple-requisitos'),
    'empleados': ('/registrar-empleado', '/empleados', '/buscando-empleado', '/editar-empleado'),
    'inspecciones': ('/inspectores', '/inspecciones'),
    'evidencias': ('/evidencias',),
    'informes': ('/inf_avance_obra',),
    'publicaciones': ('/registrar-publicaciones', '/lista-publicaciones', '/editar-publicacion', '/eliminar-publicacion', '/form-registrar-publicacion', '/actualizar-publicacion', '/detalles-publicacion', '/api/publicaciones'),
    'reportes': ('/reportes', '/api/dashboard'),
    'usuarios': ('/users', '/api/users'),
    'roles_permisos': ('/gestionar-permisos', '/api/seguridad'),
    'respaldos': ('/administrar-respaldos', '/respaldos'),
    'bitacora': ('/bitacora',),
    'manual': ('/manual-sistema', '/api/manual-sistema/pdf'),
}


def _modulo_de_ruta(path):
    """Obtiene el módulo por prefijo, priorizando el prefijo más específico."""
    coincidencias = [
        (modulo, prefijo)
        for modulo, prefijos in _RUTAS_POR_MODULO.items()
        for prefijo in prefijos
        if path == prefijo or path.startswith(prefijo.rstrip('/') + '/')
    ]
    return max(coincidencias, key=lambda item: len(item[1]))[0] if coincidencias else None


_MODULO_POR_BLUEPRINT = {
    'user_bp': 'usuarios',
    'empleado_bp': 'empleados',
    'empresa_bp': 'empresas',
    'obra_bp': 'obras',
    'inspeccion_bp': 'inspecciones',
    'evidencia_bp': 'evidencias',
    'informe_avance_bp': 'informes',
    'reporte_excel_bp': 'reportes',
    'reporte_pdf_bp': 'reportes',
    'reporte_estadistico_bp': 'reportes',
    'contrataciones_bp': 'contrataciones',
    'respaldo_bp': 'respaldos',
}


def _modulo_de_peticion(path, endpoint):
    return _modulo_de_ruta(path) or next(
        (modulo for blueprint, modulo in _MODULO_POR_BLUEPRINT.items()
         if endpoint and endpoint.startswith(f'{blueprint}.')),
        None
    )


_ACCIONES_POR_RUTA = {
    'crear': (
        '/form-registrar-', '/registrar-', '/api/solicitudes/crear',
        '/api/gravedad/registrar', '/api/publicaciones/crear', '/api/informes/crear',
        '/api/obra/crear', '/api/maquinaria/crear', '/api/evidencias/crear',
        '/api/crear', '/form-registrar', '/crear'
    ),
    'editar': (
        '/editar-', '/editar', '/editar/', '/edit/', '/actualizar-', '/actualizar/',
        '/update-', '/update/', '/procesar-actualizacion', '/form-editar-',
        '/api/solicitudes/actualizar', '/api/gravedad/actualizar',
        '/api/prioridad/actualizar', '/api/publicaciones/actualizar',
        '/api/informes/actualizar', '/api/evidencias/actualizar',
        '/api/actualizar', '/api/obra/editar', '/api/obra/actualizar'
    ),
    'eliminar': (
        '/eliminar-', '/eliminar', '/eliminar/', '/delete/', '/api/solicitudes/eliminar',
        '/api/gravedad/eliminar', '/api/prioridad/eliminar',
        '/api/publicaciones/eliminar', '/api/informes/eliminar',
        '/api/evidencias/eliminar', '/api/obra/eliminar',
        '/api/eliminar'
    )
}


def _accion_de_ruta(path, method):
    """Determina la acción CRUD de una ruta para reforzar el backend."""
    if path.startswith('/api/maquinaria/') and path.endswith('/eliminar'):
        return 'eliminar'
    if path.startswith('/api/maquinaria/') and path.endswith('/restaurar'):
        return 'editar'
    for accion, prefijos in _ACCIONES_POR_RUTA.items():
        if any(path == prefijo or path.startswith(prefijo) for prefijo in prefijos):
            return accion
    if method in {'POST', 'PUT', 'PATCH', 'DELETE'}:
        return {'POST': 'crear', 'PUT': 'editar', 'PATCH': 'editar', 'DELETE': 'eliminar'}[method]
    return None


@app.before_request
def proteger_modulos_por_url():
    """Impide abrir por URL módulos visibles solo para otros roles."""
    if 'conectado' not in session or request.endpoint == 'static':
        return None
    if request.path.startswith(('/login', '/logout', '/api/login')):
        return None

    modulo_por_ruta = _modulo_de_peticion(request.path, request.endpoint)
    try:
        from models.model_seguridad import ModuloModel
        from controllers.UserController import verificar_permiso, verificar_permiso_accion
        modulos = ModuloModel().consultar_activos()
        if request.path == '/gestionar-permisos' or request.path.startswith('/api/seguridad/'):
            clave = 'roles_permisos'
        else:
            modulo = next((m for m in sorted(modulos, key=lambda item: len(item['url']), reverse=True)
                           if request.path == m['url'] or request.path.startswith(m['url'].rstrip('/') + '/')), None)
            clave = modulo.get('nombre') if modulo else modulo_por_ruta
        if clave and not verificar_permiso(clave):
            if request.path.startswith('/api/'):
                return {'success': False, 'message': 'No tienes permiso para acceder a este módulo.'}, 403
            from flask import flash
            flash('No tienes permiso para acceder a este módulo.', 'error')
            return redirect(url_for('login_bp.inicio'))
        accion = _accion_de_ruta(request.path, request.method)
        if clave and accion and not verificar_permiso_accion(clave, accion):
            if request.path.startswith('/api/') or request.is_json:
                return {'success': False, 'message': f'No tienes permiso para {accion} en este módulo.'}, 403
            from flask import flash
            flash(f'No tienes permiso para {accion} en este módulo.', 'error')
            return redirect(url_for('login_bp.inicio'))
    except Exception:
        # Una ruta conocida no debe quedar abierta si falla la consulta de permisos.
        if modulo_por_ruta:
            if request.path.startswith('/api/'):
                return {'success': False, 'message': 'No se pudo validar el permiso.'}, 503
            from flask import flash
            flash('No se pudo validar el permiso de acceso.', 'error')
            return redirect(url_for('login_bp.inicio'))
    return None

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

try:
    from models.model_seguridad import asegurar_tabla_permisos_usuario
    asegurar_tabla_permisos_usuario()
except Exception as e:
    print(f"[app] No se pudo actualizar el esquema de permisos: {e}")

try:
    from models.model_obra import asegurar_tabla_obra
    asegurar_tabla_obra()
except Exception as e:
    print(f"[app] No se pudo asegurar tabla obra: {e}")

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
        'perfil_correo': session.get('email_user', ''),
        'usuario_logueado_id': session.get('id') or session.get('id_usuarios')
    }
    try:
        perfiles = info_perfil_session()
        if perfiles:
            p = perfiles[0]
            datos['perfil_avatar'] = p.get('avatar') or datos['perfil_avatar']
            datos['perfil_nombre'] = p.get('nombre') or datos['perfil_nombre']
            datos['perfil_correo'] = p.get('correo') or datos['perfil_correo']
            datos['usuario_logueado_id'] = p.get('id_usuarios') or datos['usuario_logueado_id']
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
    from controllers.UserController import verificar_permiso
    from flask import g
    rol = session.get('rol', 'Usuario')
    if not hasattr(g, '_permisos_cache'):
        try:
            from models.model_seguridad import RolPermisoModel
            permisos_db = RolPermisoModel().obtener_nombres_modulos_por_rol(rol)
            g._permisos_cache = set(permisos_db)
        except Exception:
            g._permisos_cache = set()
    return {
        'tiene_permiso': verificar_permiso,
        'rol_usuario': rol,
        'permisos_usuario': list(g._permisos_cache)
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