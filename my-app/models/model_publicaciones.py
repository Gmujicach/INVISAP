"""
PublicacionModel — Modelo SOLID/POO para gestión de publicaciones.
Implementa encapsulamiento, validaciones Regex y acceso a BD.
"""

import re
from models.base_model import BaseModel


class PublicacionModel(BaseModel):
    """Repositorio de publicaciones con validación y encapsulamiento."""

    _RE_TITULO = re.compile(r'^[\w\s\.\-áéíóúÁÉÍÓÚñÑ]{3,100}$', re.UNICODE)
    _TIPOS_VALIDOS = {'Obra', 'Informe', 'Noticia', 'Anuncio'}

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_publicacion = None
        self.__titulo_publicacion = None
        self.__nombre_responsable = None
        self.__tipo_publicacion = None
        self.__fecha_publicacion = None
        self.__informe_avance_obra_id_informe = None
        self.__cuerpo_publicacion = 'Contenido pendiente'
        self.__estado = 1
        self.__asegurar_tabla_publicaciones()

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========

    def get_id_publicacion(self):
        return self.__id_publicacion

    def set_id_publicacion(self, valor):
        if valor is not None and (not isinstance(valor, int) or valor <= 0):
            raise ValueError("ID de publicación debe ser un entero positivo.")
        self.__id_publicacion = valor

    def get_titulo_publicacion(self):
        return self.__titulo_publicacion

    def set_titulo_publicacion(self, valor):
        if not self._validar_titulo(valor):
            raise ValueError("Título inválido. Mínimo 3, máximo 100 caracteres.")
        self.__titulo_publicacion = self._limpiar_texto(valor, 100)

    def get_nombre_responsable(self):
        return self.__nombre_responsable

    def set_nombre_responsable(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("El nombre del responsable es requerido.")
        self.__nombre_responsable = str(valor).strip()

    def get_tipo_publicacion(self):
        return self.__tipo_publicacion

    def set_tipo_publicacion(self, valor):
        if valor not in self._TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(self._TIPOS_VALIDOS)}")
        self.__tipo_publicacion = valor

    def get_fecha_publicacion(self):
        return self.__fecha_publicacion

    def set_fecha_publicacion(self, valor):
        if not valor or not str(valor).strip():
            raise ValueError("La fecha de publicación es requerida.")
        self.__fecha_publicacion = str(valor).strip()

    def get_informe_avance_obra_id_informe(self):
        return self.__informe_avance_obra_id_informe

    def set_informe_avance_obra_id_informe(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de informe debe ser un entero positivo.")
        self.__informe_avance_obra_id_informe = valor

    def get_cuerpo_publicacion(self):
        return self.__cuerpo_publicacion

    def set_cuerpo_publicacion(self, valor):
        self.__cuerpo_publicacion = valor if valor is not None else 'Contenido pendiente'

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 (inactivo) o 1 (activo).")
        self.__estado = valor

    # ========== MÉTODOS PRIVADOS DE VALIDACIÓN ==========

    def _validar_titulo(self, titulo):
        return bool(self._RE_TITULO.match(str(titulo or '').strip()))

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========

    def __asegurar_tabla_publicaciones(self):
        try:
            conexion = self.obtener_conexion()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SHOW COLUMNS FROM publicacion LIKE 'estado'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE publicacion ADD COLUMN estado TINYINT NOT NULL DEFAULT 1")
                    conexion.commit()
                cursor.close()
                conexion.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla publicaciones: {e}")

    def __obtener_todas_las_publicaciones_db(self):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM publicacion ORDER BY fecha_publicacion DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_todas_las_publicaciones: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __registrar_publicacion_db(self):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor()
            for _ in range(3):
                cursor.execute("SELECT COALESCE(MAX(id_publicacion), 0) + 1 AS siguiente_id FROM publicacion")
                fila = cursor.fetchone()
                siguiente_id = fila[0] if fila else 1

                sql = """INSERT INTO publicacion 
                         (id_publicacion, titulo_publicacion, nombre_responsable, tipo_publicacion, fecha_publicacion, informe_avance_obra_id_informe, estado, cuerpo_publicacion)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                valores = (
                    siguiente_id,
                    self.__titulo_publicacion,
                    self.__nombre_responsable,
                    self.__tipo_publicacion,
                    self.__fecha_publicacion,
                    self.__informe_avance_obra_id_informe,
                    1,
                    self.__cuerpo_publicacion,
                )
                try:
                    cursor.execute(sql, valores)
                    conexion.commit()
                    return cursor.rowcount
                except Exception as e:
                    error_code = getattr(e, 'errno', None)
                    if error_code is None and e.args:
                        error_code = e.args[0]
                    if error_code != 1062:
                        raise
                    conexion.rollback()
            raise ValueError("No se pudo reservar un ID único para publicacion tras 3 intentos")
        except Exception as e:
            print(f"Error en registrar_publicacion: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __obtener_publicacion_por_id_db(self, id_publicacion):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT *, cuerpo_publicacion FROM publicacion WHERE id_publicacion = %s", (id_publicacion,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en obtener_publicacion_por_id: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __actualizar_publicacion_db(self, id_publicacion):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = """UPDATE publicacion 
                     SET titulo_publicacion=%s, nombre_responsable=%s, tipo_publicacion=%s, informe_avance_obra_id_informe=%s, cuerpo_publicacion=%s
                     WHERE id_publicacion=%s"""
            valores = (
                self.__titulo_publicacion,
                self.__nombre_responsable,
                self.__tipo_publicacion,
                self.__informe_avance_obra_id_informe,
                self.__cuerpo_publicacion,
                id_publicacion,
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en actualizar_publicacion: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __eliminar_publicacion_db(self, id_publicacion):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM publicacion WHERE id_publicacion = %s", (id_publicacion,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en eliminar_publicacion: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __obtener_informes_para_publicaciones_db(self):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_informe, tipo_informe AS nombre_proyecto FROM informe_avance_obra")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_informes_para_publicaciones: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __validar_informe_activo_db(self, id_informe):
        conexion = self.obtener_conexion()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM informe_avance_obra WHERE id_informe = %s", (id_informe,))
            result = cursor.fetchone()
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"Error en validar_informe_activo: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    # ========== MÉTODOS PÚBLICOS (Fachada) ==========

    def obtener_todas_las_publicaciones(self):
        """Método público para obtener todas las publicaciones."""
        return self.__obtener_todas_las_publicaciones_db()

    def registrar_publicacion(self, data):
        """Método público para registrar una publicación."""
        self.set_titulo_publicacion(data['titulo_publicacion'])
        self.set_nombre_responsable(data['nombre_responsable'])
        self.set_tipo_publicacion(data['tipo_publicacion'])
        self.set_fecha_publicacion(data['fecha_publicacion'])
        self.set_informe_avance_obra_id_informe(data['informe_avance_obra_id_informe'])
        self.set_cuerpo_publicacion(data.get('cuerpo_publicacion', 'Contenido pendiente'))
        return self.__registrar_publicacion_db()

    def obtener_publicacion_por_id(self, id_publicacion):
        """Método público para obtener una publicación por ID."""
        return self.__obtener_publicacion_por_id_db(id_publicacion)

    def actualizar_publicacion(self, id_publicacion, data):
        """Método público para actualizar una publicación."""
        self.set_titulo_publicacion(data['titulo_publicacion'])
        self.set_nombre_responsable(data['nombre_responsable'])
        self.set_tipo_publicacion(data['tipo_publicacion'])
        self.set_fecha_publicacion(data['fecha_publicacion'])
        self.set_informe_avance_obra_id_informe(data['informe_avance_obra_id_informe'])
        self.set_cuerpo_publicacion(data.get('cuerpo_publicacion', 'Contenido pendiente'))
        return self.__actualizar_publicacion_db(id_publicacion)

    def eliminar_publicacion(self, id_publicacion):
        """Método público para eliminar una publicación."""
        return self.__eliminar_publicacion_db(id_publicacion)

    def obtener_informes_para_publicaciones(self):
        """Método público para obtener informes para publicaciones."""
        return self.__obtener_informes_para_publicaciones_db()

    def validar_informe_activo(self, id_informe):
        """Método público para validar si un informe está activo."""
        return self.__validar_informe_activo_db(id_informe)
