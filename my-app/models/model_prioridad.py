import re
from datetime import datetime
from conexion.conexionBD import connectionBD
from models.base_model import BaseModel


class PrioridadModel(BaseModel):
    PESOS_SOLICITANTE = {"comunidad": 3, "institucion": 2, "institución": 2, "particular": 1}
    PESOS_GRAVEDAD = {3: 3, 1: 1}
    PESOS_TIPO_OBRA = {"Obra Mayor": 3, "Obra Menor": 1}
    PESOS_ZONA_AGRICOLA = {3: 3, 1: 1}

    def __init__(self, id_prioridad=None, solicitud_id=None, rango_prioridad=None,
                 justificacion=None, responsable=None, estado=1, tipo_obra=None,
                 gravedad_sugerida=None, origen='manual'):
        self.__id = id_prioridad
        self.__solicitud_id = solicitud_id
        self.__rango = rango_prioridad
        self.__justificacion = justificacion
        self.__responsable = responsable
        self.__estado = estado
        self.__fecha = datetime.now()
        self.__tipo_obra = tipo_obra
        self.__gravedad_sugerida = gravedad_sugerida
        self.__origen = origen

    def get_id(self):
        return self.__id

    def get_solicitud_id(self):
        return self.__solicitud_id

    def get_rango(self):
        return self.__rango

    def set_rango(self, valor):
        try:
            v = float(valor)
            if not (0.0 <= v <= 1.0):
                raise ValueError("La prioridad debe estar entre 0 y 1.")
            self.__rango = round(v, 3)
        except (TypeError, ValueError):
            raise ValueError("Prioridad debe ser un número entre 0 y 1.")

    def get_justificacion(self):
        return self.__justificacion

    def set_justificacion(self, valor):
        if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóÚÑñ\s.,;:!?\-\'"]{3,150}$', str(valor or '')):
            raise ValueError("Justificación inválida (3-150 caracteres alfanuméricos).")
        self.__justificacion = valor

    def get_responsable(self):
        return self.__responsable

    def set_responsable(self, valor):
        if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóÚÑñ\s]{2,30}$', str(valor or '')):
            raise ValueError("Responsable inválido (2-30 caracteres).")
        self.__responsable = valor

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        self.__estado = 1 if int(valor) else 0

    def get_origen(self):
        return self.__origen

    def set_origen(self, valor):
        if valor not in ('ia', 'heuristica', 'error', 'manual', 'pendiente', None):
            raise ValueError("Origen debe ser 'ia', 'heuristica', 'error', 'manual' o 'pendiente'.")
        self.__origen = valor

    def get_tipo_obra(self):
        return self.__tipo_obra

    def set_tipo_obra(self, valor):
        if valor not in ("Obra Mayor", "Obra Menor", None):
            raise ValueError("Tipo de obra debe ser 'Obra Mayor' o 'Obra Menor'.")
        self.__tipo_obra = valor

    def get_gravedad_sugerida(self):
        return self.__gravedad_sugerida

    def set_gravedad_sugerida(self, valor):
        if valor not in ("Alta", "Baja", None):
            raise ValueError("Gravedad debe ser 'Alta' o 'Baja'.")
        self.__gravedad_sugerida = valor

    def registrar(self):
        self._validar_para_persistencia()
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            sql = """INSERT INTO prioridad (rango_prioridad, tipo_obra,
                    gravedad_sugerida, origen, fecha_asignacion, responsable_ajuste,
                    justificacion_cambio, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (self.__rango, self.__tipo_obra,
                                 self.__gravedad_sugerida, self.__origen, self.__fecha,
                                 self.__responsable, self.__justificacion, self.__estado))
            conexion.commit()
            self.__id = cursor.lastrowid
            return self.__id
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self):
        self._validar_para_persistencia()
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            sql = """UPDATE prioridad SET rango_prioridad=%s, justificacion_cambio=%s,
                    tipo_obra=%s, gravedad_sugerida=%s, origen=%s, estado=%s
                    WHERE id_gestion_prioridad=%s"""
            cursor.execute(sql, (self.__rango, self.__justificacion, self.__tipo_obra,
                                 self.__gravedad_sugerida, self.__origen,
                                 self.__estado, self.__id))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conexion.close()

    def eliminar_logico(self):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE prioridad SET estado=0 WHERE id_gestion_prioridad=%s",
                (self.__id,))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conexion.close()

    def _validar_para_persistencia(self):
        if self.__rango is None:
            raise ValueError("La prioridad es obligatoria.")
        if not self.__justificacion:
            raise ValueError("La justificación es obligatoria.")
        if len(str(self.__justificacion)) > 150:
            raise ValueError("La justificación no puede superar 150 caracteres.")

    @staticmethod
    def obtener_detalle_completo(id_prioridad):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """SELECT p.id_gestion_prioridad, p.rango_prioridad,
                          p.justificacion_cambio, p.tipo_obra, p.gravedad_sugerida,
                          p.origen, p.fecha_asignacion, p.responsable_ajuste,
                          p.estado,
                          MAX(s.id_solicitudes)       AS solicitud_id,
                          MAX(s.problematica)         AS solicitud_descripcion,
                          MAX(s.tipo_solicitud)       AS tipo_solicitud,
                          MAX(COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad)) AS nombre_solicitante,
                          MAX(per.cedula_persona)     AS cedula_persona,
                          MAX(per.telefono)           AS telefono,
                          MAX(per.correo)             AS correo,
                          MAX(per.direccion)          AS direccion,
                          MAX(per.municipio)          AS municipio,
                          MAX(per.parroquia)          AS parroquia,
                          MAX(com.sector)             AS sector,
                          MAX(com.ambito)             AS ambito,
                          MAX(s.estatus_solicitud)    AS estatus_solicitud,
                          MAX(s.fecha)                AS fecha_solicitud,
                          MAX(g.nivel_gravedad)       AS nivel_gravedad,
                          MAX(sm.color)               AS color_semaforo,
                          MAX(sm.descripcion)         AS descripcion_semaforo
                   FROM prioridad p
                   LEFT JOIN solicitudes s
                          ON s.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                   LEFT JOIN persona per
                          ON per.id_persona = s.persona_id_persona
                   LEFT JOIN particular part
                          ON part.persona_id_persona = per.id_persona
                   LEFT JOIN institucion inst
                          ON inst.persona_id_persona = per.id_persona
                   LEFT JOIN comunidad com
                          ON com.persona_id_persona = per.id_persona
                   LEFT JOIN solicitudes s2
                          ON s2.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                         AND s2.id_solicitudes <> s.id_solicitudes
                   LEFT JOIN gravedad_obra_has_prioridad ghp
                          ON ghp.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                   LEFT JOIN gravedad_obra g
                          ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                        AND g.estado = 1
                   LEFT JOIN proyecto_has_solicitudes phs
                          ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                   LEFT JOIN obra o
                          ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                   LEFT JOIN semaforo sm
                          ON sm.id_semaforo = o.estado
                   WHERE p.id_gestion_prioridad = %s
                   GROUP BY p.id_gestion_prioridad
                   LIMIT 1""",
                (id_prioridad,))
            fila = cursor.fetchone()
            return fila
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def obtener_por_id(id_prioridad):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT id_gestion_prioridad, rango_prioridad, justificacion_cambio,
                          fecha_asignacion, responsable_ajuste, estado
                   FROM prioridad WHERE id_gestion_prioridad=%s""",
                (id_prioridad,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def listar_priorizadas(page=1, per_page=10, q='', riesgo='ALL', orden='rango_asc'):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)

            where_clauses = ["p.estado = 1"]
            params = []

            if q:
                q_like = f"%{q}%"
                where_clauses.append(
                    "(s.problematica LIKE %s "
                    " OR per.direccion LIKE %s "
                    " OR per.municipio LIKE %s "
                    " OR per.parroquia LIKE %s "
                    " OR com.sector LIKE %s "
                    " OR s.tipo_solicitud LIKE %s "
                    " OR s.estatus_solicitud LIKE %s "
                    " OR DATE_FORMAT(s.fecha, '%%Y-%%m-%%d') LIKE %s "
                    " OR DATE_FORMAT(p.fecha_asignacion, '%%Y-%%m-%%d') LIKE %s "
                    " OR p.justificacion_cambio LIKE %s "
                    " OR p.tipo_obra LIKE %s "
                    " OR p.gravedad_sugerida LIKE %s)"
                )
                params.extend([
                    q_like, q_like, q_like, q_like, q_like,
                    q_like, q_like, q_like, q_like, q_like,
                    q_like, q_like,
                ])

            riesgo_upper = (riesgo or 'ALL').upper()
            if riesgo_upper == 'ALTA':
                where_clauses.append("p.rango_prioridad <= 0.30")
            elif riesgo_upper == 'BAJA':
                where_clauses.append("p.rango_prioridad > 0.30")

            where_sql = " AND ".join(where_clauses)

            orden_map = {
                'rango_asc': 'p.rango_prioridad ASC',
                'rango_desc': 'p.rango_prioridad DESC',
                'fecha_desc': 'p.fecha_asignacion DESC',
                'fecha_asc': 'p.fecha_asignacion ASC',
                'id_desc': 'p.id_gestion_prioridad DESC',
            }
            order_sql = orden_map.get(orden, 'p.rango_prioridad ASC')

            count_sql = f"""
                SELECT COUNT(DISTINCT p.id_gestion_prioridad) AS total
                FROM prioridad p
                LEFT JOIN solicitudes s
                       ON s.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                      AND s.estado = 1
                LEFT JOIN persona per
                       ON per.id_persona = s.persona_id_persona
                LEFT JOIN comunidad com
                       ON com.persona_id_persona = per.id_persona
                WHERE {where_sql}
            """
            cursor.execute(count_sql, params)
            row = cursor.fetchone()
            total = row['total'] if row else 0

            offset = (max(1, page) - 1) * per_page
            sql = f"""
                SELECT p.id_gestion_prioridad,
                       p.rango_prioridad,
                       p.justificacion_cambio,
                       p.tipo_obra,
                       p.gravedad_sugerida,
                       p.origen,
                       p.fecha_asignacion,
                       p.responsable_ajuste,
                       p.estado,
                       MAX(s.id_solicitudes)         AS solicitud_id,
                       MAX(s.problematica)           AS solicitud_descripcion,
                       MAX(s.tipo_solicitud)         AS tipo_solicitud,
                       MAX(g.nivel_gravedad)         AS nivel_gravedad,
                       MAX(sm.color)                 AS color_semaforo,
                       MAX(sm.descripcion)           AS descripcion_semaforo
                FROM prioridad p
                LEFT JOIN solicitudes s
                       ON s.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                      AND s.estado = 1
                LEFT JOIN persona per
                       ON per.id_persona = s.persona_id_persona
                LEFT JOIN comunidad com
                       ON com.persona_id_persona = per.id_persona
                LEFT JOIN gravedad_obra_has_prioridad ghp
                       ON ghp.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                LEFT JOIN gravedad_obra g
                       ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                      AND g.estado = 1
                LEFT JOIN proyecto_has_solicitudes phs
                       ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                LEFT JOIN obra o
                       ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                LEFT JOIN semaforo sm
                       ON sm.id_semaforo = o.estado
                WHERE {where_sql}
                GROUP BY p.id_gestion_prioridad, p.rango_prioridad, p.justificacion_cambio,
                         p.tipo_obra, p.gravedad_sugerida, p.origen,
                         p.fecha_asignacion, p.responsable_ajuste, p.estado
                ORDER BY {order_sql}
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (*params, per_page, offset))
            filas = cursor.fetchall()
            for f in filas:
                f['rango_prioridad'] = float(f['rango_prioridad']) if f['rango_prioridad'] is not None else 0.0
            return filas, total
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def obtener_datos_solicitud(id_solicitud):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """SELECT s.problematica       AS descripcion,
                          s.tipo_solicitud    AS tipo_solicitante,
                          p.municipio         AS municipio,
                          p.parroquia         AS parroquia,
                          com.sector          AS sector,
                          com.ambito          AS ambito,
                          g.nivel_gravedad,
                          sm.color            AS color_semaforo,
                          sm.id_semaforo      AS id_semaforo
                   FROM solicitudes s
                   LEFT JOIN persona p ON s.persona_id_persona = p.id_persona
                   LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                   LEFT JOIN proyecto_has_solicitudes phs
                          ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                   LEFT JOIN obra o
                          ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                   LEFT JOIN semaforo sm
                          ON sm.id_semaforo = o.estado
                   LEFT JOIN gravedad_obra_has_prioridad ghp
                          ON ghp.prioridad_id_gestion_prioridad = s.prioridad_id_gestion_prioridad
                   LEFT JOIN gravedad_obra g
                          ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                         AND g.estado = 1
                   WHERE s.id_solicitudes = %s AND s.estado = 1""",
                (id_solicitud,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def obtener_gravedad_obra(gravedad_id):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT id_gravedad, nivel_gravedad, criticidad
                   FROM gravedad_obra
                   WHERE id_gravedad = %s AND estado = 1""",
                (gravedad_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def obtener_solicitudes_sin_priorizar():
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """SELECT DISTINCT s.id_solicitudes       AS id,
                           s.fecha                  AS fecha,
                           s.problematica        AS descripcion,
                           s.tipo_solicitud      AS tipo_solicitante,
                           p.municipio           AS municipio,
                           p.parroquia           AS parroquia,
                           com.sector            AS sector,
                           com.ambito            AS ambito,
                           g.nivel_gravedad,
                           sm.color              AS color_semaforo
                    FROM solicitudes s
                    LEFT JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    LEFT JOIN proyecto_has_solicitudes phs
                           ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                    LEFT JOIN obra o
                           ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                    LEFT JOIN semaforo sm
                           ON sm.id_semaforo = o.estado
                    LEFT JOIN gravedad_obra_has_prioridad ghp
                           ON ghp.prioridad_id_gestion_prioridad = s.prioridad_id_gestion_prioridad
                    LEFT JOIN gravedad_obra g
                           ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                          AND g.estado = 1
                          LEFT JOIN prioridad pri
                              ON pri.id_gestion_prioridad = s.prioridad_id_gestion_prioridad
                     WHERE s.estado = 1
                          AND (s.prioridad_id_gestion_prioridad IS NULL
                                OR s.prioridad_id_gestion_prioridad = 0
                                OR pri.id_gestion_prioridad IS NULL
                                OR (pri.estado = 0 AND pri.origen = 'pendiente'))
                     ORDER BY s.fecha ASC""",
                ())
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def obtener_todas_solicitudes():
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute(
                """SELECT DISTINCT s.id_solicitudes       AS id,
                           s.fecha                  AS fecha,
                           s.problematica        AS descripcion,
                           s.tipo_solicitud      AS tipo_solicitante,
                           p.municipio           AS municipio,
                           p.parroquia           AS parroquia,
                           com.sector            AS sector,
                           com.ambito            AS ambito,
                           g.nivel_gravedad,
                           sm.color              AS color_semaforo
                    FROM solicitudes s
                    LEFT JOIN persona p ON s.persona_id_persona = p.id_persona
                    LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                    LEFT JOIN proyecto_has_solicitudes phs
                           ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                    LEFT JOIN obra o
                           ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                    LEFT JOIN semaforo sm
                           ON sm.id_semaforo = o.estado
                    LEFT JOIN gravedad_obra_has_prioridad ghp
                           ON ghp.prioridad_id_gestion_prioridad = s.prioridad_id_gestion_prioridad
                    LEFT JOIN gravedad_obra g
                           ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                          AND g.estado = 1
                    WHERE s.estado = 1
                    ORDER BY s.fecha ASC""",
                ())
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def _calcular_puntaje_ponderado(tipo_solicitante, gravedad_valor, tipo_obra,
                                    es_zona_agricola_valor):
        """Cálculo con conversión explícita a int. Defensa contra valores mal
        formateados (decimales, strings, nulos)."""
        try:
            solicitante_lower = (tipo_solicitante or "").lower()
            peso_solicitante = int(PrioridadModel.PESOS_SOLICITANTE.get(solicitante_lower, 1))
        except (TypeError, ValueError):
            peso_solicitante = 1

        try:
            peso_gravedad = int(PrioridadModel.PESOS_GRAVEDAD.get(int(gravedad_valor), 1))
        except (TypeError, ValueError):
            peso_gravedad = 1

        try:
            peso_tipo_obra = int(PrioridadModel.PESOS_TIPO_OBRA.get(tipo_obra, 1))
        except (TypeError, ValueError):
            peso_tipo_obra = 1

        try:
            peso_zona = int(PrioridadModel.PESOS_ZONA_AGRICOLA.get(int(es_zona_agricola_valor), 1))
        except (TypeError, ValueError):
            peso_zona = 1

        puntaje = (
            peso_solicitante * 0.20
            + peso_gravedad * 0.35
            + peso_tipo_obra * 0.30
            + peso_zona * 0.15
        )
        rango = round((3 - puntaje) / 2, 3)
        return {
            "puntaje_ponderado": round(puntaje, 3),
            "rango_prioridad": round(min(max(rango, 0.0), 1.0), 3),
            "peso_solicitante": peso_solicitante,
            "peso_gravedad": peso_gravedad,
            "peso_tipo_obra": peso_tipo_obra,
            "peso_zona_agricola": peso_zona,
        }

    @staticmethod
    def clasificar_nueva_solicitud(id_solicitud, responsable='IA'):
        from services.ia_prioridad_service import clasificar_solicitud_ia

        datos = PrioridadModel.obtener_datos_solicitud(id_solicitud)
        if not datos:
            return {"success": False, "message": "Solicitud no encontrada."}

        resultado_ia = clasificar_solicitud_ia(
            datos.get('descripcion') or '',
            datos.get('municipio'),
            datos.get('parroquia'),
            datos.get('sector'),
            datos.get('ambito'),
            datos.get('nivel_gravedad'),
            datos.get('color_semaforo'),
            datos.get('tipo_solicitante'),
        )

        calculo = PrioridadModel._calcular_puntaje_ponderado(
            datos.get('tipo_solicitante'),
            resultado_ia.get('gravedad_valor'),
            resultado_ia.get('tipo_obra'),
            resultado_ia.get('es_zona_agricola'),
        )

        rango = calculo['rango_prioridad']
        justificacion = resultado_ia.get('justificacion', 'Clasificación automática por IA')

        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT prioridad_id_gestion_prioridad AS pid FROM solicitudes WHERE id_solicitudes=%s",
                (id_solicitud,))
            fila = cursor.fetchone()
            pid = fila['pid'] if fila else None

            id_prioridad = pid
            debe_insertar = not id_prioridad or id_prioridad == 0

            if not debe_insertar:
                cursor.execute(
                    "SELECT id_gestion_prioridad FROM prioridad WHERE id_gestion_prioridad=%s",
                    (id_prioridad,),
                )
                debe_insertar = cursor.fetchone() is None

            if not debe_insertar:
                cursor.execute(
                    """UPDATE prioridad
                       SET rango_prioridad=%s, justificacion_cambio=%s,
                           tipo_obra=%s, gravedad_sugerida=%s, origen=%s,
                           responsable_ajuste=%s, estado=1
                       WHERE id_gestion_prioridad=%s""",
                    (rango, justificacion, resultado_ia.get('tipo_obra'),
                     resultado_ia.get('gravedad_sugerida'),
                     resultado_ia.get('origen', 'ia'),
                     responsable, id_prioridad))

            if debe_insertar:
                cursor.execute(
                    """INSERT INTO prioridad (rango_prioridad, tipo_obra,
                       gravedad_sugerida, origen, fecha_asignacion, responsable_ajuste,
                       justificacion_cambio, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (rango, resultado_ia.get('tipo_obra'),
                     resultado_ia.get('gravedad_sugerida'),
                     resultado_ia.get('origen', 'ia'),
                     datetime.now(), responsable, justificacion, 1))
                id_prioridad = cursor.lastrowid
                cursor.execute(
                    "UPDATE solicitudes SET prioridad_id_gestion_prioridad=%s WHERE id_solicitudes=%s",
                    (id_prioridad, id_solicitud))
            conexion.commit()
            return {
                "success": True,
                "data": {
                    "id_prioridad": id_prioridad,
                    "rango": rango,
                    "justificacion": justificacion,
                    "tipo_obra": resultado_ia.get('tipo_obra'),
                    "gravedad_sugerida": resultado_ia.get('gravedad_sugerida'),
                    "zona_agricola": resultado_ia.get('zona_agricola'),
                    "tipo_obra_valor": resultado_ia.get('tipo_obra_valor'),
                    "gravedad_valor": resultado_ia.get('gravedad_valor'),
                    "es_zona_agricola": resultado_ia.get('es_zona_agricola'),
                    "origen": resultado_ia.get('origen', 'desconocido'),
                    "calculo": calculo,
                }
            }
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def procesar_solicitudes_pendientes_batch(responsable='IA'):
        import traceback

        solicitudes = PrioridadModel.obtener_solicitudes_sin_priorizar()
        if not solicitudes:
            return {"success": True, "message": "No hay solicitudes pendientes.", "procesadas": 0}

        resultados = []
        procesadas = 0
        errores = 0

        for solicitud in solicitudes:
            try:
                resultado = PrioridadModel.clasificar_nueva_solicitud(
                    solicitud['id'], responsable
                )
                if resultado.get('success'):
                    procesadas += 1
                    datos = resultado['data']
                    resultados.append({
                        "solicitud_id": solicitud['id'],
                        "id_prioridad": datos['id_prioridad'],
                        "rango": datos['rango'],
                        "tipo_obra": datos['tipo_obra'],
                        "gravedad_sugerida": datos['gravedad_sugerida'],
                    })
                else:
                    errores += 1
                    resultados.append({
                        "solicitud_id": solicitud.get('id'),
                        "error": resultado.get('message', 'Error desconocido'),
                    })
            except Exception as e:
                errores += 1
                resultados.append({
                    "solicitud_id": solicitud.get('id'),
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                })

        return {
            "success": errores == 0,
            "message": f"Proceso completado. {procesadas} solicitudes procesadas, {errores} errores.",
            "procesadas": procesadas,
            "errores": errores,
            "detalle": resultados,
        }

    @staticmethod
    def procesar_todas_solicitudes_batch(responsable='IA'):
        import traceback

        solicitudes = PrioridadModel.obtener_todas_solicitudes()
        if not solicitudes:
            return {"success": True, "message": "No hay solicitudes para procesar.", "procesadas": 0}

        resultados = []
        procesadas = 0
        errores = 0

        for solicitud in solicitudes:
            try:
                resultado = PrioridadModel.clasificar_nueva_solicitud(solicitud['id'], responsable)
                if resultado.get('success'):
                    procesadas += 1
                    resultados.append({
                        "solicitud_id": solicitud['id'],
                        "id_prioridad": resultado['data']['id_prioridad'],
                        "rango": resultado['data']['rango'],
                        "tipo_obra": resultado['data']['tipo_obra'],
                        "gravedad_sugerida": resultado['data']['gravedad_sugerida'],
                    })
                else:
                    errores += 1
                    resultados.append({
                        "solicitud_id": solicitud.get('id'),
                        "error": resultado.get('message', 'Error desconocido'),
                    })
            except Exception as e:
                errores += 1
                tb = traceback.format_exc()
                resultados.append({
                    "solicitud_id": solicitud.get('id'),
                    "error": str(e),
                    "traceback": tb,
                })

        return {
            "success": errores == 0,
            "message": f"Re-clasificación completada. {procesadas} solicitudes procesadas, {errores} errores.",
            "procesadas": procesadas,
            "errores": errores,
            "detalle": resultados,
        }

    @staticmethod
    def clasificar_solicitud_con_ia(id_solicitud, descripcion, gravedad_nivel=None,
                                    color_semaforo=None, municipio=None,
                                    parroquia=None, sector=None, ambito=None,
                                    responsable='IA'):
        from services.ia_prioridad_service import calcular_prioridad_con_ia
        resultado = calcular_prioridad_con_ia(
            descripcion, municipio, parroquia, sector, ambito,
            gravedad_nivel, color_semaforo,
        )

        rango = float(resultado.get('prioridad', 0.5))
        justificacion = resultado.get('justificacion', 'Clasificación automática por IA')
        tipo_obra = resultado.get('tipo_obra')
        gravedad_sugerida = resultado.get('gravedad_sugerida')
        origen = resultado.get('origen', 'ia')

        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT prioridad_id_gestion_prioridad AS pid FROM solicitudes WHERE id_solicitudes=%s",
                (id_solicitud,))
            fila = cursor.fetchone()
            pid = fila['pid'] if fila else None

            if pid and pid != 0:
                cursor.execute(
                    """UPDATE prioridad
                       SET rango_prioridad=%s, justificacion_cambio=%s,
                           tipo_obra=%s, gravedad_sugerida=%s, origen=%s,
                           responsable_ajuste=%s, estado=1
                       WHERE id_gestion_prioridad=%s""",
                    (rango, justificacion, tipo_obra, gravedad_sugerida,
                     origen, responsable, pid))
                id_prioridad = pid
            else:
                cursor.execute(
                    "SELECT COALESCE(MAX(id_gestion_prioridad), 0) + 1 AS siguiente_id FROM prioridad")
                fila = cursor.fetchone()
                siguiente_id = fila['siguiente_id'] if fila else 1

                cursor.execute(
                    """INSERT INTO prioridad (id_gestion_prioridad, rango_prioridad, tipo_obra,
                       gravedad_sugerida, origen, fecha_asignacion, responsable_ajuste,
                       justificacion_cambio, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (siguiente_id, rango, tipo_obra, gravedad_sugerida, origen,
                     datetime.now(), responsable, justificacion, 1))
                id_prioridad = siguiente_id
                cursor.execute(
                    "UPDATE solicitudes SET prioridad_id_gestion_prioridad=%s WHERE id_solicitudes=%s",
                    (id_prioridad, id_solicitud))
            conexion.commit()
            return {'id_prioridad': id_prioridad, 'rango': rango, 'justificacion': justificacion}
        finally:
            cursor.close()
            conexion.close()
