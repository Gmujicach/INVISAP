import re
from datetime import datetime
from conexion.conexionBD import connectionBD
from models.base_model import BaseModel


class PrioridadModel(BaseModel):
    PESOS_SOLICITANTE = {"comunidad": 3, "institucion": 2, "institución": 2, "particular": 1}
    PESOS_GRAVEDAD = {"alta": 3, "baja": 1}
    PESOS_TIPO_OBRA = {"Obra Mayor": 3, "Obra Menor": 1}

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
        if valor not in ('ia', 'heuristica', 'error', 'manual', None):
            raise ValueError("Origen debe ser 'ia', 'heuristica', 'error' o 'manual'.")
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

    @staticmethod
    def _obtener_siguiente_id(cursor):
        cursor.execute("SELECT COALESCE(MAX(id_gestion_prioridad), 0) + 1 AS siguiente_id FROM prioridad")
        fila = cursor.fetchone()
        return fila[0] if fila else 1

    def registrar(self):
        self._validar_para_persistencia()
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            siguiente_id = self._obtener_siguiente_id(cursor)
            sql = """INSERT INTO prioridad (id_gestion_prioridad, rango_prioridad, tipo_obra,
                    gravedad_sugerida, origen, fecha_asignacion, responsable_ajuste,
                    justificacion_cambio, estado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (siguiente_id, self.__rango, self.__tipo_obra,
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
    def listar_priorizadas(page=1, per_page=10):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT COUNT(*) AS total FROM prioridad WHERE estado=1")
            total = cursor.fetchone()['total']

            offset = (max(1, page) - 1) * per_page
            sql = """
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
                WHERE p.estado = 1
                GROUP BY p.id_gestion_prioridad, p.rango_prioridad, p.justificacion_cambio,
                         p.tipo_obra, p.gravedad_sugerida, p.origen,
                         p.fecha_asignacion, p.responsable_ajuste, p.estado
                ORDER BY p.rango_prioridad ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (per_page, offset))
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
                          g.nivel_gravedad,
                          sm.color            AS color_semaforo
                   FROM solicitudes s
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
                """SELECT s.id_solicitudes       AS id,
                          s.problematica        AS descripcion,
                          s.tipo_solicitud      AS tipo_solicitante,
                          g.nivel_gravedad,
                          sm.color              AS color_semaforo
                   FROM solicitudes s
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
    def _calcular_puntaje_ponderado(tipo_solicitante, gravedad_sugerida, tipo_obra):
        solicitante_lower = (tipo_solicitante or "").lower()
        peso_solicitante = PrioridadModel.PESOS_SOLICITANTE.get(solicitante_lower, 1)

        gravedad_lower = (gravedad_sugerida or "").lower()
        peso_gravedad = PrioridadModel.PESOS_GRAVEDAD.get(gravedad_lower, 1)

        peso_tipo_obra = PrioridadModel.PESOS_TIPO_OBRA.get(tipo_obra, 1)

        puntaje = (peso_solicitante * 0.30) + (peso_gravedad * 0.40) + (peso_tipo_obra * 0.30)

        rango = round((3 - puntaje) / 2, 3)

        return {
            "puntaje_ponderado": round(puntaje, 3),
            "rango_prioridad": round(min(max(rango, 0.0), 1.0), 3),
            "peso_solicitante": peso_solicitante,
            "peso_gravedad": peso_gravedad,
            "peso_tipo_obra": peso_tipo_obra,
        }

    @staticmethod
    def clasificar_nueva_solicitud(id_solicitud, responsable='IA'):
        from services.ia_prioridad_service import clasificar_solicitud_ia

        datos = PrioridadModel.obtener_datos_solicitud(id_solicitud)
        if not datos:
            return {"success": False, "message": "Solicitud no encontrada."}

        descripcion = datos.get('descripcion') or ''
        gravedad_nivel = datos.get('nivel_gravedad')
        color_semaforo = datos.get('color_semaforo')
        tipo_solicitante = datos.get('tipo_solicitante')

        resultado_ia = clasificar_solicitud_ia(descripcion, gravedad_nivel, color_semaforo, tipo_solicitante)

        calculo = PrioridadModel._calcular_puntaje_ponderado(
            tipo_solicitante,
            resultado_ia.get('gravedad_sugerida'),
            resultado_ia.get('tipo_obra')
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

            if pid and pid != 0:
                cursor.execute(
                    """UPDATE prioridad
                       SET rango_prioridad=%s, justificacion_cambio=%s,
                           tipo_obra=%s, gravedad_sugerida=%s, origen=%s,
                           responsable_ajuste=%s, estado=1
                       WHERE id_gestion_prioridad=%s""",
                    (rango, justificacion, resultado_ia.get('tipo_obra'),
                     resultado_ia.get('gravedad_sugerida'),
                     resultado_ia.get('origen', 'ia'),
                     responsable, pid))
                id_prioridad = pid
            else:
                cursor.execute(
                    "SELECT COALESCE(MAX(id_gestion_prioridad), 0) + 1 AS siguiente_id FROM prioridad")
                fila = cursor.fetchone()
                siguiente_id = fila[0] if fila else 1

                cursor.execute(
                    """INSERT INTO prioridad (id_gestion_prioridad, rango_prioridad, tipo_obra,
                       gravedad_sugerida, origen, fecha_asignacion, responsable_ajuste,
                       justificacion_cambio, estado)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (siguiente_id, rango, resultado_ia.get('tipo_obra'),
                     resultado_ia.get('gravedad_sugerida'),
                     resultado_ia.get('origen', 'ia'),
                     datetime.now(), responsable, justificacion, 1))
                id_prioridad = siguiente_id
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
                    "origen": resultado_ia.get('origen', 'desconocido'),
                    "calculo": calculo,
                }
            }
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def procesar_solicitudes_pendientes_batch(responsable='IA'):
        from services.ia_prioridad_service import clasificar_solicitud_ia
        import traceback

        solicitudes = PrioridadModel.obtener_solicitudes_sin_priorizar()
        if not solicitudes:
            return {"success": True, "message": "No hay solicitudes pendientes.", "procesadas": 0}

        resultados = []
        errores = 0

        for solicitud in solicitudes:
            try:
                id_sol = solicitud['id']
                descripcion = solicitud.get('descripcion') or ''
                gravedad_nivel = solicitud.get('nivel_gravedad')
                color_semaforo = solicitud.get('color_semaforo')
                tipo_solicitante = solicitud.get('tipo_solicitante')

                resultado_ia = clasificar_solicitud_ia(
                    descripcion, gravedad_nivel, color_semaforo, tipo_solicitante
                )

                calculo = PrioridadModel._calcular_puntaje_ponderado(
                    tipo_solicitante,
                    resultado_ia.get('gravedad_sugerida'),
                    resultado_ia.get('tipo_obra')
                )

                rango = calculo['rango_prioridad']
                justificacion = resultado_ia.get('justificacion', 'Clasificación automática por IA')

                conexion = connectionBD()
                try:
                    cursor = conexion.cursor(dictionary=True, buffered=True)
                    cursor.execute(
                        "SELECT COALESCE(MAX(id_gestion_prioridad), 0) + 1 AS siguiente_id FROM prioridad")
                    fila = cursor.fetchone()
                    siguiente_id = fila['siguiente_id'] if fila else 1

                    cursor.execute(
                        """INSERT INTO prioridad (id_gestion_prioridad, rango_prioridad, tipo_obra,
                           gravedad_sugerida, origen, fecha_asignacion, responsable_ajuste,
                           justificacion_cambio, estado)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (siguiente_id, rango, resultado_ia.get('tipo_obra'),
                         resultado_ia.get('gravedad_sugerida'),
                         resultado_ia.get('origen', 'ia'),
                         datetime.now(), responsable, justificacion, 1))
                    id_prioridad = siguiente_id

                    cursor.execute(
                        "UPDATE solicitudes SET prioridad_id_gestion_prioridad=%s WHERE id_solicitudes=%s",
                        (id_prioridad, id_sol))
                    conexion.commit()

                    resultados.append({
                        "solicitud_id": id_sol,
                        "id_prioridad": id_prioridad,
                        "rango": rango,
                        "tipo_obra": resultado_ia.get('tipo_obra'),
                        "gravedad_sugerida": resultado_ia.get('gravedad_sugerida'),
                    })
                finally:
                    cursor.close()
                    conexion.close()

            except Exception as e:
                errores += 1
                tb = traceback.format_exc()
                resultados.append({
                    "solicitud_id": solicitud.get('id'),
                    "error": str(e),
                    "traceback": tb,
                })

        return {
            "success": True,
            "message": f"Proceso completado. {len(resultados)} solicitudes procesadas, {errores} errores.",
            "procesadas": len(resultados),
            "errores": errores,
            "detalle": resultados,
        }

    @staticmethod
    def clasificar_solicitud_con_ia(id_solicitud, descripcion, gravedad_nivel=None,
                                    color_semaforo=None, responsable='IA'):
        from services.ia_prioridad_service import calcular_prioridad_con_ia
        resultado = calcular_prioridad_con_ia(descripcion, gravedad_nivel, color_semaforo)

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
                siguiente_id = fila[0] if fila else 1

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
