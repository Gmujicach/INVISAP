from conexion.conexionBD import connectionBD
from werkzeug.security import generate_password_hash


class UsuarioModel:
    def __init__(self):
        pass

    def listar_todos(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = "SELECT id, name_surname, email_user, created_user FROM users"
            cursor.execute(querySQL)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    def incluir(self, data):
        name_surname = data.get('name_surname')
        email_user = data.get('email_user')
        pass_user = data.get('pass_user')

        if not (name_surname and email_user and pass_user):
            return 0

        hashed_pass = generate_password_hash(pass_user)

        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = "INSERT INTO users (name_surname, email_user, pass_user) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name_surname, email_user, hashed_pass))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()

    def eliminar(self, id_usuario):
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = "DELETE FROM users WHERE id=%s"
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
            sql = "SELECT id, name_surname, email_user FROM users WHERE id = %s"
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self, id_user, name, email, password=None):
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            if password:
                sql = "UPDATE users SET name_surname=%s, email_user=%s, pass_user=%s WHERE id=%s"
                cursor.execute(sql, (name, email, generate_password_hash(password), id_user))
            else:
                sql = "UPDATE users SET name_surname=%s, email_user=%s WHERE id=%s"
                cursor.execute(sql, (name, email, id_user))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
