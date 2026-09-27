from flask import render_template, request, flash, redirect, url_for, session, Blueprint, jsonify, g
from models.model_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash, check_password_hash
from services.bitacora_service import BitacoraService
import re

# Blueprint for user management
user_bp = Blueprint('user_bp', __name__, template_folder='../vista/usuarios')

# instantiate model
user_model = UsuarioModel()
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$')

# ============================================
# Sistema de Roles y Permisos
# ============================================
PERMISOS = {
    'Super Usuario': ['usuarios', 'solicitudes', 'empleados', 'empresas', 'maquinaria', 'obras', 'proyectos', 'evidencias', 'publicaciones', 'reportes', 'bitacora', 'contrataciones', 'inspecciones', 'respaldos', 'gravedad', 'prioridad', 'informes', 'manual', 'roles_permisos'],
    'Administrador': ['usuarios', 'solicitudes', 'empleados', 'empresas', 'maquinaria', 'obras', 'proyectos', 'evidencias', 'publicaciones', 'reportes', 'bitacora', 'contrataciones', 'inspecciones', 'respaldos', 'gravedad', 'prioridad', 'informes', 'manual', 'roles_permisos'],
    'Gerente': ['solicitudes', 'obras', 'empleados', 'reportes', 'informes', 'gravedad', 'prioridad', 'publicaciones'],
    'Inspector': ['solicitudes', 'obras', 'inspecciones', 'evidencias', 'informes'],
    'Recepcionista': ['solicitudes', 'reportes', 'informes'],
    'Asistente': ['solicitudes'],
    'Proyectista': ['proyectos', 'obras', 'informes'],
    'Usuario': ['solicitudes', 'informes'],
    'Presidente': ['solicitudes', 'gravedad', 'prioridad', 'proyectos', 'contrataciones', 'maquinaria', 'empresas', 'obras', 'inspecciones', 'evidencias', 'publicaciones', 'informes', 'reportes', 'empleados', 'bitacora', 'manual']
}

def verificar_permiso(modulo):
    """Verifica si el rol del usuario tiene permiso para acceder al módulo."""
    rol_usuario = session.get('rol', 'Usuario')

    if not hasattr(g, '_permisos_cache'):
        from models.model_seguridad import RolPermisoModel
        try:
            permisos_db = RolPermisoModel().obtener_nombres_modulos_por_rol(rol_usuario)
            g._permisos_cache = set(permisos_db)
        except Exception:
            g._permisos_cache = set()

    if rol_usuario == 'Super Usuario':
        return True
    usuario_id = session.get('id') or session.get('id_usuarios')
    if usuario_id:
        try:
            from models.model_seguridad import RolPermisoModel
            excepciones = RolPermisoModel().obtener_permisos_usuario(usuario_id)
            permiso = next((p for p in excepciones if p.get('nombre') == modulo), None)
            if permiso is not None:
                return bool(permiso.get('puede_ver'))
        except Exception:
            return False
    return modulo in g._permisos_cache


def verificar_permiso_accion(modulo, accion):
    """Verifica Ver/Crear/Editar/Eliminar considerando excepciones individuales."""
    if session.get('rol') == 'Super Usuario':
        return True
    try:
        from models.model_seguridad import RolPermisoModel
        permiso = RolPermisoModel().obtener_permiso(
            session.get('rol', 'Usuario'), session.get('id') or session.get('id_usuarios'), modulo)
        return bool(permiso and permiso.get(f'puede_{accion}'))
    except Exception:
        return False

def requerir_permiso(modulo):
    """Decorador para requerir permiso de módulo."""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'conectado' not in session:
                flash('Primero debes iniciar sesión.', 'error')
                return redirect(url_for('login_bp.inicio'))
            if not verificar_permiso(modulo):
                flash('No tienes permiso para acceder a este módulo.', 'error')
                return redirect(url_for('login_bp.inicio'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@user_bp.route('/users', methods=['GET'])
def list_users():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para gestionar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    users_data = user_model.listar_todos()
    return render_template('usuarios/lista_usuarios.html', resp_usuariosBD=users_data)


@user_bp.route('/users/register', methods=['GET'])
def show_register_form():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para registrar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('usuarios/form_user.html')


@user_bp.route('/users/register', methods=['POST'])
def register_user():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para registrar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso_accion('usuarios', 'crear'):
        flash('No tienes permiso para registrar usuarios.', 'error')
        return redirect(url_for('user_bp.list_users'))
    
    name_surname = request.form.get('nombre')
    email_user = request.form.get('correo')
    pass_user = request.form.get('pass_user')
    cedula = request.form.get('cedula_usuario')
    rol = request.form.get('rol')
    
    # Validar datos obligatorios
    if not all([name_surname, email_user, cedula, rol]):
        flash('Todos los campos son obligatorios.', 'error')
        return render_template('usuarios/form_user.html')
    
    # No permitir registrar Super Usuario
    if rol.strip().lower() == 'super usuario':
        flash('🔒 No está permitido registrar usuarios con el rol Super Usuario.', 'error')
        return render_template('usuarios/form_user.html', nombre=name_surname)
    
    # Validar si ya existe el correo o cédula
    if user_model.validar_duplicados(email_user, cedula):
        flash('Ya existe un usuario con este correo o cédula.', 'error')
        return render_template('usuarios/form_user.html', nombre=name_surname)
    
    result = user_model.incluir({
        'nombre': name_surname,
        'correo': email_user,
        'pass_user': pass_user,
        'cedula_usuario': cedula,
        'rol': rol
    })
    
    if result:
        BitacoraService.registrar_accion(
            session, 'Usuarios', 'CREAR',
            f'Registró el usuario: {email_user}'
        )
        flash('Usuario registrado correctamente.', 'success')
    else:
        flash('Error al registrar el usuario. Verifique los datos.', 'error')
    return redirect(url_for('user_bp.list_users'))


@user_bp.route('/users/edit/<int:user_id>', methods=['GET'])
def show_edit_form(user_id):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para modificar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    user = user_model.buscar_por_id(user_id)
    if user:
        return render_template('usuarios/form_user_update.html', usuario=user)
    else:
        flash('El usuario no existe.', 'error')
        return redirect(url_for('user_bp.list_users'))


@user_bp.route('/api/users/verify-password', methods=['POST', 'OPTIONS'])
def verify_password():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    try:
        data = request.get_json(silent=True) or {}
        password = data.get('password')

        if password is None:
            return jsonify({'success': False, 'message': 'Datos incompletos.'}), 400

        if session.get('rol', '').strip().lower() != 'super usuario':
            return jsonify({'success': False, 'message': 'No tienes permisos para cambiar contraseñas.'}), 403

        try:
            user = user_model.buscar_por_id_con_contrasena(session.get('id'))
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error interno al buscar usuario.'}), 500

        if not user:
            return jsonify({'success': False, 'message': 'Usuario no encontrado.'}), 404

        contrasena_hash = user.get('contrasena')
        if not contrasena_hash:
            return jsonify({'success': False, 'message': 'El usuario no tiene contraseña registrada.'}), 400

        try:
            if check_password_hash(contrasena_hash, password):
                return jsonify({'success': True})
        except Exception:
            pass

        return jsonify({'success': False, 'message': 'Contraseña incorrecta.'}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error inesperado en la verificación.'}), 500


@user_bp.route('/users/update', methods=['POST'])
def update_user():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para modificar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso_accion('usuarios', 'editar'):
        flash('No tienes permiso para modificar usuarios.', 'error')
        return redirect(url_for('user_bp.list_users'))

    user_id = request.form.get('id_user')
    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    cedula = request.form.get('cedula_usuario')
    rol = request.form.get('rol')
    new_password = request.form.get('pass_user')
    current_password = request.form.get('password_actual')

    user_to_update = user_model.buscar_por_id(user_id)
    if user_to_update and user_to_update['rol'] == 'Super Usuario':
        if str(session.get('id')) != str(user_id):
            flash('El Super Usuario no puede ser modificado por razones de seguridad.', 'error')
            return redirect(url_for('user_bp.list_users'))

    if (not user_to_update or user_to_update['rol'] != 'Super Usuario') and rol and rol.strip().lower() == 'super usuario':
        flash('No está permitido asignar el rol Super Usuario a otro usuario.', 'error')
        return redirect(url_for('user_bp.list_users'))

    if user_to_update and user_to_update['rol'] == 'Super Usuario':
        rol = user_to_update['rol']

    if new_password:
        if session.get('rol', '').strip().lower() != 'super usuario':
            flash('No tienes permisos para cambiar contraseñas. Solo el Super Usuario puede realizar esta acción.', 'error')
            return redirect(url_for('user_bp.list_users'))

        if not current_password:
            flash('Debes ingresar la contraseña actual para cambiarla.', 'error')
            return redirect(url_for('user_bp.list_users'))

        logged_user = user_model.buscar_por_id_con_contrasena(session.get('id'))
        current_hash = logged_user.get('contrasena') if logged_user else None
        if not current_hash or not check_password_hash(current_hash, current_password):
            flash('La contraseña actual es incorrecta.', 'error')
            return redirect(url_for('user_bp.list_users'))

        if not PASSWORD_REGEX.fullmatch(new_password):
            flash('La nueva contraseña debe tener de 8 a 12 caracteres, al menos una letra y un símbolo. Ejemplo: Invi2026*', 'error')
            return redirect(url_for('user_bp.list_users'))

    if user_model.actualizar(user_id, nombre, correo, cedula, rol, new_password if new_password else None):
        BitacoraService.registrar_accion(
            session, 'Usuarios', 'EDITAR',
            f'Actualizó el usuario ID: {user_id}'
        )
        if new_password and user_to_update and user_to_update['rol'] == 'Super Usuario':
            flash('La contraseña del Super Usuario se modificó correctamente.', 'success')
        else:
            flash('Usuario actualizado correctamente.', 'success')
    else:
        flash('Error al actualizar el usuario.', 'error')
    return redirect(url_for('user_bp.list_users'))


@user_bp.route('/users/delete/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para eliminar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso_accion('usuarios', 'eliminar'):
        flash('No tienes permiso para eliminar usuarios.', 'error')
        return redirect(url_for('user_bp.list_users'))
    
    if not request.args.get('confirm'):
        flash('¿Estás seguro? Haz clic en "Eliminar" nuevamente para confirmar.', 'warning')
        return redirect(url_for('user_bp.list_users'))
    
    # Medida de seguridad: No permitir eliminar al Super Usuario
    user_to_delete = user_model.buscar_por_id(user_id)
    if user_to_delete and user_to_delete['rol'] == 'Super Usuario':
        flash('El Super Usuario no puede ser eliminado por razones de seguridad.', 'error')
        return redirect(url_for('user_bp.list_users'))

    if user_model.eliminar(user_id):
        BitacoraService.registrar_accion(
            session, 'Usuarios', 'ELIMINAR',
            f'Eliminó el usuario ID: {user_id}'
        )
        flash('Usuario eliminado correctamente.', 'success')
    else:
        flash('Error al eliminar el usuario.', 'error')
    return redirect(url_for('user_bp.list_users'))


# ============================================
# API AJAX — Módulo de Usuarios
# Evita la recarga completa de la página al
# eliminar, ver o filtrar usuarios.
# ============================================

@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
def api_detalle_usuario(user_id):
    """Devuelve el detalle de un usuario en JSON para el modal de verificación."""
    if 'conectado' not in session:
        return jsonify({'ok': False, 'mensaje': 'Sesión expirada. Inicie sesión nuevamente.'}), 401
    if not verificar_permiso('usuarios'):
        return jsonify({'ok': False, 'mensaje': 'No tiene permiso para consultar usuarios.'}), 403

    usuario = user_model.buscar_por_id(user_id)
    if not usuario:
        return jsonify({'ok': False, 'mensaje': 'El usuario no existe.'}), 404

    try:
        from models.model_seguridad import RolPermisoModel
        modulos = RolPermisoModel().obtener_nombres_modulos_por_rol(usuario.get('rol', 'Usuario'))
    except Exception:
        modulos = []

    datos = dict(usuario)
    datos['modulos_asignados'] = sorted(modulos)
    return jsonify({'ok': True, 'usuario': datos})


@user_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def api_eliminar_usuario(user_id):
    """Elimina un usuario por AJAX y registra la acción en la bitácora."""
    if 'conectado' not in session:
        return jsonify({'ok': False, 'mensaje': 'Sesión expirada. Inicie sesión nuevamente.'}), 401
    if not verificar_permiso('usuarios'):
        return jsonify({'ok': False, 'mensaje': 'No tiene permiso para eliminar usuarios.'}), 403
    if not verificar_permiso_accion('usuarios', 'eliminar'):
        return jsonify({'ok': False, 'mensaje': 'No tiene permiso para eliminar usuarios.'}), 403

    usuario_a_eliminar = user_model.buscar_por_id(user_id)
    if not usuario_a_eliminar:
        return jsonify({'ok': False, 'mensaje': 'El usuario no existe.'}), 404
    if usuario_a_eliminar['rol'] == 'Super Usuario':
        return jsonify({
            'ok': False,
            'mensaje': 'El Super Usuario no puede ser eliminado por razones de seguridad.'
        }), 403

    if user_model.eliminar(user_id):
        BitacoraService.registrar_accion(
            session, 'Usuarios', 'ELIMINAR',
            f'Eliminó el usuario ID: {user_id}'
        )
        return jsonify({'ok': True, 'mensaje': 'Usuario eliminado correctamente.'})

    return jsonify({'ok': False, 'mensaje': 'Error al eliminar el usuario.'}), 500