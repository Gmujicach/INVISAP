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