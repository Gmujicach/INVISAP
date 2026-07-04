from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from conexion.conexionBD import connectionBD_seguridad
from werkzeug.security import check_password_hash, generate_password_hash
from controllers.funciones_login import *
from controllers.strategies import AuthContext, DatabaseLoginStrategy
from services.bitacora_service import BitacoraService
import re
from controllers.funciones_solicitud import obtener_dashboard_datos

# Importar el servicio de email
from app import mail
from services.email_service import EmailService

login_bp = Blueprint('login_bp', __name__)
PATH_URL_LOGIN = "login"

# Contexto de autenticación inyectado con la estrategia de base de datos
auth_context = AuthContext(DatabaseLoginStrategy())

# Inicializar servicio de email
email_service = EmailService(mail)

# Regex para validación de contraseña (Prof. Escalona)
PASSWORD_REGEX = r'^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$'

@login_bp.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        stats = obtener_dashboard_datos()
        return render_template('home/dashboard.html', 
                               dataLogin=dataLoginSesion(),
                               stats=stats,
                               solicitudes_priorizadas=stats.get('pendientes_priorizadas', []))
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@login_bp.route('/mi-perfil', methods=['GET'])
def perfil():
    if 'conectado' in session:
        return render_template(f'perfil/perfil.html', info_perfil_session=info_perfil_session())
    else:
        return redirect(url_for('login_bp.inicio'))


@login_bp.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
    if 'conectado' in session:
        return redirect(url_for('login_bp.inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html')


@login_bp.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('login_bp.inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


@login_bp.route('/saved-register', methods=['POST'])
def cpanelResgisterUserBD():
    if request.method == 'POST' and 'nombre' in request.form and 'pass_user' in request.form:
        nombre = request.form['nombre']
        correo = request.form['correo']
        cedula = request.form['cedula_usuario']
        pass_user = request.form['pass_user']
        rol = 'Usuario'

        resultData = recibeInsertRegisterUser(nombre, correo, pass_user, cedula, rol)
        if (resultData != 0):
            flash('La cuenta fue creada correctamente.', 'success')
            return redirect(url_for('login_bp.inicio'))
        else:
            return redirect(url_for('login_bp.inicio'))
    else:
        flash('El método HTTP es incorrecto.', 'danger')
        return redirect(url_for('login_bp.inicio'))


@login_bp.route("/actualizar-datos-perfil", methods=['POST'])
def actualizarPerfil():
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form)
            if respuesta == 1:
                flash('Los datos fueron actualizados correctamente.', 'success')
                return redirect(url_for('login_bp.inicio'))
            elif respuesta == 0:
                flash('La contraseña actual es incorrecta. Por favor, verifique.', 'danger')
                return redirect(url_for('login_bp.perfil'))
            elif respuesta == 2:
                flash('Las contraseñas no coinciden. Por favor, verifique.', 'danger')
                return redirect(url_for('login_bp.perfil'))
            elif respuesta == 3:
                flash('La Clave actual es obligatoria.', 'error')
                return redirect(url_for('login_bp.perfil'))
        else:
            flash('Primero debes iniciar sesión.', 'danger')
            return redirect(url_for('login_bp.inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'danger')
        return redirect(url_for('login_bp.inicio'))


@login_bp.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('login_bp.inicio'))
    else:
        if request.method == 'POST' and 'nombre' in request.form and 'pass_user' in request.form:
            nombre_usuario = str(request.form['nombre'])
            pass_user = str(request.form['pass_user'])

            account = auth_context.login(nombre_usuario, pass_user)

            if account:
                session['conectado'] = True
                session['id'] = account['id_usuarios']
                session['name_surname'] = account['nombre']
                session['email_user'] = account['correo']
                session['rol'] = account.get('rol', 'Usuario')
                flash('¡Inicio de sesión exitoso!', 'success')

                BitacoraService.registrar_accion(
                    session=session,
                    accion='LOGIN',
                    modulo='Login',
                    descripcion=f'Usuario {account["nombre"]} inició sesión.'
                )

                return redirect(url_for('login_bp.inicio'))
            else:
                flash('Credenciales incorrectas o usuario inactivo.', 'danger')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('Primero debes iniciar sesión.', 'danger')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


# ============================================
# NUEVAS RUTAS PARA RECUPERACIÓN DE CONTRASEÑA
# ============================================

@login_bp.route('/enviar-otp', methods=['POST'])
def enviarOTP():
    """
    Ruta para enviar el código OTP al correo del usuario
    Validaciones con Regex según Prof. Escalona
    """
    if request.method == 'POST':
        correo = request.form.get('email_user', '').strip()
        
        # Validación de formato de email con Regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, correo):
            flash('El formato del correo electrónico no es válido.', 'error')
            return redirect(url_for('login_bp.cpanelRecoveryPassUser'))
        
        # Verificar que el usuario existe y está activo (Borrado lógico - Prof. Escalona)
        try:
            conexion = connectionBD_seguridad()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT nombre, correo FROM usuarios WHERE correo = %s AND estado = 1", 
                [correo]
            )
            user = cursor.fetchone()
            cursor.close()
            conexion.close()
            
            if user:
                # Enviar OTP
                success, otp_code, message = email_service.send_otp_email(
                    correo, 
                    user['nombre']
                )
                
                if success:
                    # Guardar el correo en sesión temporal para la verificación
                    session['recovery_email'] = correo
                    flash('Se ha enviado un código de verificación a tu correo electrónico.', 'success')
                    return redirect(url_for('login_bp.verificarOTP'))
                else:
                    flash(f'Error al enviar el código: {message}', 'danger')
                    return redirect(url_for('login_bp.cpanelRecoveryPassUser'))
            else:
                # Por seguridad, no revelar si el correo existe o no
                flash('Si el correo está registrado, recibirás un código de verificación.', 'info')
                return redirect(url_for('login_bp.cpanelRecoveryPassUser'))
                
        except Exception as e:
            print(f"Error en enviarOTP: {e}")
            flash('Ocurrió un error al procesar tu solicitud.', 'danger')
            return redirect(url_for('login_bp.cpanelRecoveryPassUser'))
    
    return redirect(url_for('login_bp.cpanelRecoveryPassUser'))


@login_bp.route('/verificar-otp', methods=['GET', 'POST'])
def verificarOTP():
    """
    Ruta para verificar el código OTP ingresado por el usuario
    """
    # Verificar que hay una sesión de recuperación activa
    if 'recovery_email' not in session:
        flash('Sesión de recuperación expirada. Inicia el proceso nuevamente.', 'warning')
        return redirect(url_for('login_bp.cpanelRecoveryPassUser'))
    
    if request.method == 'POST':
        otp_ingresado = request.form.get('otp_code', '').strip()
        correo = session.get('recovery_email')
        
        # Validar formato del OTP (6 dígitos)
        if not re.match(r'^\d{6}$', otp_ingresado):
            flash('El código debe contener exactamente 6 dígitos.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/auth_verify_otp.html')
        
        # Verificar OTP
        valid, message = email_service.verify_otp(correo, otp_ingresado)
        
        if valid:
            # OTP válido - permitir cambio de contraseña
            session['otp_verified'] = True
            flash('Código verificado correctamente. Ahora puedes cambiar tu contraseña.', 'success')
            return redirect(url_for('login_bp.restablecerClave'))
        else:
            flash(message, 'danger')
            return render_template(f'{PATH_URL_LOGIN}/auth_verify_otp.html')
    
    return render_template(f'{PATH_URL_LOGIN}/auth_verify_otp.html')


@login_bp.route('/restablecer-clave', methods=['GET', 'POST'])
def restablecerClave():
    """
    Ruta para restablecer la contraseña después de verificar el OTP
    """
    # Verificar que el OTP fue verificado
    if 'otp_verified' not in session or not session.get('otp_verified'):
        flash('Debes verificar el código OTP primero.', 'warning')
        return redirect(url_for('login_bp.verificarOTP'))
    
    if request.method == 'POST':
        nueva_clave = request.form.get('new_password', '').strip()
        confirmar_clave = request.form.get('confirm_password', '').strip()
        correo = session.get('recovery_email')
        
        # Validaciones según Prof. Escalona
        if not nueva_clave or not confirmar_clave:
            flash('Todos los campos son obligatorios.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/auth_reset_password.html')
        
        if nueva_clave != confirmar_clave:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/auth_reset_password.html')
        
        # Validar formato de contraseña con Regex
        if not re.match(PASSWORD_REGEX, nueva_clave):
            flash('La contraseña debe tener entre 8-12 caracteres, incluir letras y al menos un símbolo especial.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/auth_reset_password.html')
        
        # Actualizar contraseña en la base de datos
        try:
            conexion = connectionBD_seguridad()
            cursor = conexion.cursor()
            
            nueva_password_hash = generate_password_hash(nueva_clave)
            
            sql = """
                UPDATE usuarios 
                SET contrasena = %s,
                    otp_code = NULL,
                    otp_expiry = NULL,
                    otp_attempts = 0
                WHERE correo = %s AND estado = 1
            """
            cursor.execute(sql, (nueva_password_hash, correo))
            conexion.commit()
            
            if cursor.rowcount > 0:
                # Limpiar sesión de recuperación
                session.pop('recovery_email', None)
                session.pop('otp_verified', None)
                
                flash('¡Contraseña restablecida exitosamente! Ya puedes iniciar sesión.', 'success')
                return redirect(url_for('login_bp.inicio'))
            else:
                flash('Error al actualizar la contraseña.', 'danger')
                return render_template(f'{PATH_URL_LOGIN}/auth_reset_password.html')
                
        except Exception as e:
            print(f"Error al restablecer contraseña: {e}")
            flash('Ocurrió un error al actualizar la contraseña.', 'danger')
            return render_template(f'{PATH_URL_LOGIN}/auth_reset_password.html')
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
    
    return render_template(f'{PATH_URL_LOGIN}/auth_reset_password.html')


@login_bp.route('/closed-session', methods=['GET'])
def logout():
    if request.method == 'GET':
        if 'conectado' in session:
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email_user', None)
            session.pop('recovery_email', None)
            session.pop('otp_verified', None)

            BitacoraService.registrar_accion(
                session=session,
                accion='LOGOUT',
                modulo='Login',
                descripcion='Usuario cerró la sesión.'
            )
            flash('Tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('login_bp.inicio'))
        else:
            flash('Recuerde que debe iniciar sesión.', 'danger')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')