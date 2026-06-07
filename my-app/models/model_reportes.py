from conexion.conexionBD import connectionBD

class ReporteModel:
    def __init__(self):
        pass

    def obtener_empleados_reporte(self, filtro=None):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT 
                    e.id_empleado,
                    e.nombre_empleado, 
                    e.apellido_empleado,
                    CASE
                        WHEN e.sexo_empleado = 1 THEN 'Masculino'
                        ELSE 'Femenino'
                    END AS sexo_empleado,
                    e.telefono_empleado, 
                    e.email_empleado,
                    e.profesion_empleado,
                    e.salario_empleado,
                    DATE_FORMAT(e.fecha_registro, '%d de %b %Y %h:%i %p') AS fecha_registro
                FROM tbl_empleados AS e
            """
            params = []
            if filtro:
                querySQL += " WHERE e.nombre_empleado LIKE %s OR e.apellido_empleado LIKE %s OR e.profesion_empleado LIKE %s"
                search = f"%{filtro}%"
                params = [search, search, search]
                
            querySQL += " ORDER BY e.id_empleado DESC"
            cursor.execute(querySQL, params)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    def obtener_publicaciones_reporte(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            querySQL = """
                SELECT 
                    titulo_publicacion, 
                    autor_publicacion, 
                    DATE_FORMAT(fecha_publicacion, '%d/%m/%Y') AS fecha_formateada,
                    resumen_publicacion
                FROM tbl_publicaciones 
                ORDER BY fecha_publicacion DESC
            """
            cursor.execute(querySQL)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_generales(self):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            stats = {}
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN sexo_empleado = 1 THEN 1 ELSE 0 END) as hombres,
                    SUM(CASE WHEN sexo_empleado = 2 THEN 1 ELSE 0 END) as mujeres,
                    COUNT(*) as total
                FROM tbl_empleados
            """)
            stats['empleados'] = cursor.fetchone()
            cursor.execute("SELECT AVG(salario_empleado) as promedio_salarial FROM tbl_empleados")
            res_salario = cursor.fetchone()
            stats['promedio_salarial'] = res_salario['promedio_salarial'] if res_salario else 0
            cursor.execute("SELECT COUNT(*) as total_pub FROM tbl_publicaciones")
            res_pub = cursor.fetchone()
            stats['publicaciones'] = res_pub['total_pub'] if res_pub else 0
            return stats
        finally:
            cursor.close()
            conexion.close()