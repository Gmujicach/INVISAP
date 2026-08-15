"""
BitacoraModel — Modelo para la tabla `bitacora`.
Principios SOLID/DRY: métodos privados con SQL, métodos públicos como fachada.
Toda entrada es validada con regex antes de ejecutar consultas parametrizadas.
"""
import re
from datetime import datetime
from conexion.conexionBD import connectionBD_seguridad
from models.base_model import BaseModel


class BitacoraModel(BaseModel):
    """
    Repositorio de la tabla bitacora.
    Métodos privados (_): contienen SQL directamente.
    Métodos públicos:     fachada con validación de entrada.
    """

    # -----------------------------------------------------------------
    # Constantes y utilidades de validación
    # -----------------------------------------------------------------
    _RE_TEXTO_SEGURO = re.compile(r"^[\w\s\.\,\-\#áéíóúÁÉÍÓÚñÑ]{1,100}$", re.UNICODE)
    _RE_USUARIO = re.compile(r"^[\w\s\-áéíóúÁÉÍÓÚñÑ]{1,15}$", re.UNICODE)

    @staticmethod
    def _es_texto_valido(texto: str) -> bool:
        return bool(BitacoraModel._RE_TEXTO_SEGURO.match(str(texto or '').strip()))

    @staticmethod
    def _es_usuario_valido(usuario: str) -> bool:
        return bool(BitacoraModel._RE_USUARIO.match(str(usuario or '').strip()))

    @staticmethod
    def _con():
        """Abre y retorna una conexión nueva."""
        return connectionBD_seguridad()

    # -----------------------------------------------------------------
    # Métodos privados — SQL
    # -----------------------------------------------------------------
    def _sql_insertar(self, usuario: str, id_usuario: int, modulo: str,
                      accion: str, descripcion: str) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            ahora = datetime.now()

            cursor.execute(
                "SELECT COALESCE(MAX(id_bitacora), 0) + 1 AS siguiente_id FROM bitacora"
            )
            fila = cursor.fetchone()
            if isinstance(fila, dict):
                siguiente_id = fila.get('siguiente_id', 1)
            else:
                siguiente_id = fila[0] if fila else 1

            sql = """
                INSERT INTO bitacora
                    (id_bitacora, usuario, id_modulo, modulo, accion, fecha,
                     hora_inicio_sesion, hora_cierre_sesion, usuarios_id_usuarios)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                siguiente_id, usuario, 0, modulo, accion,
                ahora, ahora, ahora, id_usuario
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"[BitacoraModel._sql_insertar] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_obtener_todos(self, limit: int = 500) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id_bitacora, usuario, modulo, accion,
                       fecha, hora_inicio_sesion, hora_cierre_sesion,
                       usuarios_id_usuarios
                FROM bitacora
                ORDER BY fecha DESC
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[BitacoraModel._sql_obtener_todos] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_filtrar_por_usuario(self, usuario: str) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id_bitacora, usuario, modulo, accion,
                       fecha, hora_inicio_sesion, hora_cierre_sesion
                FROM bitacora
                WHERE usuario LIKE %s
                ORDER BY fecha DESC
                LIMIT 200
            """
            cursor.execute(sql, (f"%{usuario}%",))
            return cursor.fetchall()
        except Exception as e:
            print(f"[BitacoraModel._sql_filtrar_por_usuario] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_filtrar_por_modulo(self, modulo: str) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id_bitacora, usuario, modulo, accion,
                       fecha, hora_inicio_sesion, hora_cierre_sesion
                FROM bitacora
                WHERE modulo = %s
                ORDER BY fecha DESC
                LIMIT 200
            """
            cursor.execute(sql, (modulo,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[BitacoraModel._sql_filtrar_por_modulo] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_filtrar_por_accion(self, accion: str) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT id_bitacora, usuario, modulo, accion,
                       fecha, hora_inicio_sesion, hora_cierre_sesion
                FROM bitacora
                WHERE accion = %s
                ORDER BY fecha DESC
                LIMIT 200
            """
            cursor.execute(sql, (accion,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[BitacoraModel._sql_filtrar_por_accion] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_filtrar_por_criterios(self, usuario: str = None,
                                   modulo: str = None,
                                   accion: str = None,
                                   limit: int = 500,
                                   offset: int = 0) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)

            condiciones = []
            params = []

            if usuario:
                condiciones.append("usuario LIKE %s")
                params.append(f"%{usuario}%")
            if modulo:
                condiciones.append("modulo = %s")
                params.append(modulo)
            if accion:
                condiciones.append("accion = %s")
                params.append(accion)

            if not condiciones:
                return self._sql_obtener_todos(limit=limit)

            params.extend([limit, offset])
            sql = f"""
                SELECT id_bitacora, usuario, modulo, accion,
                       fecha, hora_inicio_sesion, hora_cierre_sesion,
                       usuarios_id_usuarios
                FROM bitacora
                WHERE {' AND '.join(condiciones)}
                ORDER BY fecha DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, tuple(params))
            return cursor.fetchall()
        except Exception as e:
            print(f"[BitacoraModel._sql_filtrar_por_criterios] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_contar_por_accion(self) -> dict:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return {}
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT accion, COUNT(*) AS total FROM bitacora GROUP BY accion"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return {row['accion']: row['total'] for row in rows}
        except Exception as e:
            print(f"[BitacoraModel._sql_contar_por_accion] Error: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _sql_contar_filtrados(self, usuario: str = None,
                              modulo: str = None,
                              accion: str = None) -> int:
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return 0
            cursor = conn.cursor()

            condiciones = []
            params = []

            if usuario:
                condiciones.append("usuario LIKE %s")
                params.append(f"%{usuario}%")
            if modulo:
                condiciones.append("modulo = %s")
                params.append(modulo)
            if accion:
                condiciones.append("accion = %s")
                params.append(accion)

            if not condiciones:
                sql = "SELECT COUNT(*) FROM bitacora"
                cursor.execute(sql)
            else:
                sql = f"SELECT COUNT(*) FROM bitacora WHERE {' AND '.join(condiciones)}"
                cursor.execute(sql, tuple(params))

            row = cursor.fetchone()
            return row[0] if row else 0
        except Exception as e:
            print(f"[BitacoraModel._sql_contar_filtrados] Error: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    # -----------------------------------------------------------------
    # Métodos públicos — Fachada con validación
    # -----------------------------------------------------------------
    def registrar(self, usuario: str, id_usuario: int,
                  modulo: str, accion: str, descripcion: str = '') -> bool:
        """Inserta un nuevo registro en la bitácora."""
        # Validaciones básicas de entrada
        usuario = str(usuario or 'Sistema').strip()[:15]
        modulo = str(modulo or 'General').strip()[:20]
        accion = str(accion or 'VER').upper().strip()[:45]
        id_usuario = int(id_usuario) if str(id_usuario).isdigit() else 1
        return self._sql_insertar(usuario, id_usuario, modulo, accion, descripcion)

    def obtener_todos(self) -> list:
        """Retorna los últimos 500 registros de la bitácora."""
        return self._sql_obtener_todos(limit=500)

    def filtrar_por_usuario(self, usuario: str) -> list:
        """Filtra registros de bitácora por nombre de usuario."""
        if not usuario or len(usuario.strip()) < 2:
            return []
        usuario_limpio = re.sub(r'[<>\'";\\]', '', usuario)[:15]
        return self._sql_filtrar_por_usuario(usuario_limpio)

    def filtrar_por_modulo(self, modulo: str) -> list:
        """Filtra registros de bitácora por módulo del sistema."""
        if not modulo:
            return []
        modulo_limpio = re.sub(r'[<>\'";\\]', '', modulo)[:20]
        return self._sql_filtrar_por_modulo(modulo_limpio)

    def filtrar_por_accion(self, accion: str) -> list:
        """Filtra registros por tipo de acción (CREAR, EDITAR, ELIMINAR, VER)."""
        acciones_validas = {'CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'LOGIN', 'LOGOUT'}
        accion = accion.upper().strip() if accion else ''
        if accion not in acciones_validas:
            return []
        return self._sql_filtrar_por_accion(accion)

    def filtrar_por_criterios(self, usuario: str = None,
                               modulo: str = None,
                               accion: str = None,
                               page: int = 1,
                               per_page: int = 10) -> list:
        """Filtra por uno o más criterios combinados con AND."""
        usuario_limpio = None
        modulo_limpio = None
        accion_limpia = None

        if usuario and len(usuario.strip()) >= 2:
            usuario_limpio = re.sub(r'[<>\'";\\]', '', usuario)[:15]
        if modulo:
            modulo_limpio = re.sub(r'[<>\'";\\]', '', modulo)[:20]
        if accion:
            acciones_validas = {'CREAR', 'EDITAR', 'ELIMINAR', 'VER',
                                'LOGIN', 'LOGOUT'}
            accion_upper = accion.upper().strip()
            if accion_upper in acciones_validas:
                accion_limpia = accion_upper

        if not usuario_limpio and not modulo_limpio and not accion_limpia:
            return self.obtener_todos()

        offset = (page - 1) * per_page
        return self._sql_filtrar_por_criterios(
            usuario=usuario_limpio,
            modulo=modulo_limpio,
            accion=accion_limpia,
            limit=per_page,
            offset=offset
        )

    def estadisticas_por_accion(self) -> dict:
        """Retorna conteo de registros agrupados por acción."""
        return self._sql_contar_por_accion()

    def contar_filtrados(self, usuario: str = None,
                              modulo: str = None,
                              accion: str = None) -> int:
        """Retorna el total de registros que coinciden con los filtros."""
        usuario_limpio = None
        modulo_limpio = None
        accion_limpia = None

        if usuario and len(usuario.strip()) >= 2:
            usuario_limpio = re.sub(r'[<>\'";\\]', '', usuario)[:15]
        if modulo:
            modulo_limpio = re.sub(r'[<>\'";\\]', '', modulo)[:20]
        if accion:
            acciones_validas = {'CREAR', 'EDITAR', 'ELIMINAR', 'VER',
                                'LOGIN', 'LOGOUT'}
            accion_upper = accion.upper().strip()
            if accion_upper in acciones_validas:
                accion_limpia = accion_upper

        return self._sql_contar_filtrados(
            usuario=usuario_limpio,
            modulo=modulo_limpio,
            accion=accion_limpia
        )
