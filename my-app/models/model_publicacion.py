import re
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara

class PublicacionModel:
    def __init__(self, titulo=None, responsable=None, tipo=None, id_informe=None, id_publicacion=None):
        self.__id_publicacion = id_publicacion
        self.__titulo = titulo
        self.__responsable = responsable
        self.__tipo = tipo
        self.__id_informe = id_informe
        self.__estado = 1
        self.__regex_titulo = r"^[a-zA-Z0-9\sÁÉÍÓÚáéíóúñÑ.,-]{5,150}$"
        self.__regex_nombre = r"^[a-zA-Z\sÁÉÍÓÚáéíóúñÑ]{3,45}$"

    # Getters y Setters con validaciones Regex
    @property
    def titulo(self): return self.__titulo
    
    @titulo.setter
    def titulo(self, value):
        if not re.match(self.__regex_titulo, value):
            raise ValueError("El título no cumple con el formato o longitud (5-150 caracteres).")
        self.__titulo = value

    @property
    def responsable(self): return self.__responsable
    
    @responsable.setter
    def responsable(self, value):
        if not re.match(self.__regex_nombre, value):
            raise ValueError("El nombre del responsable es inválido.")
        self.__responsable = value

    @property
    def tipo(self): return self.__tipo
    @tipo.setter
    def tipo(self, v): self.__tipo = v

    @property
    def id_informe(self): return self.__id_informe
    @id_informe.setter
    def id_informe(self, v): self.__id_informe = v

    # Métodos Públicos (Capa de Seguridad)
    def obtener_todas_las_publicaciones(self):
        return self.__obtener_publicaciones_db()

    def obtener_publicacion_por_id(self, id_pub):
        return self.__obtener_por_id_db(id_pub)

    def obtener_informes_para_publicaciones(self):
        return self.__obtener_informes_db()

    def guardar(self):
        return self.__registrar_db()

    def actualizar(self):
        return self.__actualizar_db()

    def eliminar(self):
        return self.__borrado_logico_db()

    def validar_informe_activo(self, id_informe):
        return self.__verificar_existencia_informe(id_informe)

    def obtener_todas(self):
        return self.__obtener_publicaciones_db()

    def obtener_por_id(self, id_pub):
        return self.__obtener_por_id_db(id_pub)

    # Métodos Privados de Persistencia
    def __obtener_publicaciones_db(self):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            # Solo traemos las que tienen estado 1 (Borrado Lógico)
            sql = """SELECT id_publicacion, titulo_publicacion, 
                            autor_publicacion AS nombre_responsable, tipo_publicacion, 
                            fecha_publicacion, evidencias AS id_informe, estado 
                     FROM publicacion WHERE estado = 1 ORDER BY fecha_publicacion DESC"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    def __obtener_informes_db(self):
        """Consulta los informes de avance de obra en la BD invilara."""
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            # Se usa el alias 'nombre_proyecto' para compatibilidad con la vista
            sql = "SELECT id_informe, tipo_informe AS nombre_proyecto FROM informe_avance_obra"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener informes: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    def __obtener_por_id_db(self, id_pub):
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            sql = """SELECT id_publicacion, titulo_publicacion, 
                            autor_publicacion AS nombre_responsable, tipo_publicacion, 
                            fecha_publicacion, evidencias AS id_informe, estado 
                     FROM publicacion WHERE id_publicacion = %s AND estado = 1"""
            cursor.execute(sql, (id_pub,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener publicación por ID: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    def __actualizar_db(self):
        conexion = None
        cursor = None
        try:
            # Asegurar que el id_informe sea un entero o None (NULL en SQL)
            id_inf_val = int(self.__id_informe) if str(self.__id_informe).isdigit() else None

            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            sql = """UPDATE publicacion SET 
                     titulo_publicacion = %s, autor_publicacion = %s, 
                     tipo_publicacion = %s, evidencias = %s 
                     WHERE id_publicacion = %s"""
            valores = (self.__titulo, self.__responsable, self.__tipo, 
                       id_inf_val, self.__id_publicacion)
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar publicación: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    # Métodos Privados de Persistencia
    def __registrar_db(self):
        conexion = None
        cursor = None
        try:
            # Asegurar que el id_informe sea un entero o None (NULL en SQL)
            id_inf_val = int(self.__id_informe) if str(self.__id_informe).isdigit() else None
            
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            # Se añade cuerpo_publicacion con valor por defecto para evitar errores de integridad
            sql = """INSERT INTO publicacion 
                     (titulo_publicacion, autor_publicacion, tipo_publicacion, 
                      fecha_publicacion, evidencias, estado, cuerpo_publicacion) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            valores = (self.__titulo, self.__responsable, self.__tipo, 
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                       id_inf_val, 1, 'Contenido pendiente')
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error crítico al registrar publicación: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    def __borrado_logico_db(self):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            sql = "UPDATE publicacion SET estado = 0 WHERE id_publicacion = %s"
            cursor.execute(sql, (self.__id_publicacion,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    def __verificar_existencia_informe(self, id_informe):
        """Valida en tiempo real que el informe asociado exista."""
        if id_informe is None or str(id_informe).strip() in ['', 'None', '0', 'null']:
            print(f"DEBUG: id_informe inválido recibido: {id_informe}")
            return False
            
        val_id = str(id_informe).strip()
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            if not conexion:
                return False
            cursor = conexion.cursor()
            sql = "SELECT id_informe FROM informe_avance_obra WHERE id_informe = %s LIMIT 1"
            cursor.execute(sql, (val_id,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error al verificar existencia de informe: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()