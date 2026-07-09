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

    def obtener_todas(self) -> list:
        return self._sql_obtener_todas()

    def registrar_obra(self, datos: dict) -> bool:
        return self._sql_insertar(datos)