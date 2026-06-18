from werkzeug.security import generate_password_hash
from conexion.conexionBD import connectionBD_seguridad

class UsuarioModel:
    def __init__(self, id_usuarios=None, nombre=None, correo=None, contrasena=None, cedula=None, rol='Usuario'):
        self.__id_usuarios = id_usuarios # Privado
        self.__nombre = nombre           # Privado
        self.__correo = correo           # Privado
        self.__contrasena = contrasena   # Privado
        self.__cedula = cedula           # Privado
        self.__rol = rol                 # Privado

    # --- GETTERS Y SETTERS ---
    def get_id(self): return self.__id_usuarios
    def get_nombre(self): return self.__nombre
    def set_nombre(self, val): self.__nombre = val
    def get_correo(self): return self.__correo
    def set_correo(self, val): self.__correo = val
    def get_cedula(self): return self.__cedula
    def set_cedula(self, val): self.__cedula = val
    def get_rol(self): return self.__rol
    def set_rol(self, val): self.__rol = val
    def get_contrasena(self): return self.__contrasena
    def set_contrasena(self, val): self.__contrasena = val

    def buscar_por_nombre(self, nombre):
        conn = connectionBD_seguridad()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM usuarios WHERE nombre = %s"
            cursor.execute(sql, (nombre,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def buscar_por_email(self, email):
        conn = connectionBD_seguridad()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM usuarios WHERE correo = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def validar_duplicados(self, correo, cedula):
        conn = connectionBD_seguridad()
        if not conn: return False
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id_usuarios FROM usuarios WHERE correo = %s OR cedula_usuario = %s"
            cursor.execute(sql, (correo, cedula))
            result = cursor.fetchone()
            return result is not None
        finally:
            cursor.close()
            conn.close()

    def listar_todos(self):
        conn = connectionBD_seguridad()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id_usuarios, nombre, correo, cedula_usuario, rol FROM usuarios"
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def buscar_por_id(self, id_usuario):
        conn = connectionBD_seguridad()
        if not conn: return None
        try:
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id_usuarios, nombre, correo, cedula_usuario, rol FROM usuarios WHERE id_usuarios = %s"
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def incluir(self, data):
        self.set_nombre(data.get('nombre'))
        self.set_correo(data.get('correo'))
        self.set_cedula(data.get('cedula_usuario'))
        self.set_rol(data.get('rol', 'Usuario'))
        pass_user = data.get('pass_user')
        if pass_user:
            self.set_contrasena(generate_password_hash(pass_user))
        return self.__registrar_db()

    def actualizar(self, id_user, name, email, cedula, rol, password=None):
        self.__id_usuarios = id_user
        self.set_nombre(name)
        self.set_correo(email)
        self.set_cedula(cedula)
        self.set_rol(rol)
        self.set_contrasena(generate_password_hash(password) if password else None)
        return self.__actualizar_db()

    # --- MÉTODOS PRIVADOS DE BASE DE DATOS (Seguridad) ---
    def __registrar_db(self):
        conn = connectionBD_seguridad()
        if not conn: return False
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO usuarios (nombre, correo, contrasena, cedula_usuario, rol) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (self.get_nombre(), self.get_correo(), self.get_contrasena(), self.get_cedula(), self.get_rol()))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def __actualizar_db(self):
        conn = connectionBD_seguridad()
        if not conn: return False
        try:
            cursor = conn.cursor()
            if self.__contrasena:
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, cedula_usuario=%s, rol=%s, contrasena=%s WHERE id_usuarios=%s"
                cursor.execute(sql, (self.__nombre, self.__correo, self.__cedula, self.__rol, self.__contrasena, self.__id_usuarios))
            else:
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, cedula_usuario=%s, rol=%s WHERE id_usuarios=%s"
                cursor.execute(sql, (self.__nombre, self.__correo, self.__cedula, self.__rol, self.__id_usuarios))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def __eliminar_fisico_db(self):
        conn = connectionBD_seguridad()
        if not conn: return False
        try:
            cursor = conn.cursor()
            sql = "DELETE FROM usuarios WHERE id_usuarios = %s"
            cursor.execute(sql, (self.get_id(),))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    # --- MÉTODOS PÚBLICOS (Capa de Seguridad Intermedia) ---
    def guardar(self):
        if self.__id_usuarios:
            return self.__actualizar_db()
        return self.__registrar_db()

    def eliminar(self, id_usuario=None):
        if id_usuario:
            self.__id_usuarios = id_usuario
        if self.__id_usuarios:
            return self.__eliminar_fisico_db()
        return False

    @staticmethod
    def existe_y_activo(id_usuario):
        conn = connectionBD_seguridad()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_usuarios FROM usuarios WHERE id_usuarios = %s", (id_usuario,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
