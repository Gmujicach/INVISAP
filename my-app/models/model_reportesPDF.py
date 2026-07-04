from conexion.conexionBD import connectionBD, connectionBD_seguridad


class ReportePDFModel:
    def __init__(self):
        pass

    def _ejecutar_query(self, query, params=None, db_name=None):
        conexion = connectionBD_seguridad() if db_name == 'seguridad' else connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    def obtener_solicitudes(self, filtro=None):
        query = """
            SELECT 
                s.id_solicitudes,
                DATE_FORMAT(s.fecha, '%d/%m/%Y %H:%i') AS fecha,
                s.tipo_solicitud,
                s.estatus_solicitud,
                s.problematica,
                p.cedula_persona AS cedula,
                pr.rango_prioridad AS prioridad
            FROM solicitudes s
            JOIN persona p ON s.persona_id_persona = p.id_persona
            JOIN prioridad pr ON s.prioridad_id_gestion_prioridad = pr.id_gestion_prioridad
        """
        params = []
        if filtro:
            query += " WHERE s.tipo_solicitud LIKE %s OR s.estatus_solicitud LIKE %s OR s.problematica LIKE %s OR p.cedula_persona LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search, search]
        query += " ORDER BY s.fecha DESC"
        rows = self._ejecutar_query(query, params)
        return rows

    def obtener_solicitantes(self, filtro=None):
        query = """
            SELECT 
                pa.nombre,
                pa.apellido,
                p.cedula_persona AS cedula
            FROM particular pa
            JOIN persona p ON pa.persona_id_persona = p.id_persona
            JOIN solicitudes s ON s.persona_id_persona = p.id_persona
            GROUP BY pa.id_particular, pa.nombre, pa.apellido, p.cedula_persona
        """
        params = []
        if filtro:
            query += " HAVING pa.nombre LIKE %s OR pa.apellido LIKE %s OR p.cedula_persona LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search]
        query += " ORDER BY pa.nombre ASC"
        rows = self._ejecutar_query(query, params)
        return rows

    def obtener_empleados(self, filtro=None):
        query = """
            SELECT 
                e.nombre_empleado,
                e.cargo AS profesion_empleado,
                e.gerencia_asignada,
                DATE_FORMAT(e.fecha_ingreso, '%d/%m/%Y') AS fecha_ingreso,
                p.correo AS email_empleado,
                p.telefono AS telefono_empleado,
                CASE WHEN e.estado = 1 THEN 'Activo' ELSE 'Inactivo' END AS estado_empleado
            FROM empleados e
            JOIN persona p ON e.persona_id_persona = p.id_persona
        """
        params = []
        if filtro:
            query += " WHERE e.nombre_empleado LIKE %s OR e.cargo LIKE %s OR e.gerencia_asignada LIKE %s OR p.correo LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search, search]
        query += " ORDER BY e.nombre_empleado ASC"
        rows = self._ejecutar_query(query, params)
        return rows

    def obtener_usuarios(self, filtro=None):
        query = """
            SELECT 
                nombre,
                cedula_usuario,
                correo AS email,
                rol
            FROM usuarios
        """
        params = []
        if filtro:
            query += " WHERE nombre LIKE %s OR cedula_usuario LIKE %s OR correo LIKE %s OR rol LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search, search]
        query += " ORDER BY nombre ASC"
        rows = self._ejecutar_query(query, params, db_name='seguridad')
        return rows

    def obtener_contrataciones(self, filtro=None):
        query = """
            SELECT 
                c.empresa_ganadora AS nombre_empresa,
                c.empresa_rif AS rif_empresa,
                c.numero_contrato,
                c.monto,
                c.tipo_contrato,
                c.modalidad
            FROM contratacion c
        """
        params = []
        if filtro:
            query += " WHERE c.empresa_ganadora LIKE %s OR c.empresa_rif LIKE %s OR c.numero_contrato LIKE %s OR c.tipo_contrato LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search, search]
        query += " ORDER BY c.fecha_registro DESC"
        rows = self._ejecutar_query(query, params)
        return rows

    def obtener_obras(self, filtro=None):
        query = """
            SELECT 
                o.titulo_obra AS nombre_obra,
                o.ubicacion_obra,
                o.porcentaje_avance_obra,
                s.estado AS semaforo,
                s.color,
                c.empresa_ganadora AS contratista
            FROM obra o
            JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
            JOIN contratacion c ON o.contratacion_id_contratacion = c.id_contratacion
        """
        params = []
        if filtro:
            query += " WHERE o.titulo_obra LIKE %s OR o.ubicacion_obra LIKE %s OR s.estado LIKE %s OR c.empresa_ganadora LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search, search]
        query += " ORDER BY o.titulo_obra ASC"
        rows = self._ejecutar_query(query, params)
        return rows

    def obtener_publicaciones_reporte(self, filtro=None):
        query = """
            SELECT 
                titulo_publicacion, 
                nombre_responsable AS autor_publicacion, 
                DATE_FORMAT(fecha_publicacion, '%d/%m/%Y') AS fecha_formateada,
                tipo_publicacion
            FROM publicacion
        """
        params = []
        if filtro:
            query += " WHERE titulo_publicacion LIKE %s OR nombre_responsable LIKE %s OR cuerpo_publicacion LIKE %s"
            search = f"%{filtro}%"
            params = [search, search, search]
        query += " ORDER BY fecha_publicacion DESC"
        rows = self._ejecutar_query(query, params)
        return rows
