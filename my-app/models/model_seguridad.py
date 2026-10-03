"""
model_seguridad.py — Modelos POO para la gestión dinámica de
Roles y Permisos en la base de datos `invilara_seguridad`.

Tablas: modulos, roles, roles_permisos.
Patrón: igual que model_gravedad (encapsulamiento + conexión que se abre/cierra por consulta).
Conexión: BaseConexionBD.obtener_conexion_seguridad() (BD de seguridad).
"""
import re
from conexion.base_conexion import BaseConexionBD
from models.base_model import BaseModel


def asegurar_tabla_permisos_usuario():
    """Crea la tabla de excepciones al actualizar una instalación existente."""
    con = cursor = None
    try:
        con = BaseConexionBD.obtener_conexion_seguridad()
        cursor = con.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios_permisos (
            id_usuario_permiso INT NOT NULL AUTO_INCREMENT,
            id_usuario INT NOT NULL,
            id_modulo INT NOT NULL,
            puede_ver TINYINT(1) NOT NULL DEFAULT 0,
            puede_crear TINYINT(1) NOT NULL DEFAULT 0,
            puede_editar TINYINT(1) NOT NULL DEFAULT 0,
            puede_eliminar TINYINT(1) NOT NULL DEFAULT 0,
            estado TINYINT(1) NOT NULL DEFAULT 1,
            PRIMARY KEY (id_usuario_permiso),
            UNIQUE KEY uk_usuario_modulo (id_usuario, id_modulo),
            CONSTRAINT fk_usuarios_permisos_modulo FOREIGN KEY (id_modulo)
              REFERENCES modulos (id_modulo) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cursor.execute("""INSERT INTO modulos
            (nombre, descripcion, url, tipo, icono, orden, estado)
            SELECT 'roles_permisos', 'Administración de roles, módulos y permisos.',
                   '/gestionar-permisos', 'CRUD', 'bi-shield-lock-fill', 19, 1
            WHERE NOT EXISTS (SELECT 1 FROM modulos WHERE nombre = 'roles_permisos')""")
        cursor.execute("""INSERT IGNORE INTO roles_permisos
            (id_rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar, estado)
            SELECT r.id_rol, m.id_modulo, 1, 1, 1, 1, 1
            FROM roles r CROSS JOIN modulos m
            WHERE r.nombre IN ('Super Usuario', 'Administrador')
              AND m.nombre = 'roles_permisos'""")
        con.commit()
    except Exception as e:
        print(f"[seguridad] No se pudo asegurar usuarios_permisos: {e}")
    finally:
        if cursor: cursor.close()
        if con: con.close()


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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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
            con = self.obtener_conexion_seguridad()
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

    def existe_super_usuario_activo(self, excluir_id=None):
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor(dictionary=True)
            if excluir_id:
                cursor.execute(
                    "SELECT id_rol FROM roles WHERE nombre = %s AND estado = 1 AND id_rol <> %s LIMIT 1",
                    ("Super Usuario", excluir_id))
            else:
                cursor.execute(
                    "SELECT id_rol FROM roles WHERE nombre = %s AND estado = 1 LIMIT 1",
                    ("Super Usuario",))
            return cursor.fetchone() is not None
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def obtener_super_usuario_id(self):
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_rol FROM roles WHERE nombre = %s AND estado = 1 LIMIT 1",
                ("Super Usuario",))
            row = cursor.fetchone()
            return row['id_rol'] if row else None
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def obtener_usuarios_por_rol(self):
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor(dictionary=True)
            sql = """
                SELECT id_usuarios, nombre, correo, cedula_usuario, rol, avatar, estado
                FROM usuarios
                WHERE rol = %s AND estado = 1
                ORDER BY nombre ASC
            """
            cursor.execute(sql, (self.__nombre.strip(),))
            return cursor.fetchall()
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
            con = self.obtener_conexion_seguridad()
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

    def obtener_nombres_modulos_por_rol(self, nombre_rol):
        """Retorna una lista de nombres de módulos que el rol puede ver."""
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor(dictionary=True)
            sql = """
                SELECT DISTINCT m.nombre
                FROM roles_permisos rp
                JOIN modulos m ON rp.id_modulo = m.id_modulo
                JOIN roles r ON rp.id_rol = r.id_rol
                WHERE r.nombre = %s
                  AND rp.puede_ver = 1
                  AND rp.estado = 1
                  AND m.estado = 1
            """
            cursor.execute(sql, (nombre_rol,))
            rows = cursor.fetchall()
            return [row['nombre'] for row in rows]
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def obtener_permiso(self, nombre_rol, id_usuario, nombre_modulo):
        """Obtiene el permiso efectivo de un usuario sobre un módulo."""
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                """SELECT rp.puede_ver, rp.puede_crear, rp.puede_editar, rp.puede_eliminar,
                          up.puede_ver AS usuario_puede_ver, up.puede_crear AS usuario_puede_crear,
                          up.puede_editar AS usuario_puede_editar, up.puede_eliminar AS usuario_puede_eliminar
                     FROM modulos m
                     LEFT JOIN roles r ON r.nombre = %s
                     LEFT JOIN roles_permisos rp ON rp.id_rol = r.id_rol AND rp.id_modulo = m.id_modulo AND rp.estado = 1
                     LEFT JOIN usuarios_permisos up ON up.id_usuario = %s AND up.id_modulo = m.id_modulo AND up.estado = 1
                    WHERE m.nombre = %s AND m.estado = 1""",
                (nombre_rol, id_usuario, nombre_modulo))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                accion: row[f'usuario_{accion}'] if row[f'usuario_{accion}'] is not None else row[accion]
                for accion in ('puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar')
            }
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def obtener_permisos_usuario(self, id_usuario):
        """Retorna las excepciones de permisos asignadas directamente a un usuario."""
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor(dictionary=True)
            cursor.execute(
                """SELECT m.nombre, up.id_modulo, up.puede_ver,
                          up.puede_crear, up.puede_editar, up.puede_eliminar
                     FROM usuarios_permisos up
                     JOIN modulos m ON m.id_modulo = up.id_modulo
                    WHERE up.id_usuario = %s AND up.estado = 1
                      AND m.estado = 1""",
                (id_usuario,))
            return cursor.fetchall()
        finally:
            if cursor: cursor.close()
            if con: con.close()

    def guardar_permisos_usuario(self, id_usuario, permisos):
        """Reemplaza las excepciones directas de un usuario en una transacción."""
        con = cursor = None
        try:
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE usuarios_permisos SET estado = 0 WHERE id_usuario = %s",
                (id_usuario,))
            for permiso in permisos:
                cursor.execute(
                    """INSERT INTO usuarios_permisos
                         (id_usuario, id_modulo, puede_ver, puede_crear,
                          puede_editar, puede_eliminar, estado)
                                             VALUES (%s, %s, %s, %s, %s, %s, 1)
                                             ON DUPLICATE KEY UPDATE
                                                 puede_ver = VALUES(puede_ver), puede_crear = VALUES(puede_crear),
                                                 puede_editar = VALUES(puede_editar), puede_eliminar = VALUES(puede_eliminar),
                                                 estado = 1""",
                    (id_usuario, permiso.get('id_modulo'),
                     int(bool(permiso.get('puede_ver'))),
                     int(bool(permiso.get('puede_crear'))),
                     int(bool(permiso.get('puede_editar'))),
                     int(bool(permiso.get('puede_eliminar')))))
            con.commit()
            return True
        except Exception as e:
            if con: con.rollback()
            print(f"[RolPermisoModel.guardar_permisos_usuario] Error: {e}")
            return False
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
            con = self.obtener_conexion_seguridad()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE roles_permisos SET estado = 0 WHERE id_rol = %s", (id_rol,))
            for p in permisos:
                cursor.execute(
                    """INSERT INTO roles_permisos
                         (id_rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar, estado)
                                             VALUES (%s, %s, %s, %s, %s, %s, 1)
                                             ON DUPLICATE KEY UPDATE
                                                 puede_ver = VALUES(puede_ver), puede_crear = VALUES(puede_crear),
                                                 puede_editar = VALUES(puede_editar), puede_eliminar = VALUES(puede_eliminar),
                                                 estado = 1""",
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
