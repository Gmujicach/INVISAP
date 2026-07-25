from conexion.conexionBD import connectionBD


class ReporteEstadisticoModel:
    def __init__(self):
        pass

    def _ejecutar_query(self, query, params=None):
        conexion = connectionBD()
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
            if key in ('tipo_reporte', 'agrupacion'):
                continue
            columna = mapeo.get(key, key)
            if key == 'correo_dominio':
                where_clauses.append(f"{columna} LIKE %s")
                params.append(f"%{val}%")
            elif key.startswith('fecha_') and key.endswith('_desde'):
                where_clauses.append(f"DATE({columna}) >= %s")
                params.append(val)
            elif key.startswith('fecha_') and key.endswith('_hasta'):
                where_clauses.append(f"DATE({columna}) <= %s")
                params.append(val)
            elif key == 'porcentaje_avance_min':
                where_clauses.append(f"o.porcentaje_avance_obra >= %s")
                params.append(val)
            elif key == 'porcentaje_avance_max':
                where_clauses.append(f"o.porcentaje_avance_obra <= %s")
                params.append(val)
            elif key == 'sector':
                where_clauses.append("com.sector LIKE %s")
                params.append(f"%{val}%")
            elif key == 'ambito':
                where_clauses.append("com.ambito LIKE %s")
                params.append(f"%{val}%")
            elif key == 'estado':
                if val in ('0', '1'):
                    where_clauses.append(f"{columna} = %s")
                    params.append(int(val) if val in ('0', '1') else val)
                else:
                    where_clauses.append(f"{columna} LIKE %s")
                    params.append(f"%{val}%")
            else:
                where_clauses.append(f"{columna} LIKE %s")
                params.append(f"%{val}%")

    def obtener_estadisticas_solicitudes(self, filtros=None, agrupacion='dia'):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        params = []
        where = ["s.estado = 1", "p.estado = 1"]
        mapeo = {
            'tipo_solicitud': 's.tipo_solicitud',
            'estatus_solicitud': 's.estatus_solicitud',
            'problematica': 's.problematica',
            'cedula': 'p.cedula_persona',
            'nombre_solicitante': 'COALESCE(part.nombre, inst.razon_social, com.nombre_comunidad)',
            'fecha_desde': 's.fecha',
            'fecha_hasta': 's.fecha',
            'municipio': 'p.municipio',
            'parroquia': 'p.parroquia',
            'direccion': 'p.direccion',
            'telefono': 'p.telefono',
            'correo': 'p.correo',
            'correo_dominio': 'p.correo',
            'sector': 'com.sector',
            'ambito': 'com.ambito',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        where_sql = "WHERE " + " AND ".join(where)

        try:
            stats = {}

            if agrupacion == 'mes':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(s.fecha, '%Y-%m') as label, COUNT(*) as valor 
                    FROM solicitudes s
                    JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                    LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    {where_sql}
                    GROUP BY DATE_FORMAT(s.fecha, '%Y-%m') ORDER BY label ASC
                """, params)
                stats['por_mes'] = cursor.fetchall()
            elif agrupacion == 'semana':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(s.fecha, '%x-W%v') as label, COUNT(*) as valor 
                    FROM solicitudes s
                    JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                    LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    {where_sql}
                    GROUP BY DATE_FORMAT(s.fecha, '%x-W%v') ORDER BY label ASC
                """, params)
                stats['por_semana'] = cursor.fetchall()
            else:
                cursor.execute(f"""
                    SELECT DATE(s.fecha) as label, COUNT(*) as valor 
                    FROM solicitudes s
                    JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                    LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    {where_sql}
                    GROUP BY DATE(s.fecha) ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT s.tipo_solicitud as label, COUNT(*) as valor 
                FROM solicitudes s
                JOIN persona p ON s.persona_id_persona = p.id_persona
                LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                {where_sql}
                GROUP BY s.tipo_solicitud
            """, params)
            stats['por_tipo'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT s.estatus_solicitud as label, COUNT(*) as valor 
                FROM solicitudes s
                JOIN persona p ON s.persona_id_persona = p.id_persona
                LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                {where_sql}
                GROUP BY s.estatus_solicitud
            """, params)
            stats['por_estatus'] = cursor.fetchall()

            if filtros and any(k in filtros for k in ['municipio', 'parroquia', 'cedula', 'direccion', 'telefono', 'correo', 'sector', 'ambito']):
                cursor.execute(f"""
                    SELECT p.municipio as label, COUNT(*) as valor
                    FROM solicitudes s
                    JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                    LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    {where_sql}
                    GROUP BY p.municipio
                """, params)
                stats['por_municipio'] = cursor.fetchall()

                cursor.execute(f"""
                    SELECT p.parroquia as label, COUNT(*) as valor
                    FROM solicitudes s
                    JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                    LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    {where_sql}
                    GROUP BY p.parroquia
                """, params)
                stats['por_parroquia'] = cursor.fetchall()

                cursor.execute(f"""
                    SELECT com.sector as label, COUNT(*) as valor
                    FROM solicitudes s
                    JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                    LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    {where_sql} AND com.sector IS NOT NULL AND com.sector != ''
                    GROUP BY com.sector
                """, params)
                stats['por_sector'] = cursor.fetchall()

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_obras(self, filtros=None, agrupacion='dia'):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        params = []
        where = ["o.estado = 1"]
        mapeo = {
            'titulo_obra': 'o.titulo_obra',
            'ubicacion_obra': 'o.ubicacion_obra',
            'fecha_inicio_desde': 'o.fecha_inicio',
            'fecha_inicio_hasta': 'o.fecha_inicio',
            'fecha_fin_desde': 'o.fecha_fin',
            'fecha_fin_hasta': 'o.fecha_fin',
            'semaforo_estado': 's.estado',
            'contratista': 'c.empresa_ganadora',
            'criticidad': 'g.criticidad',
            'nivel_gravedad': 'g.nivel_gravedad',
            'gerente': 'e.nombre_empleado',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        where_sql = "WHERE " + " AND ".join(where)

        try:
            stats = {}

            if agrupacion == 'mes':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%Y-%m') as label, COUNT(*) as valor
                    FROM obra o
                    JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                    JOIN contratacion c ON o.contratacion_id_contratacion = c.id_contratacion
                    LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                    LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                    LEFT JOIN empleados e ON e.id_empleados = a.gerente
                    {where_sql}
                    GROUP BY DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%Y-%m') ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()
            elif agrupacion == 'semana':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%x-W%v') as label, COUNT(*) as valor
                    FROM obra o
                    JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                    JOIN contratacion c ON o.contratacion_id_contratacion = c.id_contratacion
                    LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                    LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                    LEFT JOIN empleados e ON e.id_empleados = a.gerente
                    {where_sql}
                    GROUP BY DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%x-W%v') ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()
            else:
                cursor.execute(f"""
                    SELECT DATE(COALESCE(o.fecha_inicio, o.fecha_fin)) as label, COUNT(*) as valor
                    FROM obra o
                    JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                    JOIN contratacion c ON o.contratacion_id_contratacion = c.id_contratacion
                    LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                    LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                    LEFT JOIN empleados e ON e.id_empleados = a.gerente
                    {where_sql}
                    GROUP BY DATE(COALESCE(o.fecha_inicio, o.fecha_fin)) ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT s.estado as label, COUNT(*) as valor
                FROM obra o
                JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                LEFT JOIN empleados e ON e.id_empleados = a.gerente
                {where_sql}
                GROUP BY s.estado
            """, params)
            stats['por_estado'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT c.empresa_ganadora as label, COUNT(*) as valor
                FROM obra o
                JOIN contratacion c ON o.contratacion_id_contratacion = c.id_contratacion
                LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                LEFT JOIN empleados e ON e.id_empleados = a.gerente
                {where_sql}
                GROUP BY c.empresa_ganadora
            """, params)
            stats['por_contratista'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT o.ubicacion_obra as label, COUNT(*) as valor
                FROM obra o
                LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                LEFT JOIN empleados e ON e.id_empleados = a.gerente
                {where_sql}
                GROUP BY o.ubicacion_obra
            """, params)
            stats['por_ubicacion'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT s.color as label, COUNT(*) as valor
                FROM obra o
                JOIN semaforo s ON o.semaforo_id_semaforo = s.id_semaforo
                LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                LEFT JOIN empleados e ON e.id_empleados = a.gerente
                {where_sql}
                GROUP BY s.color
            """, params)
            stats['por_semaforo_color'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT CASE
                    WHEN o.porcentaje_avance_obra < 25 THEN '0-25%'
                    WHEN o.porcentaje_avance_obra < 50 THEN '25-50%'
                    WHEN o.porcentaje_avance_obra < 75 THEN '50-75%'
                    ELSE '75-100%'
                END as label, COUNT(*) as valor
                FROM obra o
                LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                LEFT JOIN empleados e ON e.id_empleados = a.gerente
                {where_sql}
                GROUP BY label
            """, params)
            stats['por_avance'] = cursor.fetchall()

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_empleados(self, filtros=None, agrupacion='dia'):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        params = []
        where = ["e.estado = 1"]
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
        where_sql = "WHERE " + " AND ".join(where)

        try:
            stats = {}

            cursor.execute(f"""
                SELECT e.cargo as label, COUNT(*) as valor
                FROM empleados e
                {where_sql}
                GROUP BY e.cargo
            """, params)
            stats['por_cargo'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT e.gerencia_asignada as label, COUNT(*) as valor
                FROM empleados e
                {where_sql}
                GROUP BY e.gerencia_asignada
            """, params)
            stats['por_gerencia'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT e.estado as label, COUNT(*) as valor
                FROM empleados e
                {where_sql}
                GROUP BY e.estado
            """, params)
            stats['por_estado'] = cursor.fetchall()

            if agrupacion == 'mes':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(e.fecha_ingreso, '%Y-%m') as label, COUNT(*) as valor
                    FROM empleados e
                    {where_sql}
                    GROUP BY DATE_FORMAT(e.fecha_ingreso, '%Y-%m') ORDER BY label ASC
                """, params)
                stats['por_fecha_ingreso'] = cursor.fetchall()
            elif agrupacion == 'semana':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(e.fecha_ingreso, '%x-W%v') as label, COUNT(*) as valor
                    FROM empleados e
                    {where_sql}
                    GROUP BY DATE_FORMAT(e.fecha_ingreso, '%x-W%v') ORDER BY label ASC
                """, params)
                stats['por_fecha_ingreso'] = cursor.fetchall()
            else:
                cursor.execute(f"""
                    SELECT DATE(e.fecha_ingreso) as label, COUNT(*) as valor
                    FROM empleados e
                    {where_sql}
                    GROUP BY DATE(e.fecha_ingreso) ORDER BY label ASC
                """, params)
                stats['por_fecha_ingreso'] = cursor.fetchall()

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_contrataciones(self, filtros=None, agrupacion='dia'):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        params = []
        where = ["c.estado = 1"]
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
        where_sql = "WHERE " + " AND ".join(where)

        try:
            stats = {}

            cursor.execute(f"""
                SELECT c.tipo_contrato as label, COUNT(*) as valor
                FROM contratacion c
                {where_sql}
                GROUP BY c.tipo_contrato
            """, params)
            stats['por_tipo'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT c.modalidad as label, COUNT(*) as valor
                FROM contratacion c
                {where_sql}
                GROUP BY c.modalidad
            """, params)
            stats['por_modalidad'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT c.objeto as label, COUNT(*) as valor
                FROM contratacion c
                {where_sql}
                GROUP BY c.objeto
            """, params)
            stats['por_objeto'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT c.estado as label, COUNT(*) as valor
                FROM contratacion c
                {where_sql}
                GROUP BY c.estado
            """, params)
            stats['por_estado'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT c.empresa_ganadora as label, COUNT(*) as valor
                FROM contratacion c
                {where_sql}
                GROUP BY c.empresa_ganadora
            """, params)
            stats['por_empresa'] = cursor.fetchall()

            if agrupacion == 'mes':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(c.fecha_registro, '%Y-%m') as label, COUNT(*) as valor
                    FROM contratacion c
                    {where_sql}
                    GROUP BY DATE_FORMAT(c.fecha_registro, '%Y-%m') ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()
            elif agrupacion == 'semana':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(c.fecha_registro, '%x-W%v') as label, COUNT(*) as valor
                    FROM contratacion c
                    {where_sql}
                    GROUP BY DATE_FORMAT(c.fecha_registro, '%x-W%v') ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()
            else:
                cursor.execute(f"""
                    SELECT DATE(c.fecha_registro) as label, COUNT(*) as valor
                    FROM contratacion c
                    {where_sql}
                    GROUP BY DATE(c.fecha_registro) ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_publicaciones(self, filtros=None, agrupacion='dia'):
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        params = []
        where = ["estado = 1"]
        mapeo = {
            'titulo_publicacion': 'titulo_publicacion',
            'nombre_responsable': 'nombre_responsable',
            'tipo_publicacion': 'tipo_publicacion',
            'fecha_publicacion_desde': 'fecha_publicacion',
            'fecha_publicacion_hasta': 'fecha_publicacion',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)
        where_sql = "WHERE " + " AND ".join(where)

        try:
            stats = {}

            cursor.execute(f"""
                SELECT tipo_publicacion as label, COUNT(*) as valor
                FROM publicacion
                {where_sql}
                GROUP BY tipo_publicacion
            """, params)
            stats['por_tipo'] = cursor.fetchall()

            cursor.execute(f"""
                SELECT nombre_responsable as label, COUNT(*) as valor
                FROM publicacion
                {where_sql}
                GROUP BY nombre_responsable
            """, params)
            stats['por_autor'] = cursor.fetchall()

            if agrupacion == 'mes':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(fecha_publicacion, '%Y-%m') as label, COUNT(*) as valor
                    FROM publicacion
                    {where_sql}
                    GROUP BY DATE_FORMAT(fecha_publicacion, '%Y-%m') ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()
            elif agrupacion == 'semana':
                cursor.execute(f"""
                    SELECT DATE_FORMAT(fecha_publicacion, '%x-W%v') as label, COUNT(*) as valor
                    FROM publicacion
                    {where_sql}
                    GROUP BY DATE_FORMAT(fecha_publicacion, '%x-W%v') ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()
            else:
                cursor.execute(f"""
                    SELECT DATE(fecha_publicacion) as label, COUNT(*) as valor
                    FROM publicacion
                    {where_sql}
                    GROUP BY DATE(fecha_publicacion) ORDER BY label ASC
                """, params)
                stats['por_fecha'] = cursor.fetchall()

            return stats
        finally:
            cursor.close()
            conexion.close()
