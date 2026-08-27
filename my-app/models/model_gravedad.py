import re
from conexion.conexionBD import connectionBD
from models.base_model import BaseModel


class GravedadObraModel(BaseModel):
    def __init__(self, nivel_gravedad=None, criticidad=None, estado=1, id_gravedad=None):
        # Atributos privados (Encapsulamiento - POO)
        self.__id_gravedad = id_gravedad
        self.__nivel_gravedad = nivel_gravedad
        self.__criticidad = criticidad
        self.__estado = estado

    # Getters
    def get_id(self):
        return self.__id_gravedad

    def get_nivel_gravedad(self):
        return self.__nivel_gravedad

    def get_criticidad(self):
        return self.__criticidad

    # Setters con validación (Backend robusto - Prof. Escalona)
    def set_nivel_gravedad(self, valor):
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,20}$', str(valor or '').strip()):
            raise ValueError("Formato de gravedad inválido. Solo letras y espacios (3-20 caracteres).")
        self.__nivel_gravedad = valor.strip()

    def set_criticidad(self, valor):
        try:
            v = int(float(valor))
        except (TypeError, ValueError):
            raise ValueError("La criticidad debe ser un número entero entre 0 y 100.")
        if not (0 <= v <= 100):
            raise ValueError("La criticidad debe estar entre 0 y 100.")
        self.__criticidad = v

    # ----- Métodos de persistencia (la conexión se abre y cierra por consulta) -----
    def registrar_gravedad(self):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COALESCE(MAX(id_gravedad), 0) + 1 AS siguiente_id FROM gravedad_obra")
            fila = cursor.fetchone()
            siguiente_id = fila[0] if fila else 1

            sql = """INSERT INTO gravedad_obra (id_gravedad, nivel_gravedad, criticidad, estado)
                     VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (siguiente_id, self.__nivel_gravedad, self.__criticidad, self.__estado))
            conexion.commit()
            return siguiente_id
        finally:
            cursor.close()
            conexion.close()

    def consultar_activos(self):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_gravedad, nivel_gravedad, criticidad, estado "
                "FROM gravedad_obra WHERE estado = 1 ORDER BY id_gravedad ASC"
            )
            filas = cursor.fetchall()
            for f in filas:
                try:
                    c = float(f.get('criticidad'))
                    if c <= 1:
                        f['criticidad'] = int(round(c * 100))
                    else:
                        f['criticidad'] = int(c)
                except Exception:
                    f['criticidad'] = 0
                nivel = (f.get('nivel_gravedad') or '').strip().lower()
                if nivel in ('baja', 'bajo'):
                    f['nivel_gravedad'] = 'Bajo'
                elif nivel in ('media', 'alto'):
                    f['nivel_gravedad'] = 'Alto'
            return filas
        finally:
            cursor.close()
            conexion.close()

    def obtener_gravedad_por_id(self, id_gravedad):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_gravedad, nivel_gravedad, criticidad, estado "
                "FROM gravedad_obra WHERE id_gravedad = %s", (id_gravedad,)
            )
            fila = cursor.fetchone()
            if fila:
                try:
                    c = float(fila.get('criticidad'))
                    if c <= 1:
                        fila['criticidad'] = int(round(c * 100))
                    else:
                        fila['criticidad'] = int(c)
                except Exception:
                    fila['criticidad'] = 0
                nivel = (fila.get('nivel_gravedad') or '').strip().lower()
                if nivel in ('baja', 'bajo'):
                    fila['nivel_gravedad'] = 'Bajo'
                elif nivel in ('media', 'alto'):
                    fila['nivel_gravedad'] = 'Alto'
            return fila
        finally:
            cursor.close()
            conexion.close()

    def actualizar_gravedad(self):
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            sql = """UPDATE gravedad_obra
                     SET nivel_gravedad = %s, criticidad = %s, estado = %s
                     WHERE id_gravedad = %s"""
            cursor.execute(sql, (self.__nivel_gravedad, self.__criticidad,
                                 self.__estado, self.__id_gravedad))
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conexion.close()

    def eliminar_gravedad(self):
        """Borrado lógico exigido por el Prof. Escalona (estado = 0)."""
        conexion = connectionBD()
        try:
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE gravedad_obra SET estado = 0 WHERE id_gravedad = %s",
                (self.__id_gravedad,)
            )
            conexion.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conexion.close()

    def validar_nivel_existente(self, excluir_id=None):
        """Validación de existencia en tiempo real (change en el frontend)."""
        conexion = connectionBD()
        try:
            cursor = conexion.cursor(dictionary=True)
            if excluir_id:
                cursor.execute(
                    "SELECT 1 FROM gravedad_obra WHERE nivel_gravedad = %s "
                    "AND id_gravedad <> %s AND estado = 1 LIMIT 1",
                    (self.__nivel_gravedad, excluir_id)
                )
            else:
                cursor.execute(
                    "SELECT 1 FROM gravedad_obra WHERE nivel_gravedad = %s "
                    "AND estado = 1 LIMIT 1",
                    (self.__nivel_gravedad,)
                )
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conexion.close()
