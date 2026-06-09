from flask import render_template, request, flash, redirect, url_for, session, Blueprint
from models.model_usuarios import UsuarioModel

# Blueprint for user management
user_bp = Blueprint('user_bp', __name__, template_folder='../vista/usuarios')

# instantiate model
user_model = UsuarioModel()


@user_bp.route('/users', methods=['GET'])
def list_users():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    users_data = user_model.listar_todos()
    return render_template('usuarios/lista_usuarios.html', resp_usuariosBD=users_data)


@user_bp.route('/users/register', methods=['GET'])
def show_register_form():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))
    return render_template('usuarios/form_user.html')


@user_bp.route('/users/register', methods=['POST'])
def register_user():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    name_surname = request.form.get('nombre')
    email_user = request.form.get('correo')
    pass_user = request.form.get('pass_user')
    cedula = request.form.get('cedula_usuario')
    rol = request.form.get('rol')

    result = user_model.incluir({
        'nombre': name_surname,
        'correo': email_user,
        'pass_user': pass_user,
        'cedula_usuario': cedula,
        'rol': rol
    })

    if result:
        flash('El usuario fue registrado correctamente.', 'success')
        return redirect(url_for('user_bp.list_users'))
    else:
        flash('Error al registrar el usuario. Verifique los datos.', 'error')
        return render_template('usuarios/form_user.html', name_surname=name_surname, email_user=email_user)


@user_bp.route('/users/edit/<int:user_id>', methods=['GET'])
def show_edit_form(user_id):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    user = user_model.buscar_por_id(user_id)
    if user:
        return render_template('usuarios/form_user_update.html', usuario=user)
    else:
        flash('El usuario no existe.', 'error')
        return redirect(url_for('user_bp.list_users'))


@user_bp.route('/users/update', methods=['POST'])
def update_user():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    user_id = request.form.get('id_user')
    
    # Medida de seguridad: No permitir modificar al Super Usuario
    user_to_update = user_model.buscar_por_id(user_id)
    if user_to_update and user_to_update['rol'] == 'Super Usuario':
        flash('El Super Usuario no puede ser modificado por razones de seguridad.', 'error')
        return redirect(url_for('user_bp.list_users'))

    nombre = request.form.get('nombre')
    correo = request.form.get('correo')
    cedula = request.form.get('cedula_usuario')
    rol = request.form.get('rol')
    new_password = request.form.get('pass_user')

    if user_model.actualizar(user_id, nombre, correo, cedula, rol, new_password if new_password else None):
        flash('El usuario fue actualizado correctamente.', 'success')
    else:
        flash('Error al actualizar el usuario.', 'error')
    return redirect(url_for('user_bp.list_users'))


@user_bp.route('/users/delete/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    # Medida de seguridad: No permitir eliminar al Super Usuario
    user_to_delete = user_model.buscar_por_id(user_id)
    if user_to_delete and user_to_delete['rol'] == 'Super Usuario':
        flash('El Super Usuario no puede ser eliminado por razones de seguridad.', 'error')
        return redirect(url_for('user_bp.list_users'))

    if user_model.eliminar(user_id):
        flash('El usuario fue eliminado correctamente.', 'success')
    else:
        flash('Error al eliminar el usuario.', 'error')
    return redirect(url_for('user_bp.list_users'))