import re
from datetime import datetime
from conexion.conexionBD import connectionBD


class PrioridadModel:
    def __init__(self, id_prioridad=None, solicitud_id=None, rango_prioridad=None,
                 justificacion=None, responsable=None, estado=1):
        self.__id = id_prioridad
        self.__solicitud_id = solicitud_id
        self.__rango = rango_prioridad
        self.__justificacion = justificacion
        self.__responsable = responsable
        self.__estado = estado
        self.__fecha = datetime.now()

    # Getters y Setters con validación
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

    def set_justificacion(self, valor):
        if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s.,;:!?]{3,150}$', str(valor or '')):
            raise ValueError("Justificación inválida (3-150 caracteres alfanuméricos).")
        self.__justificacion = valor

    # ----- Métodos de persistencia (abren y cierran su propia conexión) -----
    def registrar(self):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            sql = """INSERT INTO prioridad (rango_prioridad, fecha_asignacion,
                    responsable_ajuste, justificacion_cambio, estado)
                    VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(sql, (self.__rango, self.__fecha,
                                 self.__responsable, self.__justificacion, self.__estado))
            conexion.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conexion.close()

    def actualizar(self):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            sql = """UPDATE prioridad SET rango_prioridad=%s, justificacion_cambio=%s,
                    estado=%s WHERE id_gestion_prioridad=%s"""
            cursor.execute(sql, (self.__rango, self.__justificacion,
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
        """
        Lista los registros de prioridad ordenados de MENOR a MAYOR rango
        (las más priorizadas están cerca de 0; las menos priorizadas cerca de 1).
        Incluye la solicitud vinculada, su gravedad y el color del semáforo.
        """
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) AS total FROM prioridad WHERE estado=1")
            total = cursor.fetchone()['total']

            offset = (max(1, page) - 1) * per_page
            sql = """
                SELECT p.id_gestion_prioridad,
                       p.rango_prioridad,
                       p.justificacion_cambio,
                       p.fecha_asignacion,
                       p.responsable_ajuste,
                       p.estado,
                       MAX(s.id_solicitudes)         AS solicitud_id,
                       MAX(s.problematica)           AS solicitud_descripcion,
                       MAX(s.tipo_solicitud)         AS tipo_solicitud,
                       MAX(g.nivel_gravedad)         AS nivel_gravedad,
                       MAX(sm.color)                 AS color_semaforo,
                       MAX(sm.estatus_semaforo)      AS estatus_semaforo
                FROM prioridad p
                LEFT JOIN solicitudes s
                       ON s.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                      AND s.estado = 1
                LEFT JOIN gravedad_obra_has_prioridad ghp
                       ON ghp.prioridad_id_gestion_prioridad = p.id_gestion_prioridad
                LEFT JOIN gravedad_obra g
                       ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                LEFT JOIN proyecto_has_solicitudes phs
                       ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                LEFT JOIN obra o
                       ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                LEFT JOIN semaforo sm
                       ON sm.id_semaforo = o.semaforo_id_semaforo
                WHERE p.estado = 1
                GROUP BY p.id_gestion_prioridad, p.rango_prioridad, p.justificacion_cambio,
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
    def clasificar_solicitud_con_ia(id_solicitud, descripcion, gravedad_nivel=None,
                                    color_semaforo=None, responsable='IA'):
        """
        Crea (o actualiza) el registro de prioridad de una solicitud usando la IA.
        Devuelve el id de la prioridad y los datos calculados.
        """
        from services.ia_prioridad_service import calcular_prioridad_con_ia
        resultado = calcular_prioridad_con_ia(descripcion, gravedad_nivel, color_semaforo)

        rango = float(resultado.get('prioridad', 0.5))
        justificacion = resultado.get('justificacion', 'Clasificación automática por IA')

        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            # ¿La solicitud ya tiene una prioridad propia?
            cursor.execute(
                "SELECT prioridad_id_gestion_prioridad AS pid FROM solicitudes WHERE id_solicitudes=%s",
                (id_solicitud,))
            fila = cursor.fetchone()
            pid = fila['pid'] if fila else None

            if pid:
                cursor.execute(
                    """UPDATE prioridad
                       SET rango_prioridad=%s, justificacion_cambio=%s,
                           responsable_ajuste=%s, estado=1
                       WHERE id_gestion_prioridad=%s""",
                    (rango, justificacion, responsable, pid))
                id_prioridad = pid
            else:
                cursor.execute(
                    """INSERT INTO prioridad (rango_prioridad, fecha_asignacion,
                       responsable_ajuste, justificacion_cambio, estado)
                       VALUES (%s, %s, %s, %s, 1)""",
                    (rango, datetime.now(), responsable, justificacion))
                id_prioridad = cursor.lastrowid
                cursor.execute(
                    "UPDATE solicitudes SET prioridad_id_gestion_prioridad=%s WHERE id_solicitudes=%s",
                    (id_prioridad, id_solicitud))
            conexion.commit()
            return {'id_prioridad': id_prioridad, 'rango': rango, 'justificacion': justificacion}
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def obtener_datos_solicitud(id_solicitud):
        """Devuelve descripción, gravedad y color de semáforo de una solicitud."""
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                """SELECT s.problematica AS descripcion,
                          g.nivel_gravedad,
                          sm.color AS color_semaforo
                   FROM solicitudes s
                   LEFT JOIN proyecto_has_solicitudes phs
                          ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                   LEFT JOIN obra o
                          ON o.gestionar_proyectos_codigo_proyecto = phs.proyecto_codigo_proyecto
                   LEFT JOIN semaforo sm
                          ON sm.id_semaforo = o.semaforo_id_semaforo
                   LEFT JOIN gravedad_obra_has_prioridad ghp
                          ON ghp.prioridad_id_gestion_prioridad = s.prioridad_id_gestion_prioridad
                   LEFT JOIN gravedad_obra g
                          ON g.id_gravedad = ghp.gravedad_obra_id_gravedad
                   WHERE s.id_solicitudes = %s AND s.estado = 1""",
                (id_solicitud,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()
