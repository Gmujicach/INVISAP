from models.base_model import BaseModel


class ReporteEstadisticoModel(BaseModel):
    def __init__(self):
        pass

    def _ejecutar_query(self, query, params=None):
        conexion = self.obtener_conexion_estricta()
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
            if key not in mapeo and key not in (
                'porcentaje_avance_min', 'porcentaje_avance_max',
                'sector', 'ambito',
            ):
                continue
            columna = mapeo.get(key)
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

    def _build_query(self, base_query, where_clauses):
        if where_clauses:
            return base_query + " WHERE " + " AND ".join(where_clauses)
        return base_query

    def _execute_stat_query(self, cursor, query, params):
        cursor.execute(query, params)
        return cursor.fetchall()

    def obtener_estadisticas_solicitudes(self, filtros=None, agrupacion='dia'):
        conexion = self.obtener_conexion_estricta()
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

        try:
            stats = {}

            base_from = """
                FROM solicitudes s
                JOIN persona p ON s.persona_id_persona = p.id_persona
                LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
            """

            if agrupacion == 'mes':
                query = self._build_query(
                    "SELECT DATE_FORMAT(s.fecha, '%%Y-%%m') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(s.fecha, '%%Y-%%m') ORDER BY label ASC"
                stats['por_mes'] = self._execute_stat_query(cursor, query, params)
            elif agrupacion == 'semana':
                query = self._build_query(
                    "SELECT DATE_FORMAT(s.fecha, '%%x-W%%v') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(s.fecha, '%%x-W%%v') ORDER BY label ASC"
                stats['por_semana'] = self._execute_stat_query(cursor, query, params)
            else:
                query = self._build_query(
                    "SELECT DATE(s.fecha) as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE(s.fecha) ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT s.tipo_solicitud as label, COUNT(*) as valor " + base_from,
                where
            ) + " GROUP BY s.tipo_solicitud"
            stats['por_tipo'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT s.estatus_solicitud as label, COUNT(*) as valor " + base_from,
                where
            ) + " GROUP BY s.estatus_solicitud"
            stats['por_estatus'] = self._execute_stat_query(cursor, query, params)

            if filtros and any(k in filtros for k in ['municipio', 'parroquia', 'cedula', 'direccion', 'telefono', 'correo', 'sector', 'ambito']):
                query = self._build_query(
                    "SELECT p.municipio as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY p.municipio"
                stats['por_municipio'] = self._execute_stat_query(cursor, query, params)

                query = self._build_query(
                    "SELECT p.parroquia as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY p.parroquia"
                stats['por_parroquia'] = self._execute_stat_query(cursor, query, params)

                query = self._build_query(
                    "SELECT com.sector as label, COUNT(*) as valor " + base_from + " AND com.sector IS NOT NULL AND com.sector != ''",
                    where
                ) + " GROUP BY com.sector"
                stats['por_sector'] = self._execute_stat_query(cursor, query, params)

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_obras(self, filtros=None, agrupacion='dia'):
        conexion = self.obtener_conexion_estricta()
        cursor = conexion.cursor(dictionary=True)
        params = []
        where = ["o.activo = 1"]
        mapeo = {
            'titulo_obra': 'o.titulo_obra',
            'ubicacion_obra': 'o.ubicacion_obra',
            'fecha_inicio_desde': 'o.fecha_inicio',
            'fecha_inicio_hasta': 'o.fecha_inicio',
            'fecha_fin_desde': 'o.fecha_fin',
            'fecha_fin_hasta': 'o.fecha_fin',
            'semaforo_estado': 's.color',
            'contratista': 'c.empresa_ganadora',
            'criticidad': 'g.criticidad',
            'nivel_gravedad': 'g.nivel_gravedad',
            'gerente': 'e.nombre_empleado',
        }
        self._aplicar_filtros(where, params, filtros, mapeo)

        try:
            stats = {}

            base_from = """
                FROM obra o
                JOIN semaforo s ON o.estado = s.id_semaforo
                JOIN contratacion c ON o.contratacion_id_contratacion = c.id_contratacion
                LEFT JOIN gravedad_obra g ON g.obra_id_obra = o.id_obra AND g.estado = 1
                LEFT JOIN avance a ON a.obra_id_obra = o.id_obra AND a.estado = 1
                LEFT JOIN empleados e ON e.id_empleados = a.gerente
            """

            if agrupacion == 'mes':
                query = self._build_query(
                    "SELECT DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%%Y-%%m') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%%Y-%%m') ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)
            elif agrupacion == 'semana':
                query = self._build_query(
                    "SELECT DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%%x-W%%v') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%%x-W%%v') ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)
            else:
                query = self._build_query(
                    "SELECT DATE(COALESCE(o.fecha_inicio, o.fecha_fin)) as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE(COALESCE(o.fecha_inicio, o.fecha_fin)) ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT s.estado as label, COUNT(*) as valor " + base_from,
                where
            ) + " GROUP BY s.estado"
            stats['por_estado'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT c.empresa_ganadora as label, COUNT(*) as valor " + base_from,
                where
            ) + " GROUP BY c.empresa_ganadora"
            stats['por_contratista'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT o.ubicacion_obra as label, COUNT(*) as valor " + base_from,
                where
            ) + " GROUP BY o.ubicacion_obra"
            stats['por_ubicacion'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT s.color as label, COUNT(*) as valor " + base_from,
                where
            ) + " GROUP BY s.color"
            stats['por_semaforo_color'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                """SELECT CASE
                    WHEN o.porcentaje_avance_obra < 25 THEN '0-25%%'
                    WHEN o.porcentaje_avance_obra < 50 THEN '25-50%%'
                    WHEN o.porcentaje_avance_obra < 75 THEN '50-75%%'
                    ELSE '75-100%%'
                END as label, COUNT(*) as valor """ + base_from,
                where
            ) + " GROUP BY label"
            stats['por_avance'] = self._execute_stat_query(cursor, query, params)

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_empleados(self, filtros=None, agrupacion='dia'):
        conexion = self.obtener_conexion_estricta()
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

        try:
            stats = {}

            query = self._build_query(
                "SELECT e.cargo as label, COUNT(*) as valor FROM empleados e",
                where
            ) + " GROUP BY e.cargo"
            stats['por_cargo'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT e.gerencia_asignada as label, COUNT(*) as valor FROM empleados e",
                where
            ) + " GROUP BY e.gerencia_asignada"
            stats['por_gerencia'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT e.estado as label, COUNT(*) as valor FROM empleados e",
                where
            ) + " GROUP BY e.estado"
            stats['por_estado'] = self._execute_stat_query(cursor, query, params)

            base_from = "FROM empleados e"

            if agrupacion == 'mes':
                query = self._build_query(
                    "SELECT DATE_FORMAT(e.fecha_ingreso, '%%Y-%%m') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(e.fecha_ingreso, '%%Y-%%m') ORDER BY label ASC"
                stats['por_fecha_ingreso'] = self._execute_stat_query(cursor, query, params)
            elif agrupacion == 'semana':
                query = self._build_query(
                    "SELECT DATE_FORMAT(e.fecha_ingreso, '%%x-W%%v') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(e.fecha_ingreso, '%%x-W%%v') ORDER BY label ASC"
                stats['por_fecha_ingreso'] = self._execute_stat_query(cursor, query, params)
            else:
                query = self._build_query(
                    "SELECT DATE(e.fecha_ingreso) as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE(e.fecha_ingreso) ORDER BY label ASC"
                stats['por_fecha_ingreso'] = self._execute_stat_query(cursor, query, params)

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_contrataciones(self, filtros=None, agrupacion='dia'):
        conexion = self.obtener_conexion_estricta()
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

        try:
            stats = {}

            query = self._build_query(
                "SELECT c.tipo_contrato as label, COUNT(*) as valor FROM contratacion c",
                where
            ) + " GROUP BY c.tipo_contrato"
            stats['por_tipo'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT c.modalidad as label, COUNT(*) as valor FROM contratacion c",
                where
            ) + " GROUP BY c.modalidad"
            stats['por_modalidad'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT c.objeto as label, COUNT(*) as valor FROM contratacion c",
                where
            ) + " GROUP BY c.objeto"
            stats['por_objeto'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT c.estado as label, COUNT(*) as valor FROM contratacion c",
                where
            ) + " GROUP BY c.estado"
            stats['por_estado'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT c.empresa_ganadora as label, COUNT(*) as valor FROM contratacion c",
                where
            ) + " GROUP BY c.empresa_ganadora"
            stats['por_empresa'] = self._execute_stat_query(cursor, query, params)

            base_from = "FROM contratacion c"

            if agrupacion == 'mes':
                query = self._build_query(
                    "SELECT DATE_FORMAT(c.fecha_registro, '%%Y-%%m') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(c.fecha_registro, '%%Y-%%m') ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)
            elif agrupacion == 'semana':
                query = self._build_query(
                    "SELECT DATE_FORMAT(c.fecha_registro, '%%x-W%%v') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(c.fecha_registro, '%%x-W%%v') ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)
            else:
                query = self._build_query(
                    "SELECT DATE(c.fecha_registro) as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE(c.fecha_registro) ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)

            return stats
        finally:
            cursor.close()
            conexion.close()

    def obtener_estadisticas_publicaciones(self, filtros=None, agrupacion='dia'):
        conexion = self.obtener_conexion_estricta()
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

        try:
            stats = {}

            query = self._build_query(
                "SELECT tipo_publicacion as label, COUNT(*) as valor FROM publicacion",
                where
            ) + " GROUP BY tipo_publicacion"
            stats['por_tipo'] = self._execute_stat_query(cursor, query, params)

            query = self._build_query(
                "SELECT nombre_responsable as label, COUNT(*) as valor FROM publicacion",
                where
            ) + " GROUP BY nombre_responsable"
            stats['por_autor'] = self._execute_stat_query(cursor, query, params)

            base_from = "FROM publicacion"

            if agrupacion == 'mes':
                query = self._build_query(
                    "SELECT DATE_FORMAT(fecha_publicacion, '%%Y-%%m') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(fecha_publicacion, '%%Y-%%m') ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)
            elif agrupacion == 'semana':
                query = self._build_query(
                    "SELECT DATE_FORMAT(fecha_publicacion, '%%x-W%%v') as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE_FORMAT(fecha_publicacion, '%%x-W%%v') ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)
            else:
                query = self._build_query(
                    "SELECT DATE(fecha_publicacion) as label, COUNT(*) as valor " + base_from,
                    where
                ) + " GROUP BY DATE(fecha_publicacion) ORDER BY label ASC"
                stats['por_fecha'] = self._execute_stat_query(cursor, query, params)

            return stats
        finally:
            cursor.close()
            conexion.close()