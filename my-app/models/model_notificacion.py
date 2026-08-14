"""
NotificacionModel — Modelo para la tabla `notificaciones`.

Las notificaciones son por usuario (destinatario) y se usan en el "campanita"
del panel. La tabla se crea automáticamente (CREATE TABLE IF NOT EXISTS) la
primera vez que se usa, sobre la base de datos de seguridad (donde vive
la tabla `usuarios`).

Principios: SQL parametrizado, validación de entrada y cierre seguro de
conexiones.
"""
import re
from datetime import datetime
from conexion.conexionBD import connectionBD_seguridad
from models.base_model import BaseModel


class NotificacionModel(BaseModel):
    """Repositorio de la tabla notificaciones."""

    _RE_TEXTO = re.compile(r"^[\w\s\.\,\-\#\(\)áéíóúÁÉÍÓÚñÑ/:]{1,200}$", re.UNICODE)
    _RE_MODULO = re.compile(r"^[\w\s\-áéíóúÁÉÍÓÚñÑ]{1,30}$", re.UNICODE)

    # -----------------------------------------------------------------
    # Conexión y aseguramiento de tabla
    # -----------------------------------------------------------------
    @staticmethod
    def _con():
        return connectionBD_seguridad()

    def _asegurar_tabla(self):
        """Crea la tabla notificaciones si no existe."""
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id_notificacion INT AUTO_INCREMENT PRIMARY KEY,
                    usuarios_id_usuarios INT NOT NULL DEFAULT 0,
                    modulo VARCHAR(30) NOT NULL DEFAULT 'General',
                    titulo VARCHAR(120) NOT NULL DEFAULT '',
                    mensaje VARCHAR(255) NOT NULL DEFAULT '',
                    enlace VARCHAR(255) NULL,
                    leida TINYINT(1) NOT NULL DEFAULT 0,
                    creado_por VARCHAR(60) NULL,
                    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_notif_usuario (usuarios_id_usuarios, leida)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
            conn.commit()
        except Exception as e:
            print(f"[NotificacionModel._asegurar_tabla] Error: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    # -----------------------------------------------------------------
    # SQL privado
    # -----------------------------------------------------------------
    def _sql_crear(self, id_usuario, modulo, titulo, mensaje, enlace, creado_por):
        conn = cursor = None
        try:
            self._asegurar_tabla()
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = """
                INSERT INTO notificaciones
                    (usuarios_id_usuarios, modulo, titulo, mensaje, enlace, leida, creado_por, fecha)
                VALUES (%s, %s, %s, %s, %s, 0, %s, %s)
            """
            cursor.execute(sql, (
                int(id_usuario) if str(id_usuario).isdigit() else 0,
                modulo[:30],
                titulo[:120],
                mensaje[:255],
                (enlace or '')[:255],
                (creado_por or '')[:60],
                datetime.now()
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"[NotificacionModel._sql_crear] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_listar(self, id_usuario, limit=20):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id_notificacion, modulo, titulo, mensaje, enlace,
                       leida, creado_por, fecha
                FROM notificaciones
                WHERE usuarios_id_usuarios = %s
                ORDER BY leida ASC, fecha DESC
                LIMIT %s
            """
            cursor.execute(sql, (int(id_usuario), int(limit)))
            return cursor.fetchall()
        except Exception as e:
            print(f"[NotificacionModel._sql_listar] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_contar_no_leidas(self, id_usuario):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return 0
            cursor = conn.cursor()
            sql = """
                SELECT COUNT(*) AS total
                FROM notificaciones
                WHERE usuarios_id_usuarios = %s AND leida = 0
            """
            cursor.execute(sql, (int(id_usuario),))
            fila = cursor.fetchone()
            if isinstance(fila, dict):
                return int(fila.get('total', 0))
            return int(fila[0]) if fila else 0
        except Exception as e:
            print(f"[NotificacionModel._sql_contar_no_leidas] Error: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_marcar_leida(self, id_notificacion, id_usuario):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = """
                UPDATE notificaciones
                SET leida = 1
                WHERE id_notificacion = %s AND usuarios_id_usuarios = %s
            """
            cursor.execute(sql, (int(id_notificacion), int(id_usuario)))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[NotificacionModel._sql_marcar_leida] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_marcar_todas(self, id_usuario):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = """
                UPDATE notificaciones
                SET leida = 1
                WHERE usuarios_id_usuarios = %s AND leida = 0
            """
            cursor.execute(sql, (int(id_usuario),))
            conn.commit()
            return True
        except Exception as e:
            print(f"[NotificacionModel._sql_marcar_todas] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_eliminar(self, id_notificacion, id_usuario):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = """
                DELETE FROM notificaciones
                WHERE id_notificacion = %s AND usuarios_id_usuarios = %s
            """
            cursor.execute(sql, (int(id_notificacion), int(id_usuario)))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[NotificacionModel._sql_eliminar] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_eliminar_todas(self, id_usuario):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = """
                DELETE FROM notificaciones
                WHERE usuarios_id_usuarios = %s
            """
            cursor.execute(sql, (int(id_usuario),))
            conn.commit()
            return True
        except Exception as e:
            print(f"[NotificacionModel._sql_eliminar_todas] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_ids_por_rol(self, rol):
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT id_usuarios FROM usuarios WHERE rol = %s"
            cursor.execute(sql, (rol,))
            return [int(r['id_usuarios']) for r in cursor.fetchall()]
        except Exception as e:
            print(f"[NotificacionModel._sql_ids_por_rol] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    # -----------------------------------------------------------------
    # Métodos públicos (fachada)
    # -----------------------------------------------------------------
    def crear(self, id_usuario, modulo, titulo, mensaje, enlace=None, creado_por=None):
        modulo = str(modulo or 'General').strip()[:30]
        titulo = str(titulo or '').strip()[:120]
        mensaje = str(mensaje or '').strip()[:255]
        if not titulo:
            return False
        return self._sql_crear(id_usuario, modulo, titulo, mensaje, enlace, creado_por)

    def listar(self, id_usuario, limit=20):
        return self._sql_listar(id_usuario, limit)

    def contar_no_leidas(self, id_usuario):
        try:
            return self._sql_contar_no_leidas(int(id_usuario))
        except (TypeError, ValueError):
            return 0

    def marcar_leida(self, id_notificacion, id_usuario):
        return self._sql_marcar_leida(id_notificacion, id_usuario)

    def marcar_todas(self, id_usuario):
        return self._sql_marcar_todas(id_usuario)

    def eliminar(self, id_notificacion, id_usuario):
        return self._sql_eliminar(id_notificacion, id_usuario)

    def eliminar_todas(self, id_usuario):
        return self._sql_eliminar_todas(id_usuario)

    def ids_por_rol(self, rol):
        return self._sql_ids_por_rol(rol)


# -----------------------------------------------------------------
# Funciones auxiliares (fachada global) para usar desde cualquier
# controlador sin instanciar el modelo.
# -----------------------------------------------------------------
def notificar(id_usuario, modulo, titulo, mensaje, enlace=None, creado_por=None):
    """Crea una notificación para un usuario específico."""
    return NotificacionModel().crear(id_usuario, modulo, titulo, mensaje, enlace, creado_por)


def notificar_a_rol(rol, modulo, titulo, mensaje, enlace=None, creado_por=None):
    """Crea una notificación para todos los usuarios con el rol indicado."""
    modelo = NotificacionModel()
    for uid in modelo.ids_por_rol(rol):
        modelo.crear(uid, modulo, titulo, mensaje, enlace, creado_por)


def notificar_a_roles(roles, modulo, titulo, mensaje, enlace=None, creado_por=None, excluir_id=None):
    """Crea una notificación para todos los usuarios de varios roles.
    Si se indica excluir_id, omite a ese usuario (p. ej. el autor de la acción)."""
    modelo = NotificacionModel()
    for rol in roles:
        for uid in modelo.ids_por_rol(rol):
            if excluir_id is not None and int(uid) == int(excluir_id):
                continue
            modelo.crear(uid, modulo, titulo, mensaje, enlace, creado_por)
