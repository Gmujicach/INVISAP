# Importandopaquetes desde flask
from flask import session, flash

# Importando conexion a BD
from conexion.conexionBD import connectionBD

# Importando conexion a BD invilara
from conexion.conexionBD import connectionBD_invilara
# Para  validar contraseña
from werkzeug.security import check_password_hash

import re
# Para encriptar contraseña generate_password_hash
from werkzeug.security import generate_password_hash


def recibeInsertRegisterUser(nombre, correo, pass_user, cedula, rol='Usuario'):
    respuestaValidar = validarDataRegisterLogin(nombre, correo, pass_user, cedula)

    if (respuestaValidar):
        nueva_password = generate_password_hash(pass_user)
        try:
            conexion_MySQLdb = connectionBD()
            mycursor = conexion_MySQLdb.cursor()
            try:
                sql = "INSERT INTO usuarios (nombre, correo, contraseña, cedula_usuario, rol) VALUES (%s, %s, %s, %s, %s)"
                valores = (nombre, correo, nueva_password, cedula, rol)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_insert = mycursor.rowcount
                return resultado_insert
            finally:
                mycursor.close()
                conexion_MySQLdb.close()
        except Exception as e:
            print(f"Error en el Insert usuarios: {e}")
            return 0
    else:
        return False


# Validando la data del Registros para el login
def validarDataRegisterLogin(nombre, correo, pass_user, cedula):
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = "SELECT * FROM usuarios WHERE correo = %s OR cedula_usuario = %s"
            cursor.execute(querySQL, (correo, cedula))
            userBD = cursor.fetchone()  # Obtener la primera fila de resultados

            if userBD is not None:
                flash('el registro no fue procesado ya existe la cuenta', 'error')
                return False
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', correo):
                flash('el Correo es invalido', 'error')
                return False
            elif not nombre or not correo or not pass_user or not cedula:
                flash('por favor llene los campos del formulario.', 'error')
                return False
            else:
                # La cuenta no existe y los datos del formulario son válidos, puedo realizar el Insert
                return True
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Error en validarDataRegisterLogin : {e}")
        return []


def info_perfil_session():
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = "SELECT nombre, correo FROM usuarios WHERE id_usuarios = %s"
            cursor.execute(querySQL, (session['id'],))
            info_perfil = cursor.fetchall()
            return info_perfil
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Error en info_perfil_session : {e}")
        return []


def procesar_update_perfil(data_form):
    # Extraer datos del diccionario data_form
    id_user = session['id']
    name_surname = data_form['name_surname']
    email_user = data_form['email_user']
    pass_actual = data_form['pass_actual']
    new_pass_user = data_form['new_pass_user']
    repetir_pass_user = data_form['repetir_pass_user']

    if not pass_actual or not email_user:
        return 3

    conexion_MySQLdb = connectionBD()
    cursor = conexion_MySQLdb.cursor(dictionary=True)
    try:
        querySQL = """SELECT * FROM usuarios WHERE correo = %s LIMIT 1"""
        cursor.execute(querySQL, (email_user,))
        account = cursor.fetchone()
        if account:
            if check_password_hash(account['contraseña'], pass_actual):
                # Verificar si new_pass_user y repetir_pass_user están vacías
                if not new_pass_user or not repetir_pass_user:
                    return updatePefilSinPass(id_user, name_surname)
                else:
                    if new_pass_user != repetir_pass_user:
                        return 2
                    else:
                        try:
                            nueva_password = generate_password_hash(new_pass_user)
                            conexion_upd = connectionBD()
                            cursor_upd = conexion_upd.cursor()
                            try:
                                querySQL = """
                                    UPDATE usuarios
                                    SET 
                                        nombre = %s,
                                        contraseña = %s
                                    WHERE id_usuarios = %s
                                """
                                params = (name_surname, nueva_password, id_user)
                                cursor_upd.execute(querySQL, params)
                                conexion_upd.commit()
                                return cursor_upd.rowcount or []
                            finally:
                                cursor_upd.close()
                                conexion_upd.close()
                        except Exception as e:
                            print(f"Ocurrió en procesar_update_perfil: {e}")
                            return []
        else:
            return 0
    finally:
        cursor.close()
        conexion_MySQLdb.close()


def updatePefilSinPass(id_user, name_surname):
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        try:
            querySQL = """
                UPDATE usuarios
                SET 
                    nombre = %s
                WHERE id_usuarios = %s
            """
            params = (name_surname, id_user)
            cursor.execute(querySQL, params)
            conexion_MySQLdb.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Ocurrió un error en la funcion updatePefilSinPass: {e}")
        return []


def dataLoginSesion():
    inforLogin = {
        "id": session['id'],
        "name_surname": session['name_surname'],
        "email_user": session['email_user']
    }
    return inforLogin
