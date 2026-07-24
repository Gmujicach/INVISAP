from conexion.conexionBD import connectionBD, connectionBD_seguridad


class ReporteExcelModel:
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

    def _aplicar_filtros(self, where_clauses, params, filtros, mapeo_columnas=None):
        mapeo = mapeo_columnas or {}
        if not filtros:
            return
        for key, val in filtros.items():
            if not val and val != 0:
                continue
            columna = mapeo.get(key, key)
            if key == 'nombre_solicitante':
                where_clauses.append("(COALESCE(part.nombre, inst.razon_social, com.nombre_comunidad) LIKE %s)")
                params.append(f"%{val}%")
            elif key.startswith('fecha_') and key.endswith('_desde'):
                where_clauses.append(f"DATE({columna}) >= %s")
                params.append(val)
            elif key.startswith('fecha_') and key.endswith('_hasta'):
                where_clauses.append(f"DATE({columna}) <= %s")
                params.append(val)
            elif key == 'estado':
                if val in ('0', '1'):
                    where_clauses.append(f"{columna} = %s")
                    params.append(int(val))
            elif key == 'porcentaje_avance_min':
                where_clauses.append(f"{columna.replace('_min', '')} >= %s")
                params.append(val)
            elif key == 'porcentaje_avance_max':
                where_clauses.append(f"{columna.replace('_max', '')} <= %s")
                params.append(val)
            elif key == 'sector':
                where_clauses.append("com.sector LIKE %s")
                params.append(f"%{val}%")
            elif key == 'ambito':
                where_clauses.append("com.ambito LIKE %s")
                params.append(f"%{val}%")
            elif key == 'titulo_obra':
                where_clauses.append("o.titulo_obra LIKE %s")
                params.append(f"%{val}%")
            else:
                where_clauses.append(f"{columna} LIKE %s")
                params.append(f"%{val}%")

    def obtener_solicitudes_reporte(self, filtros=None):
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
            LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
            LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
            LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
            JOIN prioridad pr ON s.prioridad_id_gestion_prioridad = pr.id_gestion_prioridad
            WHERE s.estado = 1
        """
        params = []
        where = []
        mapeo = {
            'tipo_solicitud': 's.tipo_solicitud',
            'estatus_solicitud': 's.estatus_solicitud',
            'problematica': 's.problematica',
            'cedula': 'p.cedula_persona',
            'fecha_desde': 's.fecha',
            'fecha_hasta': 's.fecha',
            'municipio': 'p.municipio',
            'parroquia': 'p.parroquia',
            'direccion': 'p.direccion',
            'telefono': 'p.telefono',
            'correo': 'p.correo',
            'sector': 'com.sector',
            'ambito': 'com.ambito',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " ORDER BY s.fecha DESC"
        return self._ejecutar_query(query, params)

    def obtener_solicitantes_reporte(self, filtros=None):
        query = """
            SELECT 
                pa.nombre,
                pa.apellido,
                p.cedula_persona AS cedula
            FROM particular pa
            JOIN persona p ON pa.persona_id_persona = p.id_persona
            JOIN solicitudes s ON s.persona_id_persona = p.id_persona
            WHERE pa.estado = 1
        """
        params = []
        where = []
        mapeo = {
            'nombre': 'pa.nombre',
            'apellido': 'pa.apellido',
            'cedula': 'p.cedula_persona',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " GROUP BY pa.id_particular, pa.nombre, pa.apellido, p.cedula_persona ORDER BY pa.nombre ASC"
        return self._ejecutar_query(query, params)

    def obtener_empleados_reporte(self, filtros=None):
        query = """
            SELECT 
                e.nombre_empleado,
                e.cargo AS profesion_empleado,
                e.gerencia_asignada,
                DATE_FORMAT(e.fecha_ingreso, '%d/%m/%Y') AS fecha_ingreso,
                p.correo AS email_empleado,
                p.telefono AS telefono_empleado,
                'Activo' AS estado_empleado
            FROM empleados e
            JOIN persona p ON e.persona_id_persona = p.id_persona
            WHERE e.estado = 1
        """
        params = []
        where = []
        mapeo = {
            'nombre_empleado': 'e.nombre_empleado',
            'cargo': 'e.cargo',
            'fecha_ingreso_desde': 'e.fecha_ingreso',
            'fecha_ingreso_hasta': 'e.fecha_ingreso',
            'estado_empleado': 'e.estado',
            'cedula_persona': 'p.cedula_persona',
            'telefono': 'p.telefono',
            'correo': 'p.correo',
            'direccion': 'p.direccion',
            'parroquia': 'p.parroquia',
            'municipio': 'p.municipio',
            'gerencia_asignada': 'e.gerencia_asignada',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " ORDER BY e.nombre_empleado ASC"
        return self._ejecutar_query(query, params)

    def obtener_usuarios_reporte(self, filtros=None):
        query = """
            SELECT 
                nombre,
                cedula_usuario,
                correo,
                rol
            FROM usuarios
            WHERE estado = 1
        """
        params = []
        where = []
        mapeo = {
            'nombre': 'nombre',
            'cedula_usuario': 'cedula_usuario',
            'correo': 'correo',
            'rol': 'rol',
            'estado': 'estado',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " ORDER BY nombre ASC"
        return self._ejecutar_query(query, params, db_name='seguridad')

    def obtener_contrataciones_reporte(self, filtros=None):
        query = """
            SELECT 
                c.empresa_ganadora AS nombre_empresa,
                c.empresa_rif AS rif_empresa,
                c.numero_contrato,
                c.monto,
                c.descripcion,
                c.observacion,
                c.tipo_contrato,
                c.modalidad,
                c.objeto,
                DATE_FORMAT(c.fecha_registro, '%d/%m/%Y') AS fecha_registro,
                DATE_FORMAT(c.fecha_inicio_procedimiento, '%d/%m/%Y') AS fecha_inicio,
                DATE_FORMAT(c.fecha_adjudicacion, '%d/%m/%Y') AS fecha_adjudicacion
            FROM contratacion c
            WHERE c.estado = 1
        """
        params = []
        where = []
        mapeo = {
            'empresa_ganadora': 'c.empresa_ganadora',
            'tipo_contrato': 'c.tipo_contrato',
            'modalidad': 'c.modalidad',
            'objeto': 'c.objeto',
            'fecha_registro_desde': 'c.fecha_registro',
            'fecha_registro_hasta': 'c.fecha_registro',
            'fecha_inicio_procedimiento_desde': 'c.fecha_inicio_procedimiento',
            'fecha_inicio_procedimiento_hasta': 'c.fecha_inicio_procedimiento',
            'fecha_adjudicacion_desde': 'c.fecha_adjudicacion',
            'fecha_adjudicacion_hasta': 'c.fecha_adjudicacion',
            'numero_contrato': 'c.numero_contrato',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " ORDER BY c.fecha_registro DESC"
        return self._ejecutar_query(query, params)

    def obtener_obras_reporte(self, filtros=None):
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
            WHERE o.estado = 1
        """
        params = []
        where = []
        mapeo = {
            'titulo_obra': 'o.titulo_obra',
            'ubicacion_obra': 'o.ubicacion_obra',
            'fecha_inicio_desde': 'o.fecha_inicio',
            'fecha_inicio_hasta': 'o.fecha_inicio',
            'fecha_fin_desde': 'o.fecha_fin',
            'fecha_fin_hasta': 'o.fecha_fin',
            'semaforo_estado': 's.estado',
            'contratista': 'c.empresa_ganadora',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " ORDER BY o.titulo_obra ASC"
        return self._ejecutar_query(query, params)

    def obtener_publicaciones_reporte(self, filtros=None):
        query = """
            SELECT 
                titulo_publicacion, 
                nombre_responsable AS autor_publicacion, 
                DATE_FORMAT(fecha_publicacion, '%d/%m/%Y') AS fecha_formateada,
                tipo_publicacion
            FROM publicacion
            WHERE estado = 1
        """
        params = []
        where = []
        mapeo = {
            'titulo_publicacion': 'titulo_publicacion',
            'nombre_responsable': 'nombre_responsable',
            'tipo_publicacion': 'tipo_publicacion',
            'fecha_publicacion_desde': 'fecha_publicacion',
            'fecha_publicacion_hasta': 'fecha_publicacion',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        if where:
            query += " AND " + " AND ".join(where)
        query += " ORDER BY fecha_publicacion DESC"
        return self._ejecutar_query(query, params)

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
                WHERE estado = 1
            """)
            stats['empleados'] = cursor.fetchone()
            
            cursor.execute("SELECT AVG(salario_empleado) as promedio_salarial FROM tbl_empleados WHERE estado = 1")
            res_salario = cursor.fetchone()
            stats['promedio_salarial'] = res_salario['promedio_salarial'] if res_salario else 0
            
            cursor.execute("SELECT COUNT(*) as total_pub FROM tbl_publicaciones WHERE estado = 1")
            res_pub = cursor.fetchone()
            stats['publicaciones'] = res_pub['total_pub'] if res_pub else 0
            
            return stats
        finally:
            cursor.close()
            conexion.close()
