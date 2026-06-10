from conexion.conexionBD import connectionBD_invilara

class GerenciaModel:
    def obtener_todas_las_gerencias(self):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM gerencias ORDER BY id_gerencias DESC")
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