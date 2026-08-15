"""
InspeccionModel — Modelo SOLID/POO para gestion de inspecciones.
Implementa encapsulamiento, validaciones Regex, borrado logico y relacion con obras y evidencias.
"""

import re
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara, connectionBD_invilara_seguridad
from models.base_model import BaseModel


class InspeccionModel(BaseModel):
    """Repositorio de inspecciones con validacion y encapsulamiento."""

    _RE_FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    _RE_OBSERVACIONES = re.compile(r'^[\s\S]{5,255}$')
    _TIPOS_INSPECCION_VALIDOS = {'Inicial', 'Intermedia', 'Final', 'Extraordinaria'}

    def __init__(self):
        self.__id_inspeccion = None
        self.__inspector = None
        self.__fecha_inspeccion = None
        self.__tipo_inspeccion = None
        self.__observaciones = None
        self.__obra_id_obra = None
        self.__evidencia_id_evidencia = None
        self.__estado = 1
        self.__asegurar_tabla_inspeccion()

    def _conectar(self):
        try:
            conn = connectionBD_invilara()
            if conn:
                return conn
        except Exception as e:
            print(f"[CONEXION] Falló conexión principal: {e}")
        try:
            conn = connectionBD_invilara_seguridad()
            if conn:
                return conn
        except Exception as e:
            print(f"[CONEXION] Falló conexión alternativa: {e}")
        return None

    def __asegurar_tabla_inspeccion(self):
        try:
            conn = self._conectar()
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute("SHOW COLUMNS FROM inspeccion LIKE 'estado'")
                    if not cur.fetchone():
                        cur.execute("ALTER TABLE inspeccion ADD COLUMN estado TINYINT NOT NULL DEFAULT 1")
                        conn.commit()
                        print("[DB] Columna 'estado' agregada a tabla inspeccion")

                    cur.execute("SHOW COLUMNS FROM inspeccion LIKE 'cedula'")
                    if cur.fetchone():
                        self.__limpiar_cedula_inspeccion(cur, conn)
                        print("[DB] Columna 'cedula' y su indice eliminados de tabla inspeccion")
                except Exception as e:
                    print(f"[DB] Error al verificar tabla: {e}")
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla: {e}")

    def __limpiar_cedula_inspeccion(self, cur, conn=None):
        try:
            cur.execute("SELECT TRIGGER_NAME FROM INFORMATION_SCHEMA.TRIGGERS WHERE EVENT_OBJECT_TABLE = 'inspeccion'")
            triggers = cur.fetchall()
            for trigger in triggers:
                trigger_name = trigger[0] if isinstance(trigger, (list, tuple)) else trigger.get('TRIGGER_NAME', '')
                if trigger_name:
                    try:
                        cur.execute(f"DROP TRIGGER IF EXISTS {trigger_name}")
                        print(f"[DB] Trigger eliminado: {trigger_name}")
                    except Exception as e:
                        print(f"[DB] Error al eliminar trigger {trigger_name}: {e}")
        except Exception as e:
            print(f"[DB] Error al listar triggers: {e}")

        try:
            cur.execute("SHOW INDEX FROM inspeccion WHERE Key_name = 'cedula_UNIQUE'")
            if cur.fetchone():
                try:
                    cur.execute("ALTER TABLE inspeccion DROP INDEX cedula_UNIQUE")
                    print("[DB] Indice cedula_UNIQUE eliminado")
                except Exception as e:
                    print(f"[DB] Error al eliminar indice cedula_UNIQUE: {e}")
        except Exception as e:
            print(f"[DB] Error al buscar indice cedula_UNIQUE: {e}")

        try:
            cur.execute("SHOW COLUMNS FROM inspeccion LIKE 'cedula'")
            if cur.fetchone():
                try:
                    cur.execute("ALTER TABLE inspeccion DROP COLUMN cedula")
                    print("[DB] Columna cedula eliminada")
                except Exception as e:
                    print(f"[DB] Error al eliminar columna cedula: {e}")
        except Exception as e:
            print(f"[DB] Error al buscar columna cedula: {e}")

        if conn:
            try:
                conn.commit()
                print("[DB] Commit de limpieza ejecutado")
            except Exception as e:
                print(f"[DB] Error en commit de limpieza: {e}")

    def get_id_inspeccion(self):
        return self.__id_inspeccion

    def set_id_inspeccion(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de inspeccion debe ser un entero positivo.")
        self.__id_inspeccion = valor

    def get_inspector(self):
        return self.__inspector

    def set_inspector(self, valor):
        if not self._validar_inspector(valor):
            raise ValueError("Debe seleccionar un inspector valido.")
        self.__inspector = int(valor)

    def get_fecha_inspeccion(self):
        return self.__fecha_inspeccion

    def set_fecha_inspeccion(self, valor):
        if not self._validar_fecha(valor):
            raise ValueError("Formato de fecha invalido. Use YYYY-MM-DD.")
        self.__fecha_inspeccion = valor

    def get_tipo_inspeccion(self):
        return self.__tipo_inspeccion

    def set_tipo_inspeccion(self, valor):
        valor_limpio = self._limpiar_texto(valor, 45)
        if valor_limpio not in self._TIPOS_INSPECCION_VALIDOS:
            raise ValueError("Tipo de inspeccion invalido.")
        self.__tipo_inspeccion = valor_limpio

    def get_observaciones(self):
        return self.__observaciones

    def set_observaciones(self, valor):
        if not self._validar_observaciones(valor):
            raise ValueError("Observaciones invalidas.")
        self.__observaciones = self._limpiar_texto(valor, 255)

    def get_obra_id_obra(self):
        return self.__obra_id_obra

    def set_obra_id_obra(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de obra invalido.")
        self.__obra_id_obra = valor

    def get_evidencia_id_evidencia(self):
        return self.__evidencia_id_evidencia

    def set_evidencia_id_evidencia(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de evidencia debe ser un entero positivo.")
        self.__evidencia_id_evidencia = valor

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 o 1.")
        self.__estado = valor

    def _validar_inspector(self, inspector: str) -> bool:
        try:
            return int(inspector) > 0
        except (ValueError, TypeError):
            return False

    def _validar_fecha(self, fecha: str) -> bool:
        return bool(self._RE_FECHA.match(str(fecha)))

    def _validar_observaciones(self, observaciones: str) -> bool:
        texto = str(observaciones or '').strip()
        return len(texto) >= 5 and len(texto) <= 255

    @staticmethod
    def __obtener_siguiente_id_inspeccion(conn):
        cur_id = conn.cursor(dictionary=True)
        try:
            cur_id.execute("SELECT COALESCE(MAX(id_inspeccion), 0) + 1 AS siguiente FROM inspeccion")
            fila = cur_id.fetchone()
            return int(fila['siguiente']) if fila else 1
        finally:
            cur_id.close()

    def __guardar_inspeccion_db(self):
        conn = None
        cur = None
        try:
            conn = self._conectar()
            if not conn:
                raise Exception("Error de conexion a la base de datos.")
            cur = conn.cursor(dictionary=True)

            self.__limpiar_cedula_inspeccion(cur, conn)

            tiene_cedula = self.__columna_existe('inspeccion', 'cedula')
            tiene_trigger = False
            try:
                cur.execute("SELECT TRIGGER_NAME FROM INFORMATION_SCHEMA.TRIGGERS WHERE EVENT_OBJECT_TABLE = 'inspeccion' LIMIT 1")
                tiene_trigger = cur.fetchone() is not None
            except Exception:
                pass
            if tiene_cedula or tiene_trigger:
                raise ValueError("La tabla inspeccion tiene restricciones (cedula/trigger) que impiden el registro. Ejecute manualmente: DROP TRIGGER IF EXISTS inspeccion_bi; DROP INDEX cedula_UNIQUE ON inspeccion; ALTER TABLE inspeccion DROP COLUMN cedula;")

            obra = self.__buscar_obra_por_id_db(self.__obra_id_obra)
            if not obra:
                raise ValueError("La obra seleccionada no existe en la base de datos.")

            evidencia = self.__buscar_evidencia_por_id_db(self.__evidencia_id_evidencia)
            if not evidencia:
                raise ValueError("La evidencia seleccionada no existe en la base de datos.")

            semaforo_id = obra.get('semaforo_id_semaforo') or 1
            contratacion_id = obra.get('contratacion_id_contratacion') or 1
            codigo_proyecto = obra.get('gestionar_proyectos_codigo_proyecto') or 'FRE-001'
            etapa_sincronizada = self.__mapear_tipo_a_etapa(self.__tipo_inspeccion)

            tiene_estado = self.__columna_existe('inspeccion', 'estado')
            if tiene_estado:
                columnas = "(id_inspeccion, inspector, fecha_inspeccion, tipo_inspeccion, observaciones, obra_id_obra, obra_semaforo_id_semaforo, obra_contratacion_id_contratacion, obra_gestionar_proyectos_codigo_proyecto, obra_id_obra1, obra_semaforo_id_semaforo1, obra_contratacion_id_contratacion1, obra_gestionar_proyectos_codigo_proyecto1, evidencia_id_evidencia, estado)"
                valores = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                params = (
                    self.__obtener_siguiente_id_inspeccion(conn), self.__inspector, self.__fecha_inspeccion, self.__tipo_inspeccion, self.__observaciones,
                    self.__obra_id_obra, semaforo_id, contratacion_id, codigo_proyecto,
                    self.__obra_id_obra, semaforo_id, contratacion_id, codigo_proyecto,
                    self.__evidencia_id_evidencia, 1
                )
            else:
                columnas = "(id_inspeccion, inspector, fecha_inspeccion, tipo_inspeccion, observaciones, obra_id_obra, obra_semaforo_id_semaforo, obra_contratacion_id_contratacion, obra_gestionar_proyectos_codigo_proyecto, obra_id_obra1, obra_semaforo_id_semaforo1, obra_contratacion_id_contratacion1, obra_gestionar_proyectos_codigo_proyecto1, evidencia_id_evidencia)"
                valores = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s"
                params = (
                    self.__obtener_siguiente_id_inspeccion(conn), self.__inspector, self.__fecha_inspeccion, self.__tipo_inspeccion, self.__observaciones,
                    self.__obra_id_obra, semaforo_id, contratacion_id, codigo_proyecto,
                    self.__obra_id_obra, semaforo_id, contratacion_id, codigo_proyecto,
                    self.__evidencia_id_evidencia
                )

            sql = f"INSERT INTO inspeccion {columnas} VALUES ({valores})"
            cur.execute(sql, params)
            conn.commit()

            nuevo_id = cur.lastrowid
            print(f"[DEBUG] Insert OK, id_inspeccion={nuevo_id}, lastrowid={cur.lastrowid}")
            if not nuevo_id:
                raise ValueError("El registro no devolvió un ID válido.")
            return nuevo_id
        except Exception as e:
            if conn:
                conn.rollback()
            raise ValueError(f"Error en base de datos: {str(e)}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __actualizar_inspeccion_db(self):
        conn = None
        cur = None
        try:
            conn = self._conectar()
            if not conn:
                raise Exception("Error de conexion a la base de datos.")
            cur = conn.cursor()

            self.__limpiar_cedula_inspeccion(cur, conn)

            obra = self.__buscar_obra_por_id_db(self.__obra_id_obra)
            if not obra:
                raise ValueError("La obra seleccionada no existe en la base de datos.")

            evidencia = self.__buscar_evidencia_por_id_db(self.__evidencia_id_evidencia)
            if not evidencia:
                raise ValueError("La evidencia seleccionada no existe en la base de datos.")

            semaforo_id = obra.get('semaforo_id_semaforo') or 1
            contratacion_id = obra.get('contratacion_id_contratacion') or 1
            codigo_proyecto = obra.get('gestionar_proyectos_codigo_proyecto') or 'FRE-001'
            etapa_sincronizada = self.__mapear_tipo_a_etapa(self.__tipo_inspeccion)

            tiene_estado = self.__columna_existe('inspeccion', 'estado')
            set_estado = ", estado = 1" if tiene_estado else ""

            sql = f"""
                UPDATE inspeccion
                SET inspector = %s, fecha_inspeccion = %s, tipo_inspeccion = %s,
                    observaciones = %s, obra_id_obra = %s,
                    obra_semaforo_id_semaforo = %s, obra_contratacion_id_contratacion = %s,
                    obra_gestionar_proyectos_codigo_proyecto = %s,
                    obra_id_obra1 = %s, obra_semaforo_id_semaforo1 = %s,
                    obra_contratacion_id_contratacion1 = %s,
                    obra_gestionar_proyectos_codigo_proyecto1 = %s,
                    evidencia_id_evidencia = %s{set_estado}
                WHERE id_inspeccion = %s AND 1 = 1
            """
            cur.execute(sql, (
                self.__inspector, self.__fecha_inspeccion, self.__tipo_inspeccion, self.__observaciones,
                self.__obra_id_obra, semaforo_id, contratacion_id, codigo_proyecto,
                self.__obra_id_obra, semaforo_id, contratacion_id, codigo_proyecto,
                self.__evidencia_id_evidencia, self.__id_inspeccion
            ))

            cur.execute(
                "UPDATE evidencia SET etapa = %s, fecha_registro = NOW() WHERE id_evidencia = %s AND estado = 1",
                (etapa_sincronizada, self.__evidencia_id_evidencia,)
            )

            conn.commit()
            print(f"[DEBUG] Update OK, rowcount={cur.rowcount}")
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            raise ValueError(f"Error en base de datos: {str(e)}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __eliminar_logico_db(self):
        conn = self._conectar()
        if not conn:
            raise Exception("Error de conexion a la base de datos.")
        cur = conn.cursor()
        try:
            cur.execute("UPDATE inspeccion SET estado = 0 WHERE id_inspeccion = %s", (self.__id_inspeccion,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

    def __obtener_inspeccion_por_id_db(self):
        conn = self._conectar()
        if not conn:
            return None
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT i.*, e.nombre_empleado AS inspector_nombre
                FROM inspeccion i
                LEFT JOIN empleados e ON e.id_empleados = i.inspector
                WHERE i.id_inspeccion = %s AND i.estado = 1
            """, (self.__id_inspeccion,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def __columna_existe(self, tabla, columna):
        conn = self._conectar()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            cur.execute(f"SHOW COLUMNS FROM {tabla} LIKE '{columna}'")
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    def __obtener_todas_inspecciones_db(self):
        conn = self._conectar()
        if not conn:
            print('[LISTADO] ERROR: No hay conexión a la base de datos')
            return []
        cur = conn.cursor(dictionary=True)
        try:
            tiene_estado = self.__columna_existe('inspeccion', 'estado')
            where = "WHERE i.estado = 1" if tiene_estado else ""
            cur.execute(f"""
                SELECT i.*, e.nombre_empleado AS inspector_nombre
                FROM inspeccion i
                LEFT JOIN empleados e ON e.id_empleados = i.inspector
                {where}
                ORDER BY i.id_inspeccion DESC
            """)
            rows = cur.fetchall()
            print(f'[LISTADO] Inspecciones encontradas: {len(rows)}')
            if rows:
                print(f'[LISTADO] Ultima inspeccion: id={rows[0].get("id_inspeccion")} fecha={rows[0].get("fecha_inspeccion")}')
            return rows
        finally:
            cur.close()
            conn.close()

    def __obtener_inspeccion_por_id_db(self):
        conn = self._conectar()
        if not conn:
            return None
        cur = conn.cursor(dictionary=True)
        try:
            tiene_estado = self.__columna_existe('inspeccion', 'estado')
            where = "AND i.estado = 1" if tiene_estado else ""
            cur.execute(f"""
                SELECT i.*, e.nombre_empleado AS inspector_nombre,
                       ev.id_evidencia, ev.fotos AS evidencia_fotos,
                       ev.url_archivos AS evidencia_url, ev.etapa AS evidencia_etapa
                FROM inspeccion i
                LEFT JOIN empleados e ON e.id_empleados = i.inspector
                LEFT JOIN evidencia ev ON ev.id_evidencia = i.evidencia_id_evidencia AND ev.estado = 1
                WHERE i.id_inspeccion = %s {where}
            """, (self.__id_inspeccion,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def __validar_inspeccion_activa_db(self):
        conn = self._conectar()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            tiene_estado = self.__columna_existe('inspeccion', 'estado')
            if tiene_estado:
                cur.execute("SELECT id_inspeccion FROM inspeccion WHERE id_inspeccion = %s AND estado = 1", (self.__id_inspeccion,))
            else:
                cur.execute("SELECT id_inspeccion FROM inspeccion WHERE id_inspeccion = %s", (self.__id_inspeccion,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    def __eliminar_logico_db(self):
        conn = self._conectar()
        if not conn:
            raise Exception("Error de conexion a la base de datos.")
        cur = conn.cursor()
        try:
            tiene_estado = self.__columna_existe('inspeccion', 'estado')
            if tiene_estado:
                cur.execute("UPDATE inspeccion SET estado = 0 WHERE id_inspeccion = %s", (self.__id_inspeccion,))
                conn.commit()
                return cur.rowcount > 0
            else:
                print("[DB] No se puede hacer borrado logico: falta columna estado")
                return False
        finally:
            cur.close()
            conn.close()

    def __validar_obra_existe_db(self, obra_id):
        conn = self._conectar()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            cur.execute("SELECT id_obra FROM obra WHERE id_obra = %s", (obra_id,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    def __validar_evidencia_existe_db(self, evidencia_id):
        conn = self._conectar()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            cur.execute("SELECT id_evidencia FROM evidencia WHERE id_evidencia = %s AND estado = 1", (evidencia_id,))
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    def __obtener_obras_db(self):
        conn = self._conectar()
        if not conn:
            print('[OBRAS] ERROR: No hay conexión a la base de datos')
            return []
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT id_obra, titulo_obra, ubicacion_obra,
                       semaforo_id_semaforo, contratacion_id_contratacion,
                       gestionar_proyectos_codigo_proyecto
                FROM obra
                ORDER BY id_obra DESC
            """)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def __buscar_obra_por_id_db(self, obra_id):
        conn = self._conectar()
        if not conn:
            return None
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT id_obra, titulo_obra, ubicacion_obra,
                       semaforo_id_semaforo, contratacion_id_contratacion,
                       gestionar_proyectos_codigo_proyecto
                FROM obra
                WHERE id_obra = %s
            """, (obra_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def __buscar_evidencia_por_id_db(self, evidencia_id):
        conn = self._conectar()
        if not conn:
            return None
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT id_evidencia, fotos, etapa
                FROM evidencia
                WHERE id_evidencia = %s AND estado = 1
            """, (evidencia_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def __mapear_tipo_a_etapa(tipo_inspeccion):
        mapa = {
            'Inicial': 'antes',
            'Intermedia': 'durante',
            'Final': 'despues',
            'Extraordinaria': 'durante'
        }
        return mapa.get(tipo_inspeccion, 'antes')

    def __obtener_evidencias_db(self):
        conn = self._conectar()
        if not conn:
            print('[EVIDENCIAS] ERROR: No hay conexión a la base de datos')
            return []
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT id_evidencia, fotos, url_archivos, etapa FROM evidencia WHERE estado = 1 ORDER BY id_evidencia DESC")
            rows = cur.fetchall()
            print(f'[EVIDENCIAS] Filas encontradas: {len(rows)}')
            return rows
        finally:
            cur.close()
            conn.close()

    def __obtener_inspectores_db(self):
        conn = self._conectar()
        if not conn:
            print('[INSPECTORES] ERROR: No hay conexión a la base de datos')
            return []
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT id_empleados, nombre_empleado, cargo, gerencia_asignada
                FROM empleados
                WHERE TRIM(cargo) = 'Inspector' AND estado = 1
                ORDER BY nombre_empleado ASC
            """)
            rows = cur.fetchall()
            print(f'[INSPECTORES] Filas encontradas: {len(rows)}')
            return rows
        finally:
            cur.close()
            conn.close()

    # ========== METODOS PUBLICOS ==========

    def registrar_inspeccion(self, data):
        try:
            self.set_inspector(data.get('inspector'))
            self.set_fecha_inspeccion(data.get('fecha_inspeccion'))
            self.set_tipo_inspeccion(data.get('tipo_inspeccion'))
            self.set_observaciones(data.get('observaciones'))
            self.set_obra_id_obra(int(data.get('obra_id_obra')))
            self.set_evidencia_id_evidencia(int(data.get('evidencia_id_evidencia')))
            print(f"[DEBUG] Registrar inspeccion: obra={self.__obra_id_obra}, evidencia={self.__evidencia_id_evidencia}")
            return self.__guardar_inspeccion_db()
        except ValueError as ve:
            print(f"[DEBUG] Error de validacion al registrar: {ve}")
            raise ve
        except Exception as e:
            print(f"[DEBUG] Error inesperado al registrar: {e}")
            return None

    def actualizar_inspeccion(self, data):
        try:
            id_inspeccion = int(data.get('id_inspeccion'))
            self.set_id_inspeccion(id_inspeccion)
            if not self.__validar_inspeccion_activa_db():
                raise ValueError("La inspeccion no existe o fue eliminada.")

            self.set_id_inspeccion(id_inspeccion)
            self.set_inspector(data.get('inspector'))
            self.set_fecha_inspeccion(data.get('fecha_inspeccion'))
            self.set_tipo_inspeccion(data.get('tipo_inspeccion'))
            self.set_observaciones(data.get('observaciones'))
            self.set_obra_id_obra(int(data.get('obra_id_obra')))
            self.set_evidencia_id_evidencia(int(data.get('evidencia_id_evidencia')))
            return self.__actualizar_inspeccion_db()
        except ValueError as ve:
            raise ve
        except Exception as e:
            print(f"Error inesperado al actualizar: {e}")
            return False

    def eliminar_inspeccion(self, id_inspeccion):
        try:
            self.set_id_inspeccion(id_inspeccion)
            if not self.__validar_inspeccion_activa_db():
                raise ValueError("La inspeccion no existe o ya fue eliminada.")
            return self.__eliminar_logico_db()
        except ValueError as ve:
            raise ve
        except Exception as e:
            print(f"Error al eliminar inspeccion: {e}")
            return False

    def obtener_inspeccion_por_id(self, id_inspeccion):
        try:
            self.set_id_inspeccion(id_inspeccion)
            return self.__obtener_inspeccion_por_id_db()
        except (ValueError, TypeError):
            return None

    def obtener_todas_inspecciones(self):
        return self.__obtener_todas_inspecciones_db()

    def validar_inspeccion_activa(self, id_inspeccion):
        try:
            self.set_id_inspeccion(id_inspeccion)
            return self.__validar_inspeccion_activa_db()
        except (ValueError, TypeError):
            return False

    def obtener_catalogo_tipos_inspeccion(self):
        return sorted(list(self._TIPOS_INSPECCION_VALIDOS))

    def obra_existe(self, obra_id):
        return self.__validar_obra_existe_db(obra_id)

    def evidencia_existe(self, evidencia_id):
        return self.__validar_evidencia_existe_db(evidencia_id)

    def obtener_obras(self):
        return self.__obtener_obras_db()

    def obtener_evidencias(self):
        return self.__obtener_evidencias_db()

    def obtener_inspectores(self):
        return self.__obtener_inspectores_db()
