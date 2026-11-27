"""
MaquinariaModel — Modelo SOLID/POO para gestión de maquinaria.
Implementa encapsulamiento, validaciones Regex, borrado lógico.
"""

import re
from models.base_model import BaseModel


class MaquinariaModel(BaseModel):
    """Repositorio de maquinaria con validación y encapsulamiento."""

    _RE_NOMBRE = re.compile(r'^[\w\s\.\-áéíóúÁÉÍÓÚñÑ]{3,50}$', re.UNICODE)
    _TIPOS_VALIDOS = {'Pesada', 'Liviana', 'Herramienta', 'Vehículo'}

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_maquinaria = None
        self.__nombre_maquinaria = None
        self.__tipo_maquinaria = None
        self.__estado = 1
        self.__asegurar_tabla_maquinaria()

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========

    def get_id_maquinaria(self):
        return self.__id_maquinaria

    def set_id_maquinaria(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de maquinaria debe ser un entero positivo.")
        self.__id_maquinaria = valor

    def get_nombre_maquinaria(self):
        return self.__nombre_maquinaria

    def set_nombre_maquinaria(self, valor):
        if not self._validar_nombre(valor):
            raise ValueError("Nombre inválido. Mínimo 3, máximo 50 caracteres, sin caracteres especiales.")
        self.__nombre_maquinaria = self._limpiar_texto(valor, 50)

    def get_tipo_maquinaria(self):
        return self.__tipo_maquinaria

    def set_tipo_maquinaria(self, valor):
        if valor not in self._TIPOS_VALIDOS:
            raise ValueError(f"Tipo inválido. Valores permitidos: {', '.join(self._TIPOS_VALIDOS)}")
        self.__tipo_maquinaria = valor

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 (inactivo) o 1 (activo).")
        self.__estado = valor

    # ========== MÉTODOS PRIVADOS DE VALIDACIÓN ==========

    def _validar_nombre(self, nombre):
        return bool(self._RE_NOMBRE.match(str(nombre or '').strip()))

    def _validar_tipo(self, tipo):
        return tipo in self._TIPOS_VALIDOS

    def __asegurar_tabla_maquinaria(self):
        try:
            conexion = self.obtener_conexion_estricta()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SHOW COLUMNS FROM maquinaria LIKE 'estado'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE maquinaria ADD COLUMN estado TINYINT NOT NULL DEFAULT 1")
                    conexion.commit()
                cursor.close()
                conexion.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla maquinaria: {e}")

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========

    def __obtener_maquinarias_db(self, page=1, per_page=10):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            offset = (page - 1) * per_page
            cursor.execute("SELECT * FROM maquinaria WHERE estado = 1 ORDER BY id_maquinaria DESC LIMIT %s OFFSET %s", (per_page, offset))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo maquinarias: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __contar_maquinarias_db(self):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM maquinaria WHERE estado = 1")
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error contando maquinarias: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __obtener_maquinarias_eliminadas_db(self):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinaria WHERE estado = 0 ORDER BY id_maquinaria DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo maquinarias eliminadas: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __restaurar_maquinaria_db(self, id_maquinaria):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE maquinaria SET estado = 1 WHERE id_maquinaria = %s AND estado = 0", (id_maquinaria,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error restaurando maquinaria: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __registrar_maquinaria_db(self):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_maquinaria, estado FROM maquinaria WHERE nombre_maquinaria = %s", (self.__nombre_maquinaria.strip(),))
            existe = cursor.fetchone()

            if existe:
                if existe['estado'] == 1:
                    return {'success': False, 'message': 'Esta maquinaria ya está registrada.'}
                else:
                    cursor.execute("UPDATE maquinaria SET estado = 1 WHERE id_maquinaria = %s", (existe['id_maquinaria'],))
                    conexion.commit()
                    return {'success': True, 'id': existe['id_maquinaria'], 'restaurada': True, 'message': 'Maquinaria restaurada correctamente'}

            for _ in range(3):
                cursor.execute("SELECT COALESCE(MAX(id_maquinaria), 0) + 1 AS siguiente_id FROM maquinaria")
                fila = cursor.fetchone()
                siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)

                sql = "INSERT INTO maquinaria (id_maquinaria, nombre_maquinaria, tipo_maquinaria, estado) VALUES (%s, %s, %s, 1)"
                try:
                    cursor.execute(sql, (siguiente_id, self.__nombre_maquinaria.strip(), self.__tipo_maquinaria))
                    conexion.commit()
                    return {'success': True, 'id': cursor.lastrowid, 'message': 'Maquinaria registrada correctamente'}
                except Exception as e:
                    error_code = getattr(e, 'errno', None)
                    if error_code is None and e.args:
                        error_code = e.args[0]
                    if error_code != 1062:
                        raise
                    conexion.rollback()
            raise ValueError("No se pudo reservar un ID único para maquinaria tras 3 intentos")
        except Exception as e:
            print(f"Error registrando maquinaria: {e}")
            return {'success': False, 'message': f'Error al registrar en la base de datos: {str(e)}'}
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __obtener_maquinaria_por_id_db(self, id_maquinaria):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinaria WHERE id_maquinaria = %s", (id_maquinaria,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo maquinaria por ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __actualizar_maquinaria_db(self, id_maquinaria):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = "UPDATE maquinaria SET nombre_maquinaria = %s, tipo_maquinaria = %s WHERE id_maquinaria = %s"
            cursor.execute(sql, (self.__nombre_maquinaria.strip(), self.__tipo_maquinaria, id_maquinaria))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error actualizando maquinaria: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    def __eliminar_maquinaria_db(self, id_maquinaria):
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM proyecto_has_maquinaria WHERE maquinaria_id_maquinaria = %s", (id_maquinaria,))
            result = cursor.fetchone()
            count = result['count'] if isinstance(result, dict) else result[0]
            if count > 0:
                return "utilizada"
            cursor.execute("UPDATE maquinaria SET estado = 0 WHERE id_maquinaria = %s", (id_maquinaria,))
            conexion.commit()
            return "eliminada"
        except Exception as e:
            print(f"Error eliminando maquinaria: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conexion.close()

    # ========== MÉTODOS PÚBLICOS (Fachada) ==========

    def obtener_todos(self, page=1, per_page=10):
        """Método público para obtener maquinarias activas paginadas."""
        return self.__obtener_maquinarias_db(page, per_page)

    def contar(self):
        """Método público para contar maquinarias activas."""
        return self.__contar_maquinarias_db()

    def obtener_eliminadas(self):
        """Método público para obtener maquinarias eliminadas."""
        return self.__obtener_maquinarias_eliminadas_db()

    def restaurar(self, id_maquinaria):
        """Método público para restaurar maquinaria eliminada."""
        return self.__restaurar_maquinaria_db(id_maquinaria)

    def registrar(self, nombre, tipo):
        """Método público para registrar maquinaria."""
        if not self._validar_nombre(nombre):
            return {'success': False, 'message': 'El nombre es requerido (mín 3, máx 50 chars).'}
        if not self._validar_tipo(tipo):
            return {'success': False, 'message': 'Debe seleccionar un tipo válido.'}
        self.set_nombre_maquinaria(nombre)
        self.set_tipo_maquinaria(tipo)
        return self.__registrar_maquinaria_db()

    def obtener_por_id(self, id_maquinaria):
        """Método público para obtener maquinaria por ID."""
        return self.__obtener_maquinaria_por_id_db(id_maquinaria)

    def actualizar(self, id_maquinaria, nombre, tipo):
        """Método público para actualizar maquinaria."""
        if not self._validar_nombre(nombre):
            return {'success': False, 'message': 'El nombre es requerido (mín 3, máx 50 chars).'}
        if not self._validar_tipo(tipo):
            return {'success': False, 'message': 'Debe seleccionar un tipo válido.'}
        self.set_nombre_maquinaria(nombre)
        self.set_tipo_maquinaria(tipo)
        return self.__actualizar_maquinaria_db(id_maquinaria)

    def eliminar(self, id_maquinaria):
        """Método público para borrado lógico de maquinaria."""
        return self.__eliminar_maquinaria_db(id_maquinaria)

    def validar_nombre_existente(self, nombre, excluir_id=None):
        """Método público para validar si existe nombre (para AJAX)."""
        conexion = self.obtener_conexion_estricta()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            if excluir_id:
                cursor.execute("SELECT 1 FROM maquinaria WHERE nombre_maquinaria = %s AND id_maquinaria != %s AND estado = 1 LIMIT 1", (nombre.strip(), excluir_id))
            else:
                cursor.execute("SELECT 1 FROM maquinaria WHERE nombre_maquinaria = %s AND estado = 1 LIMIT 1", (nombre.strip(),))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error validando nombre: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conexion.close()