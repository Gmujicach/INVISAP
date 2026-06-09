from flask import Blueprint, render_template, request, flash, redirect, url_for, session

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *

login_bp = Blueprint('login_bp', __name__)
PATH_URL_LOGIN = "login"


@login_bp.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@login_bp.route('/mi-perfil', methods=['GET'])
def perfil():
    if 'conectado' in session:
        return render_template(f'perfil/perfil.html', info_perfil_session=info_perfil_session())
    else:
        return redirect(url_for('login_bp.inicio'))


# Crear cuenta de usuario
@login_bp.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
    if 'conectado' in session:
        return redirect(url_for('login_bp.inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html')


# Recuperar cuenta de usuario
@login_bp.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('login_bp.inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@login_bp.route('/saved-register', methods=['POST'])
def cpanelResgisterUserBD():
    if request.method == 'POST' and 'nombre' in request.form and 'pass_user' in request.form:
        nombre = request.form['nombre']
        correo = request.form['correo']
        cedula = request.form['cedula_usuario']
        pass_user = request.form['pass_user']
        rol = 'Usuario' # Rol por defecto para registros externos

        resultData = recibeInsertRegisterUser(
            nombre, correo, pass_user, cedula, rol)
        if (resultData != 0):
            flash('la cuenta fue creada correctamente.', 'success')
            return redirect(url_for('login_bp.inicio'))
        else:
            return redirect(url_for('login_bp.inicio'))
    else:
        flash('el método HTTP es incorrecto', 'error')
        return redirect(url_for('login_bp.inicio'))


# Actualizar datos de mi perfil
@login_bp.route("/actualizar-datos-perfil", methods=['POST'])
def actualizarPerfil():
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form)
            if respuesta == 1:
                flash('Los datos fuerón actualizados correctamente.', 'success')
                return redirect(url_for('login_bp.inicio'))
            elif respuesta == 0:
                flash(
                    'La contraseña actual esta incorrecta, por favor verifique.', 'error')
                return redirect(url_for('login_bp.perfil'))
            elif respuesta == 2:
                flash('Ambas claves deben se igual, por favor verifique.', 'error')
                return redirect(url_for('login_bp.perfil'))
            elif respuesta == 3:
                flash('La Clave actual es obligatoria.', 'error')
                return redirect(url_for('login_bp.perfil'))
        else:
            flash('primero debes iniciar sesión.', 'error')
            return redirect(url_for('login_bp.inicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))


# Validar sesión
@login_bp.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('login_bp.inicio'))
    else:
        if request.method == 'POST' and 'nombre' in request.form and 'pass_user' in request.form:

            nombre_usuario = str(request.form['nombre'])
            pass_user = str(request.form['pass_user'])

            try:
                # Comprobando si existe una cuenta
                conexion_MySQLdb = connectionBD()
                cursor = conexion_MySQLdb.cursor(dictionary=True)
                try:
                    cursor.execute(
                        "SELECT * FROM usuarios WHERE nombre = %s", [nombre_usuario])
                    account = cursor.fetchone()
                finally:
                    cursor.close()
                    conexion_MySQLdb.close()
            except Exception as db_error:
                flash('No se puede conectar con la base de datos. Verifique la configuración del servidor.', 'error')
                print(f"Error de conexión en loginCliente: {db_error}")
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')

            if account:
                if check_password_hash(account['contrasena'], pass_user):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas
                    session['conectado'] = True
                    session['id'] = account['id_usuarios']
                    session['name_surname'] = account['nombre']
                    session['email_user'] = account['correo']

                    flash('Inicio de sesion exitoso :)', 'success')
                    return redirect(url_for('login_bp.inicio'))
                else:
                    # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                    flash('Credenciales incorrectas, por favor verifique usuario y contraseña.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('El usuario no existe, por favor verifique.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('Primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')

@login_bp.route('/recuperar-clave', methods=['POST'])
def recuperarClave():
    correo = request.form.get('email_user')
    if correo:
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT nombre, correo FROM usuarios WHERE correo = %s", [correo])
        user = cursor.fetchone()
        cursor.close()
        conexion.close()

        if user:
            # Aquí iría la lógica para enviar el correo real (SMTP)
            # Por ahora simulamos la validación
            flash(f'Se ha enviado un enlace de recuperación a {correo}.', 'success')
            return redirect(url_for('login_bp.inicio'))
        else:
            flash('El correo no está registrado en el sistema.', 'error')
            return redirect(url_for('login_bp.cpanelRecoveryPassUser'))
    else:
        flash('Por favor ingrese su correo electrónico.', 'error')
        return redirect(url_for('login_bp.cpanelRecoveryPassUser'))

@login_bp.route('/closed-session',  methods=['GET'])
def logout():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email_user', None)
            flash('Tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('login_bp.inicio'))
        else:
            flash('Recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
