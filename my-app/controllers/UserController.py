from flask import render_template, request, flash, redirect, url_for, session, Blueprint
from models.model_usuarios import UsuarioModel
from werkzeug.security import generate_password_hash
from services.bitacora_service import BitacoraService

# Blueprint for user management
user_bp = Blueprint('user_bp', __name__, template_folder='../vista/usuarios')

# instantiate model
user_model = UsuarioModel()

# ============================================
# Sistema de Roles y Permisos
# ============================================
PERMISOS = {
    'Super Usuario': ['usuarios', 'solicitudes', 'empleados', 'empresas', 'maquinaria', 'obras', 'proyectos', 'evidencias', 'publicaciones', 'reportes', 'bitacora', 'contrataciones', 'inspecciones', 'respaldos', 'gravedad', 'prioridad', 'informes', 'manual', 'roles_permisos'],
    'Administrador': ['usuarios', 'solicitudes', 'empleados', 'obras', 'proyectos', 'evidencias', 'publicaciones', 'reportes', 'bitacora', 'gravedad', 'prioridad', 'informes', 'manual', 'roles_permisos'],
    'Gerente': ['solicitudes', 'obras', 'empleados', 'reportes', 'informes', 'gravedad', 'prioridad'],
    'Inspector': ['solicitudes', 'obras', 'inspecciones', 'evidencias', 'informes'],
    'Recepcionista': ['solicitudes', 'reportes', 'informes'],
    'Asistente': ['solicitudes'],
    'Proyectista': ['proyectos', 'obras', 'informes'],
    'Usuario': ['solicitudes', 'informes']
}

def verificar_permiso(modulo):
    """Verifica si el rol del usuario tiene permiso para acceder al módulo."""
    rol_usuario = session.get('rol', 'Usuario')
    return modulo in PERMISOS.get(rol_usuario, [])

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
    
    name_surname = request.form.get('nombre')
    email_user = request.form.get('correo')
    pass_user = request.form.get('pass_user')
    cedula = request.form.get('cedula_usuario')
    rol = request.form.get('rol')
    
    # Validar datos obligatorios
    if not all([name_surname, email_user, cedula, rol]):
        flash('Todos los campos son obligatorios.', 'error')
        return render_template('usuarios/form_user.html')
    
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
        flash('✅ Usuario registrado correctamente.', 'success')
    else:
        flash('❌ Error al registrar el usuario. Verifique los datos.', 'error')
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
        flash('❌ El usuario no existe.', 'error')
        return redirect(url_for('user_bp.list_users'))


@user_bp.route('/users/update', methods=['POST'])
def update_user():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para modificar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))

    user_id = request.form.get('id_user')
    
    # Medida de seguridad: No permitir modificar al Super Usuario
    user_to_update = user_model.buscar_por_id(user_id)
    if user_to_update and user_to_update['rol'] == 'Super Usuario':
        flash('🔒 El Super Usuario no puede ser modificado por razones de seguridad.', 'error')
        return redirect(url_for('user_bp.list_users'))

    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    cedula = request.form.get('cedula_usuario')
    rol = request.form.get('rol')
    new_password = request.form.get('pass_user')

    if user_model.actualizar(user_id, nombre, correo, cedula, rol, new_password if new_password else None):
        BitacoraService.registrar_accion(
            session, 'Usuarios', 'EDITAR',
            f'Actualizó el usuario ID: {user_id}'
        )
        flash('✅ Usuario actualizado correctamente.', 'success')
    else:
        flash('❌ Error al actualizar el usuario.', 'error')
    return redirect(url_for('user_bp.list_users'))


@user_bp.route('/users/delete/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    if not verificar_permiso('usuarios'):
        flash('No tienes permiso para eliminar usuarios.', 'error')
        return redirect(url_for('login_bp.inicio'))
    
    if not request.args.get('confirm'):
        flash('⚠️ ¿Estás seguro? Haz clic en "Eliminar" nuevamente para confirmar.', 'warning')
        return redirect(url_for('user_bp.list_users'))
    
    # Medida de seguridad: No permitir eliminar al Super Usuario
    user_to_delete = user_model.buscar_por_id(user_id)
    if user_to_delete and user_to_delete['rol'] == 'Super Usuario':
        flash('🔒 El Super Usuario no puede ser eliminado por razones de seguridad.', 'error')
        return redirect(url_for('user_bp.list_users'))

    if user_model.eliminar(user_id):
        BitacoraService.registrar_accion(
            session, 'Usuarios', 'ELIMINAR',
            f'Eliminó el usuario ID: {user_id}'
        )
        flash('✅ Usuario eliminado correctamente.', 'success')
    else:
        flash('❌ Error al eliminar el usuario.', 'error')
    return redirect(url_for('user_bp.list_users'))