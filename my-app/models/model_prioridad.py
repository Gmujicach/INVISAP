import re
from datetime import datetime

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
            if not (1.0 <= v <= 5.0):
                raise ValueError("La prioridad debe estar entre 1 y 5.")
            self.__rango = v
        except:
            raise ValueError("Prioridad debe ser un número.")

    def set_justificacion(self, valor):
        if not re.match(r'^[A-Za-z0-9ÁÉÍÓÚáéíóúÑñ\s.,;:!?]{3,150}$', valor):
            raise ValueError("Justificación inválida (3-150 caracteres alfanuméricos).")
        self.__justificacion = valor

    # Métodos privados para BD
    def __registrar(self, cursor):
        sql = """INSERT INTO prioridad (rango_prioridad, fecha_asignacion,
                responsable_ajuste, justificacion_cambio, estado)
                VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (self.__rango, self.__fecha,
                             self.__responsable, self.__justificacion, self.__estado))
        return cursor.lastrowid

    def __actualizar(self, cursor):
        sql = """UPDATE prioridad SET rango_prioridad=%s, justificacion_cambio=%s,
                estado=%s WHERE id_gestion_prioridad=%s"""
        cursor.execute(sql, (self.__rango, self.__justificacion,
                             self.__estado, self.__id))
        return True

    def __eliminar_logico(self, cursor):
        sql = "UPDATE prioridad SET estado=0 WHERE id_gestion_prioridad=%s"
        cursor.execute(sql, (self.__id,))
        return True

    # Métodos públicos
    def registrar_prioridad(self, cursor):
        return self.__registrar(cursor)

    def actualizar_prioridad(self, cursor):
        return self.__actualizar(cursor)

    def eliminar_prioridad(self, cursor):
        return self.__eliminar_logico(cursor)