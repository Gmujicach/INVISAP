from conexion.conexionBD import connectionBD


class ReporteEstadisticoModel:
    def __init__(self):
        pass

    def obtener_estadisticas_solicitudes(self, filtro=None):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            stats = {}

            cursor.execute("""
                SELECT tipo_solicitud as label, COUNT(*) as valor 
                FROM solicitudes 
                GROUP BY tipo_solicitud
            """)
            stats['por_tipo'] = cursor.fetchall()

            cursor.execute("""
                SELECT estatus_solicitud as label, COUNT(*) as valor 
                FROM solicitudes 
                GROUP BY estatus_solicitud
            """)
            stats['por_estatus'] = cursor.fetchall()

            query_fecha = """
                SELECT DATE(fecha) as label, COUNT(*) as valor 
                FROM solicitudes 
            """
            params = []
            if filtro:
                query_fecha += " WHERE tipo_solicitud LIKE %s OR estatus_solicitud LIKE %s"
                search = f"%{filtro}%"
                params = [search, search]
            query_fecha += " GROUP BY DATE(fecha) ORDER BY label ASC"
            cursor.execute(query_fecha, params)
            stats['por_fecha'] = cursor.fetchall()

            return stats
        finally:
            cursor.close()
            conexion.close()
