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
            sql = "SELECT * FROM obra WHERE estado = 1 ORDER BY fecha_inicio DESC"
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
                    id_obra, titulo_obra, ubicacion_obra, periodo_ejecucion, fecha_inicio, 
                    fecha_fin, mediciones_obra, valuaciones, modificaciones_contrato, 
                    certificaciones_obras_ejecutadas, numero_contrato, porcentaje_avance_obra, 
                    semaforo_id_semaforo, contratacion_id_contratacion, gestionar_proyectos_codigo_proyecto, 
                    estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            
            cursor.execute("SELECT COALESCE(MAX(id_obra), 0) + 1 AS siguiente_id FROM obra")
            fila = cursor.fetchone()
            siguiente_id = fila[0] if fila else 1
            
            valores = (
                siguiente_id,
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

    def obtener_todas(self) -> list:
        return self._sql_obtener_todas()

    def registrar_obra(self, datos: dict) -> bool:
        return self._sql_insertar(datos)

    def actualizar_obra(self, id_obra: int, datos: dict) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return False
            cursor = conn.cursor()

            porcentaje = datos.get('porcentaje_avance_obra')
            try:
                porcentaje = int(porcentaje) if porcentaje is not None else None
            except (TypeError, ValueError):
                porcentaje = None

            semaforo = datos.get('semaforo_id_semaforo')
            if semaforo is not None:
                try:
                    semaforo = int(semaforo)
                except (TypeError, ValueError):
                    semaforo = None

            if porcentaje is None and semaforo is None:
                calculado = None
            elif porcentaje is not None:
                if porcentaje >= 90:
                    calculado = 3
                elif porcentaje >= 11:
                    calculado = 2
                else:
                    calculado = 1
            else:
                calculado = semaforo

            if calculado is not None:
                datos['semaforo_id_semaforo'] = calculado

            sql = """
                UPDATE obra SET 
                    titulo_obra=%s, ubicacion_obra=%s, periodo_ejecucion=%s, 
                    fecha_inicio=%s, fecha_fin=%s, mediciones_obra=%s, valuaciones=%s, 
                    modificaciones_contrato=%s, certificaciones_obras_ejecutadas=%s, 
                    numero_contrato=%s, porcentaje_avance_obra=%s
                WHERE id_obra=%s AND estado=1
            """
            valores = (
                datos.get('titulo_obra'),
                datos.get('ubicacion_obra'),
                porcentaje,
                datos.get('fecha_inicio'),
                datos.get('fecha_fin'),
                datos.get('mediciones_obra'),
                datos.get('valuaciones'),
                datos.get('modificaciones_contrato'),
                datos.get('certificaciones_obras_ejecutadas'),
                datos.get('numero_contrato'),
                porcentaje,
                id_obra,
            )
            cursor.execute(sql, valores)
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[ObraModel.actualizar_obra] Error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def eliminar_obra(self, id_obra: int) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("UPDATE obra SET estado=0 WHERE id_obra=%s AND estado=1", (id_obra,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[ObraModel.eliminar_obra] Error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_obra_por_id(self, id_obra: int) -> dict | None:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return None
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM obra WHERE id_obra=%s AND estado=1", (id_obra,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[ObraModel.obtener_obra_por_id] Error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_avances_por_obra(self, id_obra: int) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT a.id_avance, a.porcentaje_avance, a.descripcion, a.gerente, a.fecha_avance
                FROM avance a
                WHERE a.obra_id_obra = %s AND a.estado = 1
                ORDER BY a.fecha_avance DESC
            """, (id_obra,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel.obtener_avances_por_obra] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
