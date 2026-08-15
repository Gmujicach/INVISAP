from conexion.conexionBD import connectionBD_invilara
from models.base_model import BaseModel


class PublicacionModel(BaseModel):
    def obtener_todas_las_publicaciones(self):
        try:
            conexion = connectionBD_invilara() # Asumiendo que esta es la conexión correcta a la base de datos de prueba completa
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM publicacion ORDER BY fecha_publicacion DESC")
            publicaciones = cursor.fetchall()
            return publicaciones
        except Exception as e:
            print(f"Error en obtener_todas_las_publicaciones: {e}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def registrar_publicacion(self, data):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT COALESCE(MAX(id_publicacion), 0) + 1 AS siguiente_id FROM publicacion")
            fila = cursor.fetchone()
            siguiente_id = fila[0] if fila else 1
            
            sql = """INSERT INTO publicacion 
                     (id_publicacion, titulo_publicacion, nombre_responsable, tipo_publicacion, fecha_publicacion, informe_avance_obra_id_informe, estado, cuerpo_publicacion)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            valores = (
                siguiente_id,
                data['titulo_publicacion'], 
                data['nombre_responsable'], 
                data['tipo_publicacion'], 
                data['fecha_publicacion'],
                data['informe_avance_obra_id_informe'],
                1,
                data.get('cuerpo_publicacion', 'Contenido pendiente')
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en registrar_publicacion: {e}")
            return 0
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def obtener_publicacion_por_id(self, id_publicacion):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT *, cuerpo_publicacion FROM publicacion WHERE id_publicacion = %s", (id_publicacion,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en obtener_publicacion_por_id: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def actualizar_publicacion(self, id_publicacion, data):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            # Ajustado a las columnas EXACTAS de invilara.sql
            sql = """UPDATE publicacion 
                     SET titulo_publicacion=%s, nombre_responsable=%s, tipo_publicacion=%s, informe_avance_obra_id_informe=%s, cuerpo_publicacion=%s
                     WHERE id_publicacion=%s"""
            valores = (
                data['titulo_publicacion'], 
                data['nombre_responsable'], 
                data['tipo_publicacion'], 
                data['informe_avance_obra_id_informe'], 
                data.get('cuerpo_publicacion', 'Contenido pendiente'),
                id_publicacion
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en actualizar_publicacion: {e}")
            return 0
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
    def eliminar_publicacion(self, id_publicacion):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM publicacion WHERE id_publicacion = %s", (id_publicacion,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en eliminar_publicacion: {e}")
            return 0
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def obtener_informes_para_publicaciones(self):
        """Obtiene los informes de avance de obra para vincularlos a publicaciones."""
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            # Seleccionamos el ID y el tipo como etiqueta para el select
            cursor.execute("SELECT id_informe, tipo_informe AS nombre_proyecto FROM informe_avance_obra")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_informes_para_publicaciones: {e}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def validar_informe_activo(self, id_informe):
        """Verifica si un informe existe en la base de datos."""
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM informe_avance_obra WHERE id_informe = %s", (id_informe,))
            result = cursor.fetchone()
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"Error en validar_informe_activo: {e}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()