from conexion.conexionBD import connectionBD

class ReportePDFModel:
    def __init__(self):
        pass

    def obtener_publicaciones_reporte(self, filtro=None):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT 
                    id_publicacion,
                    titulo_publicacion, 
                    autor_publicacion, 
                    DATE_FORMAT(fecha_publicacion, '%d/%m/%Y') AS fecha_formateada,
                    resumen_publicacion
                FROM tbl_publicaciones 
            """
            params = []
            if filtro:
                querySQL += " WHERE titulo_publicacion LIKE %s OR autor_publicacion LIKE %s OR resumen_publicacion LIKE %s"
                search = f"%{filtro}%"
                params = [search, search, search]
                
            querySQL += " ORDER BY fecha_publicacion DESC"
            cursor.execute(querySQL, params)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    def obtener_empleados(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT nombre_empleado, apellido_empleado, email_empleado, profesion_empleado 
                FROM tbl_empleados 
                ORDER BY id_empleado DESC
            """
            cursor.execute(querySQL)
            return cursor.fetchall()
        except:
            return []
        finally:
            cursor.close()
            conexion.close()

    def obtener_usuarios(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = "SELECT name_surname, email_user FROM users ORDER BY id DESC"
            cursor.execute(querySQL)
            return cursor.fetchall()
        except:
            return []
        finally:
            cursor.close()
            conexion.close()

    def obtener_solicitantes(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT nombre_solicitante, apellido_solicitante, cedula_solicitante 
                FROM tbl_solicitudes 
                ORDER BY id_solicitante DESC
            """
            cursor.execute(querySQL)
            return cursor.fetchall()
        except:
            return []
        finally:
            cursor.close()
            conexion.close()

    def obtener_contrataciones(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT nombre_empresa, rif_empresa 
                FROM tbl_contrataciones 
                ORDER BY id_contratacion DESC
            """
            cursor.execute(querySQL)
            return cursor.fetchall()
        except:
            return []
        finally:
            cursor.close()
            conexion.close()

    def obtener_obras(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT nombre_obra, ubicacion_obra, estado_obra 
                FROM tbl_obras 
                ORDER BY id_obra DESC
            """
            cursor.execute(querySQL)
            return cursor.fetchall()
        except:
            return []
        finally:
            cursor.close()
            conexion.close()