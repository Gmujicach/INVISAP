from conexion.conexionBD import connectionBD_invilara

class PublicacionModel:
    def obtener_todas_las_publicaciones(self):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM gestionar_publicaciones ORDER BY fecha_publicacion DESC")
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
            sql = """INSERT INTO gestionar_publicaciones 
                     (titulo_publicacion, nombre_responsable, tipo_publicacion, fecha_publicacion) 
                     VALUES (%s, %s, %s, %s)"""
            valores = (data['titulo_publicacion'], data['nombre_responsable'], 
                       data['tipo_publicacion'], data['fecha_publicacion'])
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
            cursor.execute("SELECT * FROM gestionar_publicaciones WHERE id_publicaciones = %s", (id_publicacion,))
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
            sql = """UPDATE gestionar_publicaciones 
                     SET titulo_publicacion=%s, nombre_responsable=%s, tipo_publicacion=%s, fecha_publicacion=%s
                     WHERE id_publicaciones=%s"""
            valores = (data['titulo_publicacion'], data['nombre_responsable'], 
                       data['tipo_publicacion'], data['fecha_publicacion'], id_publicacion)
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
            cursor.execute("DELETE FROM gestionar_publicaciones WHERE id_publicaciones = %s", (id_publicacion,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en eliminar_publicacion: {e}")
            return 0
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()