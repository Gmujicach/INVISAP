from conexion.conexionBD import connectionBD

class ReporteModel:
    def obtener_empleados_reporte(self, filtro=None):
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            querySQL = """
                SELECT 
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
        except Exception as e:
            print(f"Error en ReporteModel.obtener_empleados_reporte: {e}")
            return []
        finally:
            cursor.close()
            conexion.close()