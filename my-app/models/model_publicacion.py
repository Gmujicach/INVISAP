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
        self.__cuerpo = 'Contenido pendiente'
        self.__estado = 1
        self.__regex_titulo = r"^[a-zA-Z0-9\sÁÉÍÓÚáéíóúñÑ.,-]{5,150}$"
        self.__regex_nombre = r"^[a-zA-Z\sÁÉÍÓÚáéíóúñÑ]{3,45}$"
        self.__asegurar_tabla_publicacion()

    def __asegurar_tabla_publicacion(self):
        try:
            conn = connectionBD_invilara()
            if conn:
                cur = conn.cursor()
                try:
                    cur.execute("SHOW COLUMNS FROM publicacion LIKE 'cuerpo_publicacion'")
                    if not cur.fetchone():
                        cur.execute("ALTER TABLE publicacion ADD COLUMN cuerpo_publicacion TEXT")
                        conn.commit()
                        print("[DB] Columna 'cuerpo_publicacion' agregada a tabla publicacion")
                except Exception as e:
                    print(f"[DB] Error al verificar tabla: {e}")
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla: {e}")

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
        if value and not re.match(self.__regex_nombre, value):
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

    @property
    def cuerpo(self): return self.__cuerpo
    @cuerpo.setter
    def cuerpo(self, v): self.__cuerpo = v or 'Contenido pendiente'

    def obtener_todas_las_publicaciones(self):
        return self.__obtener_publicaciones_db()

    def registrar_publicacion(self, data):
        try:
            self.titulo = data.get('titulo_publicacion')
            self.responsable = data.get('nombre_responsable') or data.get('autor_publicacion')
            self.tipo = data.get('tipo_publicacion', 'General')
            self.__id_informe = data.get('informe_avance_obra_id_informe') or data.get('id_informe') or data.get('evidencias')
            self.cuerpo = data.get('cuerpo_publicacion', 'Contenido pendiente')
            return 1 if self.__registrar_db() else 0
        except Exception as e:
            print(f"Error en registrar_publicacion: {e}")
            return 0

    def actualizar_publicacion(self, id_publicacion, data):
        try:
            self.__id_publicacion = id_publicacion
            self.titulo = data.get('titulo_publicacion')
            self.responsable = data.get('nombre_responsable') or data.get('autor_publicacion')
            self.tipo = data.get('tipo_publicacion', 'General')
            self.__id_informe = data.get('informe_avance_obra_id_informe') or data.get('id_informe') or data.get('evidencias')
            self.cuerpo = data.get('cuerpo_publicacion', 'Contenido pendiente')
            return self.__actualizar_db()
        except Exception as e:
            print(f"Error en actualizar_publicacion: {e}")
            return False

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

    def __obtener_publicaciones_db(self):
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            sql = """SELECT id_publicacion, titulo_publicacion, 
                            nombre_responsable, tipo_publicacion, 
                            fecha_publicacion, informe_avance_obra_id_informe AS id_informe, estado, cuerpo_publicacion
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
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
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
                            nombre_responsable, tipo_publicacion, 
                            fecha_publicacion, informe_avance_obra_id_informe AS id_informe, 
                            estado, cuerpo_publicacion
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
            id_inf_val = int(self.__id_informe) if self.__id_informe and str(self.__id_informe).isdigit() else None
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            sql = """UPDATE publicacion SET 
                     titulo_publicacion = %s, nombre_responsable = %s, 
                     tipo_publicacion = %s, informe_avance_obra_id_informe = %s, cuerpo_publicacion = %s
                     WHERE id_publicacion = %s"""
            valores = (self.__titulo, self.__responsable, self.__tipo, 
                       id_inf_val, self.__cuerpo, self.__id_publicacion)
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar publicación: {e}")
            return False
        finally:
            if cursor: cursor.close()
            if conexion: conexion.close()

    def __registrar_db(self):
        conexion = None
        cursor = None
        try:
            id_inf_val = int(self.__id_informe) if self.__id_informe and str(self.__id_informe).isdigit() else None
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            
            cursor.execute("SELECT COALESCE(MAX(id_publicacion), 0) + 1 AS siguiente_id FROM publicacion")
            fila = cursor.fetchone()
            siguiente_id = fila[0] if fila else 1
            
            sql = """INSERT INTO publicacion 
                     (id_publicacion, titulo_publicacion, nombre_responsable, tipo_publicacion, 
                      fecha_publicacion, informe_avance_obra_id_informe, estado, cuerpo_publicacion) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            valores = (siguiente_id, self.__titulo, self.__responsable, self.__tipo, 
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                       id_inf_val, 1, self.__cuerpo)
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