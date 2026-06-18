from abc import ABC, abstractmethod
from werkzeug.security import check_password_hash, generate_password_hash
from conexion.conexionBD import connectionBD_seguridad
from models.model_usuarios import UsuarioModel
import re

# Regex: 8-12 caracteres, al menos una letra y un carácter especial
PASSWORD_REGEX = r"^(?=.*[A-Za-zÁÉÍÓÚáéíóúÑñ])(?=.*[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ]).{8,12}$"

# --- INTERFACES (Contratos Comunes) ---

class LoginStrategy(ABC):
    @abstractmethod
    def autenticar(self, nombre_usuario, password):
        pass

class UserPersistenceStrategy(ABC):
    @abstractmethod
    def registrar(self, usuario: UsuarioModel): pass
    @abstractmethod
    def actualizar(self, usuario: UsuarioModel, nueva_pass=None): pass
    @abstractmethod
    def eliminar(self, user_id): pass
    @abstractmethod
    def obtener_todos(self): pass
    @abstractmethod
    def buscar_por_id(self, user_id): pass

# --- ESTRATEGIAS CONCRETAS PARA LOGIN ---

class DatabaseLoginStrategy(LoginStrategy):
    def autenticar(self, nombre_usuario, password):
        conn = connectionBD_seguridad()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM usuarios WHERE nombre = %s", [nombre_usuario])
            account = cursor.fetchone()
            if account and check_password_hash(account['contrasena'], password):
                return account
            return None
        finally:
            cursor.close()
            conn.close()

# --- ESTRATEGIAS CONCRETAS PARA USUARIOS (MySQL) ---

class MySqlUserStrategy(UserPersistenceStrategy):
    def registrar(self, usuario: UsuarioModel):
        # Invocamos el método público del modelo que protege el método privado de DB
        return usuario.guardar()

    def obtener_todos(self):
        conn = connectionBD_seguridad()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id_usuarios, cedula_usuario, nombre, correo, rol FROM usuarios")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def buscar_por_id(self, user_id):
        conn = connectionBD_seguridad()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM usuarios WHERE id_usuarios = %s", [user_id])
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def actualizar(self, usuario: UsuarioModel, nueva_pass=None):
        conn = connectionBD_seguridad()
        cursor = conn.cursor()
        try:
            if nueva_pass:
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, cedula_usuario=%s, rol=%s, contrasena=%s WHERE id_usuarios=%s"
                cursor.execute(sql, (usuario.get_nombre(), usuario.get_correo(), usuario.get_cedula(), usuario.get_rol(), generate_password_hash(nueva_pass), usuario.get_id()))
            else:
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, cedula_usuario=%s, rol=%s WHERE id_usuarios=%s"
                cursor.execute(sql, (usuario.get_nombre(), usuario.get_correo(), usuario.get_cedula(), usuario.get_rol(), usuario.get_id()))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    def eliminar(self, user_id):
        # Borrado Lógico inyectado en el modelo
        temp_user = UsuarioModel(id_usuarios=user_id)
        return temp_user.eliminar()

# --- CONTEXTOS (Los que deciden en tiempo de ejecución) ---

class AuthContext:
    def __init__(self, strategy: LoginStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: LoginStrategy):
        self._strategy = strategy

    def login(self, user, password):
        return self._strategy.autenticar(user, password)

class UserContext:
    def __init__(self, strategy: UserPersistenceStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: UserPersistenceStrategy):
        self._strategy = strategy

    def list_all(self): return self._strategy.obtener_todos()
    def find(self, uid): return self._strategy.buscar_por_id(uid)
    def create(self, user_obj): return self._strategy.registrar(user_obj)
    def update(self, user_obj, p=None): return self._strategy.actualizar(user_obj, p)
    def remove(self, uid): return self._strategy.eliminar(uid)