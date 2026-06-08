from conexion.conexionBD import connectionBD
from werkzeug.security import generate_password_hash


class UsuarioModel:
    def __init__(self):
        pass

    def listar_todos(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = "SELECT id_usuarios, cedula_usuario, nombre, correo, rol FROM usuarios"
            cursor.execute(querySQL)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    def incluir(self, data):
        nombre = data.get('nombre')
        correo = data.get('correo')
        pass_user = data.get('pass_user')
        cedula = data.get('cedula_usuario')
        rol = data.get('rol', 'Usuario')

        if not (nombre and correo and pass_user and cedula):
            return 0

        hashed_pass = generate_password_hash(pass_user)

        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = "INSERT INTO usuarios (nombre, correo, contraseña, cedula_usuario, rol) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (nombre, correo, hashed_pass, cedula, rol))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_usuario):
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = "DELETE FROM usuarios WHERE id_usuarios=%s"
            cursor.execute(sql, (id_usuario,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_usuario):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            sql = "SELECT id_usuarios, nombre, correo, cedula_usuario, rol FROM usuarios WHERE id_usuarios = %s"
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self, id_user, name, email, cedula, rol, password=None):
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            if password:
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, cedula_usuario=%s, rol=%s, contraseña=%s WHERE id_usuarios=%s"
                cursor.execute(sql, (name, email, cedula, rol, generate_password_hash(password), id_user))
            else:
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, cedula_usuario=%s, rol=%s WHERE id_usuarios=%s"
                cursor.execute(sql, (name, email, cedula, rol, id_user))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
