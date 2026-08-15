"""
model_seguridad.py — Modelos POO para la gestión dinámica de
Roles y Permisos en la base de datos `invilara_seguridad`.

Tablas: modulos, roles, roles_permisos.
Patrón: igual que model_gravedad (encapsulamiento + conexión que se abre/cierra por consulta).
Conexión: connectionBD_seguridad() (BD de seguridad).
"""
import re
from conexion.conexionBD import connectionBD_seguridad
from models.base_model import BaseModel


class ModuloModel(BaseModel):
    """Catálogo de módulos del sistema (sidebar)."""

    _RE_NOMBRE = re.compile(r'^[a-z0-9_]{2,40}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.\,\-\#áéíóúÁÉÍÓÚñÑ\/]{0,255}$', re.UNICODE)
    _TIPOS_VALIDOS = {'CRUD', 'Transaccional', 'Enlace'}

    def __init__(self, nombre=None, descripcion=None, url=None,
                 tipo='CRUD', icono=None, orden=0, estado=1, id_modulo=None):
        self.__id_modulo = id_modulo
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__url = url
        self.__tipo = tipo
        self.__icono = icono
        self.__orden = orden
        self.__estado = estado

    # ---- Validaciones ----
    def _validar(self):
        if not self.__nombre or not ModuloModel._RE_NOMBRE.match(self.__nombre):
            raise ValueError("El nombre (clave) del módulo es inválido. Use minúsculas, números y guion bajo (2-40).")
        if not self.__url or not self.__url.strip().startswith('/'):
            raise ValueError("La URL del módulo es obligatoria y debe iniciar con '/'.")
        if self.__tipo not in ModuloModel._TIPOS_VALIDOS:
            raise ValueError("El tipo debe ser CRUD, Transaccional o Enlace.")
        if self.__descripcion and not ModuloModel._RE_TEXTO.match(self.__descripcion):
            raise ValueError("La descripción contiene caracteres no permitidos.")

    # ---- Persistencia ----
    def registrar(self):
        self._validar()
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            sql = """INSERT INTO modulos (nombre, descripcion, url, tipo, icono, orden, estado)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (self.__nombre, self.__descripcion, self.__url,
                                 self.__tipo, self.__icono, self.__orden, self.__estado))
            con.commit()
            return cursor.lastrowid
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def consultar_activos(self):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_modulo, nombre, descripcion, url, tipo, icono, orden, estado "
                "FROM modulos WHERE estado = 1 ORDER BY orden ASC, id_modulo ASC")
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def obtener_por_id(self, id_modulo):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_modulo, nombre, descripcion, url, tipo, icono, orden, estado "
                "FROM modulos WHERE id_modulo = %s", (id_modulo,))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def actualizar(self):
        self._validar()
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            sql = """UPDATE modulos
                     SET nombre = %s, descripcion = %s, url = %s, tipo = %s,
                         icono = %s, orden = %s, estado = %s
                     WHERE id_modulo = %s"""
            cursor.execute(sql, (self.__nombre, self.__descripcion, self.__url,
                                 self.__tipo, self.__icono, self.__orden,
                                 self.__estado, self.__id_modulo))
            con.commit()
            return cursor.rowcount > 0
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def eliminar(self):
        """Borrado lógico (estado = 0)."""
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            cursor.execute("UPDATE modulos SET estado = 0 WHERE id_modulo = %s", (self.__id_modulo,))
            con.commit()
            return cursor.rowcount > 0
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def validar_nombre_existente(self, excluir_id=None):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            if excluir_id:
                cursor.execute(
                    "SELECT 1 FROM modulos WHERE nombre = %s AND id_modulo <> %s AND estado = 1 LIMIT 1",
                    (self.__nombre, excluir_id))
            else:
                cursor.execute(
                    "SELECT 1 FROM modulos WHERE nombre = %s AND estado = 1 LIMIT 1",
                    (self.__nombre,))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if con: con.close()


class RolModel(BaseModel):
    """Catálogo de roles/cargos."""

    _RE_NOMBRE = re.compile(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,20}$')

    def __init__(self, nombre=None, descripcion=None, estado=1, id_rol=None):
        self.__id_rol = id_rol
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__estado = estado

    def _validar(self):
        if not self.__nombre or not RolModel._RE_NOMBRE.match(self.__nombre.strip()):
            raise ValueError("El nombre del rol es inválido (3-20 letras/espacios).")

    def registrar(self):
        self._validar()
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO roles (nombre, descripcion, estado) VALUES (%s, %s, %s)",
                (self.__nombre.strip(), self.__descripcion, self.__estado))
            con.commit()
            return cursor.lastrowid
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def consultar_activos(self):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_rol, nombre, descripcion, estado FROM roles "
                "WHERE estado = 1 ORDER BY id_rol ASC")
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def obtener_por_id(self, id_rol):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_rol, nombre, descripcion, estado FROM roles WHERE id_rol = %s",
                (id_rol,))
            return cursor.fetchone()
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def actualizar(self):
        self._validar()
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE roles SET nombre = %s, descripcion = %s, estado = %s WHERE id_rol = %s",
                (self.__nombre.strip(), self.__descripcion, self.__estado, self.__id_rol))
            con.commit()
            return cursor.rowcount > 0
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def eliminar(self):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            cursor.execute("UPDATE roles SET estado = 0 WHERE id_rol = %s", (self.__id_rol,))
            con.commit()
            return cursor.rowcount > 0
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def validar_nombre_existente(self, excluir_id=None):
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            if excluir_id:
                cursor.execute(
                    "SELECT 1 FROM roles WHERE nombre = %s AND id_rol <> %s AND estado = 1 LIMIT 1",
                    (self.__nombre.strip(), excluir_id))
            else:
                cursor.execute(
                    "SELECT 1 FROM roles WHERE nombre = %s AND estado = 1 LIMIT 1",
                    (self.__nombre.strip(),))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if con: con.close()


class RolPermisoModel(BaseModel):
    """Asignación de permisos (CRUD granulares) de un rol sobre los módulos."""

    def obtener_por_rol(self, id_rol):
        """Retorna lista de {id_modulo, nombre, url, tipo, icono,
        puede_ver, puede_crear, puede_editar, puede_eliminar}."""
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor(dictionary=True)
            sql = """
                SELECT m.id_modulo, m.nombre, m.url, m.tipo, m.icono,
                       COALESCE(rp.puede_ver, 0)      AS puede_ver,
                       COALESCE(rp.puede_crear, 0)    AS puede_crear,
                       COALESCE(rp.puede_editar, 0)   AS puede_editar,
                       COALESCE(rp.puede_eliminar, 0) AS puede_eliminar
                FROM modulos m
                LEFT JOIN roles_permisos rp
                       ON rp.id_modulo = m.id_modulo AND rp.id_rol = %s AND rp.estado = 1
                WHERE m.estado = 1
                ORDER BY m.orden ASC, m.id_modulo ASC
            """
            cursor.execute(sql, (id_rol,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def guardar_permisos(self, id_rol, permisos):
        """
        Reemplaza (borrado lógico + reinserción) los permisos de un rol.
        permisos: lista de dicts {id_modulo, puede_ver, puede_crear,
                                  puede_editar, puede_eliminar}.
        Transacción atómica: se abre, se borra lo previo y se inserta todo.
        """
        con = cursor = None
        try:
            con = connectionBD_seguridad()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE roles_permisos SET estado = 0 WHERE id_rol = %s", (id_rol,))
            for p in permisos:
                cursor.execute(
                    """INSERT INTO roles_permisos
                         (id_rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, 1)""",
                    (id_rol, p.get('id_modulo'),
                     int(bool(p.get('puede_ver'))),
                     int(bool(p.get('puede_crear'))),
                     int(bool(p.get('puede_editar'))),
                     int(bool(p.get('puede_eliminar')))))
            con.commit()
            return True
        except Exception as e:
            if con: con.rollback()
            print(f"[RolPermisoModel.guardar_permisos] Error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if con: con.close()
