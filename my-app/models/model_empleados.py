import os
import re
from conexion.conexionBD import connectionBD

class EmpleadoModel:
    def __init__(self, id_empleados=None, nombre_empleado=None, cargo=None, fecha_ingreso=None, gerencia_asignada=None, estado=1):
        self.__id_empleados = id_empleados
        self.__nombre_empleado = nombre_empleado
        self.__cargo = cargo
        self.__fecha_ingreso = fecha_ingreso
        self.__gerencia_asignada = gerencia_asignada
        self.__estado = estado

    # --- Getters y Setters con validación Regex ---
    def get_id(self): return self.__id_empleados
    def set_id(self, val): self.__id_empleados = val

    def get_nombre(self): return self.__nombre_empleado
    def set_nombre(self, val):
        if not re.match(r"^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{3,45}$", str(val)):
            raise ValueError("Nombre inválido (3-45 caracteres).")
        self.__nombre_empleado = val

    def get_cargo(self): return self.__cargo
    def set_cargo(self, val):
        if not val: raise ValueError("El cargo es obligatorio.")
        self.__cargo = val

    def get_fecha_ingreso(self): return self.__fecha_ingreso
    def set_fecha_ingreso(self, val):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(val)):
            raise ValueError("Formato de fecha inválido.")
        self.__fecha_ingreso = val

    def get_gerencia(self): return self.__gerencia_asignada
    def set_gerencia(self, val):
        if not re.match(r"^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{5,45}$", str(val)):
            raise ValueError("Gerencia inválida (mín. 5 caracteres).")
        self.__gerencia_asignada = val

    # --- Métodos de Persistencia Privados (Seguridad) ---
    def __save_db(self):
        conn = connectionBD()
        cur = conn.cursor()
        try:
            sql = "INSERT INTO empleados (nombre_empleado, cargo, fecha_ingreso, gerencia_asignada, estado) VALUES (%s, %s, %s, %s, 1)"
            cur.execute(sql, (self.__nombre_empleado, self.__cargo, self.__fecha_ingreso, self.__gerencia_asignada))
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()
            conn.close()

    def __update_db(self):
        conn = connectionBD()
        cur = conn.cursor()
        try:
            sql = "UPDATE empleados SET nombre_empleado=%s, cargo=%s, fecha_ingreso=%s, gerencia_asignada=%s WHERE id_empleados=%s"
            cur.execute(sql, (self.__nombre_empleado, self.__cargo, self.__fecha_ingreso, self.__gerencia_asignada, self.__id_empleados))
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()
            conn.close()

    def __delete_logical(self):
        conn = connectionBD()
        cur = conn.cursor()
        try:
            sql = "UPDATE empleados SET estado = 0 WHERE id_empleados = %s"
            cur.execute(sql, (self.__id_empleados,))
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()
            conn.close()

    # --- Métodos Públicos (Interfaz del Modelo) ---
    def get_all_empleados(self):
        conn = connectionBD()
        cur = conn.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM empleados WHERE estado = 1 ORDER BY id_empleados DESC"
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def get_empleado_by_id(self, id_empleado):
        conn = connectionBD()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM empleados WHERE id_empleados = %s AND estado = 1", (id_empleado,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def registrar_empleado(self, data):
        try:
            self.set_nombre(data.get('nombre_empleado'))
            self.set_cargo(data.get('cargo'))
            self.set_fecha_ingreso(data.get('fecha_ingreso'))
            self.set_gerencia(data.get('gerencia_asignada'))
            return self.__save_db()
        except ValueError as e:
            print(f"Error de validación: {e}")
            return 0

    def actualizar_empleado(self, data):
        try:
            self.set_id(data.get('id_empleado'))
            self.set_nombre(data.get('nombre_empleado'))
            self.set_cargo(data.get('cargo'))
            self.set_fecha_ingreso(data.get('fecha_ingreso'))
            self.set_gerencia(data.get('gerencia_asignada'))
            return self.__update_db()
        except ValueError as e:
            print(f"Error de validación: {e}")
            return 0

    def eliminar_empleado_logico(self, id_empleado):
        self.set_id(id_empleado)
        return self.__delete_logical()
