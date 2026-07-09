"""
ObraModel — Modelo adaptado al esquema exacto de Invilara.
"""
from conexion.conexionBD import connectionBD

class ObraModel:
    
    @staticmethod
    def _con():
        return connectionBD()

    def _sql_obtener_todas(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT o.*, s.color, s.descripcion 
                FROM obra o
                LEFT JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                WHERE o.estado = 1
                ORDER BY o.fecha_inicio DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel._sql_obtener_todas] Error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_insertar(self, datos: dict) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            
            # La consulta SQL ahora refleja exactamente tu tabla `obra`
            sql = """
                INSERT INTO obra (
                    titulo_obra, ubicacion_obra, periodo_ejecucion, fecha_inicio, 
                    fecha_fin, mediciones_obra, valuaciones, modificaciones_contrato, 
                    certificaciones_obras_ejecutadas, numero_contrato, porcentaje_avance_obra, 
                    semaforo_id_semaforo, contratacion_id_contratacion, gestionar_proyectos_codigo_proyecto, 
                    estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            
            # El orden de los valores debe ser idéntico al de las columnas de arriba
            valores = (
                datos.get('titulo_obra'), 
                datos.get('ubicacion_obra'), 
                datos.get('periodo_ejecucion'),
                datos.get('fecha_inicio'), 
                datos.get('fecha_fin'), 
                datos.get('mediciones_obra'),
                datos.get('valuaciones'), 
                datos.get('modificaciones_contrato'),
                datos.get('certificaciones_obras_ejecutadas'), 
                datos.get('numero_contrato'),
                datos.get('porcentaje_avance_obra'), 
                datos.get('semaforo_id_semaforo'),
                datos.get('contratacion_id_contratacion'), 
                datos.get('gestionar_proyectos_codigo_proyecto')
            )
            
            cursor.execute(sql, valores)
            conn.commit()
            return True
        except Exception as e:
            print(f"[ObraModel._sql_insertar] Error crítico: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_obtener_por_id(self, id_obra: int) -> dict:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return None
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT o.*, s.color, s.descripcion 
                FROM obra o
                LEFT JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                WHERE o.id_obra = %s AND o.estado = 1
            """
            cursor.execute(sql, (id_obra,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[ObraModel._sql_obtener_por_id] Error: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_actualizar(self, id_obra: int, datos: dict) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            sql = """
                UPDATE obra SET
                    titulo_obra = %s, ubicacion_obra = %s, periodo_ejecucion = %s,
                    fecha_inicio = %s, fecha_fin = %s, mediciones_obra = %s,
                    valuaciones = %s, modificaciones_contrato = %s,
                    certificaciones_obras_ejecutadas = %s, numero_contrato = %s,
                    porcentaje_avance_obra = %s, semaforo_id_semaforo = %s,
                    contratacion_id_contratacion = %s, gestionar_proyectos_codigo_proyecto = %s
                WHERE id_obra = %s AND estado = 1
            """
            valores = (
                datos.get('titulo_obra'), datos.get('ubicacion_obra'),
                datos.get('periodo_ejecucion'), datos.get('fecha_inicio'),
                datos.get('fecha_fin'), datos.get('mediciones_obra'),
                datos.get('valuaciones'), datos.get('modificaciones_contrato'),
                datos.get('certificaciones_obras_ejecutadas'), datos.get('numero_contrato'),
                datos.get('porcentaje_avance_obra'), datos.get('semaforo_id_semaforo'),
                datos.get('contratacion_id_contratacion'), datos.get('gestionar_proyectos_codigo_proyecto'),
                id_obra
            )
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[ObraModel._sql_actualizar] Error crítico: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_eliminar(self, id_obra: int) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "UPDATE obra SET estado = 0 WHERE id_obra = %s AND estado = 1"
            cursor.execute(sql, (id_obra,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[ObraModel._sql_eliminar] Error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_validar_semaforo(self, id_semaforo) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM semaforo WHERE id_semaforo = %s AND estado IN ('Activo','1',1) LIMIT 1", (id_semaforo,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel._sql_validar_semaforo] Error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_validar_contratacion(self, id_contratacion) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM contratacion WHERE id_contratacion = %s AND estado IN ('Activo','1',1) LIMIT 1", (id_contratacion,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel._sql_validar_contratacion] Error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_validar_proyecto(self, codigo_proyecto) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM proyecto WHERE codigo_proyecto = %s AND estado IN ('Activo','1',1) LIMIT 1", (codigo_proyecto,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel._sql_validar_proyecto] Error: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def validar_semaforo(self, id_semaforo) -> bool:
        return self._sql_validar_semaforo(id_semaforo)

    def validar_contratacion(self, id_contratacion) -> bool:
        return self._sql_validar_contratacion(id_contratacion)

    def validar_proyecto(self, codigo_proyecto) -> bool:
        return self._sql_validar_proyecto(codigo_proyecto)

    def _sql_listar_semaforos(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_semaforo, color, descripcion FROM semaforo")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel._sql_listar_semaforos] Error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_listar_contrataciones(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_contratacion, numero_contrato, empresa_ganadora FROM contratacion WHERE estado = 1 ORDER BY id_contratacion DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel._sql_listar_contrataciones] Error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def _sql_listar_proyectos(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT codigo_proyecto, descripcion_tecnica, fecha_planificacion FROM proyecto WHERE estado IN ('Activo','1',1) ORDER BY codigo_proyecto DESC")
            filas = cursor.fetchall()
            print(f"[ObraModel._sql_listar_proyectos] Total proyectos activos encontrados: {len(filas)}")
            for fila in filas:
                print(f"[ObraModel._sql_listar_proyectos] Proyecto: {fila}")
            return filas
        except Exception as e:
            print(f"[ObraModel._sql_listar_proyectos] Error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def obtener_obra_por_id(self, id_obra: int) -> dict:
        return self._sql_obtener_por_id(id_obra)

    def actualizar_obra(self, id_obra: int, datos: dict) -> bool:
        return self._sql_actualizar(id_obra, datos)

    def eliminar_obra(self, id_obra: int) -> bool:
        return self._sql_eliminar(id_obra)

    def validar_semaforo(self, id_semaforo) -> bool:
        return self._sql_validar_semaforo(id_semaforo)

    def validar_contratacion(self, id_contratacion) -> bool:
        return self._sql_validar_contratacion(id_contratacion)

    def validar_proyecto(self, codigo_proyecto) -> bool:
        return self._sql_validar_proyecto(codigo_proyecto)

    def listar_semaforos(self) -> list:
        return self._sql_listar_semaforos()

    def listar_contrataciones(self) -> list:
        return self._sql_listar_contrataciones()

    def listar_proyectos(self) -> list:
        return self._sql_listar_proyectos()

    def obtener_todas(self) -> list:
        return self._sql_obtener_todas()

    def registrar_obra(self, datos: dict) -> bool:
        return self._sql_insertar(datos)
