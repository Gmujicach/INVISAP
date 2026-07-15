from conexion.conexionBD import connectionBD_invilara

class GerenciaModel:
    def __init__(self):
        self._asegurar_tabla_gerencias()

    def _asegurar_tabla_gerencias(self):
        try:
            conn = connectionBD_invilara()
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS `gerencias` (
                            `id_gerencias` int NOT NULL AUTO_INCREMENT,
                            `nombre_gerencia` varchar(100) NOT NULL,
                            `direccion_gerencia` varchar(100) NOT NULL,
                            `informe_avance_obra_id_informe` int NOT NULL,
                            PRIMARY KEY (`id_gerencias`)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                    """)
                    conn.commit()
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla gerencias: {e}")

    def obtener_todas_las_gerencias(self):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT g.*, i.tipo_obras 
                FROM gerencias g
                INNER JOIN informe_avance_obra i ON g.informe_avance_obra_id_informe = i.id_informe
                ORDER BY g.id_gerencias DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener gerencias: {e}")
            return []
        finally:
            if conexion: conexion.close()

    def registrar_gerencias(self, datos):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            sql = "INSERT INTO gerencias (nombre_gerencia, direccion_gerencia, informe_avance_obra_id_informe) VALUES (%s, %s, %s)"
            valores = (
                datos['nombre_gerencia'], 
                datos['direccion_gerencia'], 
                datos['informe_avance_obra_id_informe']
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error fatal en el modelo al insertar: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_informes_disponibles(self):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_informe, tipo_informe FROM informe_avance_obra")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener informes: {e}")
            return []
        finally:
            if conexion: conexion.close()


    def update_gerencia(self, datos):
        conexion = None  # <-- Esto faltaba para evitar errores si falla la conexión
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            sql = """UPDATE gerencias 
                     SET nombre_gerencia = %s, 
                         direccion_gerencia = %s, 
                         informe_avance_obra_id_informe = %s 
                     WHERE id_gerencias = %s"""
            cursor.execute(sql, (
                datos['nombre_gerencia'], 
                datos['direccion_gerencia'], 
                datos['informe_avance_obra_id_informe'], 
                datos['id_gerencias']
            ))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_gerencia(self, id_gerencia):
        # La siguiente línea debe tener 8 espacios de sangría
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            sql = "DELETE FROM gerencias WHERE id_gerencias = %s"
            cursor.execute(sql, (id_gerencia,))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar: {e}")
            return False
        finally:
            if conexion: conexion.close()