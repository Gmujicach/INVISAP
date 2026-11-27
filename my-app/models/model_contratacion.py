"""
ContratacionModel — Modelo SOLID/POO para gestión de contrataciones.
Implementa encapsulamiento, validaciones Regex, borrado lógico.
"""

import re
from models.base_model import BaseModel


class ContratacionModel(BaseModel):
    """Repositorio de contrataciones con validación y encapsulamiento."""

    _RE_NUMERO_CONTRATO = re.compile(r'^[A-Za-z0-9\-\/\.\#\s]{1,20}$')
    _RE_RIF = re.compile(r'^[A-Za-z0-9\-]{1,12}$')
    _RE_MONTO = re.compile(r'^[\d\.]+$')
    _RE_FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:áéíóúÁÉÍÓÚñÑ]{1,500}$')

    TIPOS_CONTRATO_VALIDOS = {'Contrato de Obra', 'Contrato de Servicio', 'Contrato de Bienes'}
    MODALIDADES_VALIDAS = {'Concurso Abierto', 'Concurso Cerrado', 'Consulta de Precios', 'Contratación Directa'}
    OBJETOS_VALIDOS = {'Ejecución de Obras', 'Prestación de Servicios', 'Suministro de Bienes'}

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_contratacion = None
        self.__descripcion = None
        self.__empresa_ganadora = None
        self.__numero_contrato = None
        self.__monto = None
        self.__fecha_inicio_procedimiento = None
        self.__fecha_adjudicacion = None
        self.__tipo_contrato = None
        self.__modalidad = None
        self.__objeto = None
        self.__observacion = None
        self.__fecha_registro = None
        self.__empresa_rif = None
        self.__estado = 1

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========

    def get_id_contratacion(self):
        return self.__id_contratacion

    def set_id_contratacion(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de contratación debe ser un entero positivo.")
        self.__id_contratacion = valor

    def get_descripcion(self):
        return self.__descripcion

    def set_descripcion(self, valor):
        if not self._validar_texto(valor, 5, 500):
            raise ValueError("Descripción inválida. Mínimo 5, máximo 500 caracteres.")
        self.__descripcion = self._limpiar_texto(valor, 500)

    def get_empresa_ganadora(self):
        return self.__empresa_ganadora

    def set_empresa_ganadora(self, valor):
        if not self._validar_texto(valor, 3, 100):
            raise ValueError("Empresa ganadora inválida. Mínimo 3, máximo 100 caracteres.")
        self.__empresa_ganadora = self._limpiar_texto(valor, 100)

    def get_numero_contrato(self):
        return self.__numero_contrato

    def set_numero_contrato(self, valor):
        if not self._RE_NUMERO_CONTRATO.match(str(valor or '').strip()):
            raise ValueError("Número de contrato inválido. Mínimo 3, máximo 20 caracteres.")
        self.__numero_contrato = valor.strip()[:20]

    def get_monto(self):
        return self.__monto

    def set_monto(self, valor):
        if valor is None or str(valor).strip() == '':
            raise ValueError("Monto es obligatorio.")
        if not self._RE_MONTO.match(str(valor)):
            raise ValueError("Monto inválido. Solo números y punto decimal.")
        self.__monto = str(valor)

    def get_fecha_inicio_procedimiento(self):
        return self.__fecha_inicio_procedimiento

    def set_fecha_inicio_procedimiento(self, valor):
        if not self._validar_fecha(valor):
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")
        self.__fecha_inicio_procedimiento = valor

    def get_fecha_adjudicacion(self):
        return self.__fecha_adjudicacion

    def set_fecha_adjudicacion(self, valor):
        if not self._validar_fecha(valor):
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")
        self.__fecha_adjudicacion = valor

    def get_tipo_contrato(self):
        return self.__tipo_contrato

    def set_tipo_contrato(self, valor):
        if valor not in self.TIPOS_CONTRATO_VALIDOS:
            raise ValueError(f"Tipo de contrato inválido. Permitidos: {', '.join(self.TIPOS_CONTRATO_VALIDOS)}")
        self.__tipo_contrato = valor

    def get_modalidad(self):
        return self.__modalidad

    def set_modalidad(self, valor):
        if valor not in self.MODALIDADES_VALIDAS:
            raise ValueError(f"Modalidad inválida. Permitidas: {', '.join(self.MODALIDADES_VALIDAS)}")
        self.__modalidad = valor

    def get_objeto(self):
        return self.__objeto

    def set_objeto(self, valor):
        if valor not in self.OBJETOS_VALIDOS:
            raise ValueError(f"Objeto inválido. Permitidos: {', '.join(self.OBJETOS_VALIDOS)}")
        self.__objeto = valor

    def get_observacion(self):
        return self.__observacion

    def set_observacion(self, valor):
        self.__observacion = self._limpiar_texto(valor or '', 500)

    def get_fecha_registro(self):
        return self.__fecha_registro

    def set_fecha_registro(self, valor):
        if not self._validar_fecha(valor):
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")
        self.__fecha_registro = valor

    def get_empresa_rif(self):
        return self.__empresa_rif

    def set_empresa_rif(self, valor):
        if not self._RE_RIF.match(str(valor or '').strip()):
            raise ValueError("RIF inválido. Formato: J-12345678-9 o similar.")
        self.__empresa_rif = valor.strip()[:12]

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        self.__estado = 1 if int(valor) else 0

    # ========== MÉTODOS PRIVADOS DE VALIDACIÓN ==========

    def _validar_texto(self, texto, min_len, max_len):
        if not texto or not str(texto).strip():
            return False
        return min_len <= len(str(texto).strip()) <= max_len

    def _validar_fecha(self, fecha):
        return bool(self._RE_FECHA.match(str(fecha or '').strip()))

    def __validar_datos_completos(self):
        if not self.__descripcion or len(self.__descripcion) < 5:
            raise ValueError("La descripción debe tener al menos 5 caracteres.")
        if not self.__numero_contrato or len(self.__numero_contrato) < 3:
            raise ValueError("El número de contrato debe tener al menos 3 caracteres.")
        if self.__tipo_contrato not in self.TIPOS_CONTRATO_VALIDOS:
            raise ValueError("Tipo de contrato no permitido.")
        if self.__modalidad not in self.MODALIDADES_VALIDAS:
            raise ValueError("Modalidad no permitida.")
        if self.__objeto not in self.OBJETOS_VALIDOS:
            raise ValueError("Objeto de contratación no permitido.")
        for campo_fecha in [self.__fecha_inicio_procedimiento, self.__fecha_adjudicacion, self.__fecha_registro]:
            if not self._validar_fecha(campo_fecha):
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========

    def __registrar_contratacion_db(self):
        self.__validar_datos_completos()
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False, "Error de conexión a la base de datos."

        try:
            cursor = conexion.cursor()

            for _ in range(3):
                cursor.execute("SELECT COALESCE(MAX(id_contratacion), 0) + 1 AS siguiente_id FROM contratacion")
                fila = cursor.fetchone()
                siguiente_id = fila[0] if fila else 1

                sql = """INSERT INTO contratacion (
                    id_contratacion, descripcion, empresa_ganadora, numero_contrato, monto,
                    fecha_inicio_procedimiento, fecha_adjudicacion, tipo_contrato,
                    modalidad, objeto, observacion, fecha_registro, empresa_rif, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)"""

                valores = (
                    siguiente_id, self.__descripcion, self.__empresa_ganadora,
                    self.__numero_contrato, self.__monto,
                    self.__fecha_inicio_procedimiento, self.__fecha_adjudicacion,
                    self.__tipo_contrato, self.__modalidad,
                    self.__objeto, self.__observacion,
                    self.__fecha_registro, self.__empresa_rif
                )

                try:
                    cursor.execute(sql, valores)
                    conexion.commit()
                    self.__id_contratacion = cursor.lastrowid
                    return True, "Contratación registrada correctamente."
                except Exception as e:
                    error_msg = str(e)
                    if "1062" in error_msg or "Duplicate" in error_msg:
                        if "PRIMARY" in error_msg or "id_contratacion" in error_msg:
                            continue
                        return False, "El Número de Contrato ya se encuentra registrado."
                    return False, f"Error SQL: {error_msg}"

            return False, "No se pudo registrar la contratación por conflicto de ID."

        except Exception as e:
            print(f"Error registrando contratación: {e}")
            return False, "Error interno al registrar en la base de datos."
        finally:
            if conexion:
                conexion.close()

    def __actualizar_contratacion_db(self):
        self.__validar_datos_completos()
        if not self.__id_contratacion:
            return False, "Falta el ID de la contratación para actualizar."

        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False, "Error de conexión a la base de datos."

        try:
            cursor = conexion.cursor()
            sql = """UPDATE contratacion SET
                descripcion = %s, empresa_ganadora = %s, numero_contrato = %s, monto = %s,
                fecha_inicio_procedimiento = %s, fecha_adjudicacion = %s, tipo_contrato = %s,
                modalidad = %s, objeto = %s, observacion = %s, fecha_registro = %s, empresa_rif = %s
                WHERE id_contratacion = %s AND estado = 1"""

            valores = (
                self.__descripcion, self.__empresa_ganadora,
                self.__numero_contrato, self.__monto,
                self.__fecha_inicio_procedimiento, self.__fecha_adjudicacion,
                self.__tipo_contrato, self.__modalidad,
                self.__objeto, self.__observacion,
                self.__fecha_registro, self.__empresa_rif,
                self.__id_contratacion
            )

            cursor.execute(sql, valores)
            conexion.commit()
            return True, "Contratación modificada correctamente."

        except Exception as e:
            print(f"Error actualizando contratación: {e}")
            return False, "Error interno al actualizar en la base de datos."
        finally:
            if conexion:
                conexion.close()

    def __eliminar_logico_db(self, id_contratacion):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            sql = "UPDATE contratacion SET estado = 0 WHERE id_contratacion = %s"
            cursor.execute(sql, (id_contratacion,))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error eliminando contratación: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    def __obtener_todas_contrataciones_db(self):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT c.*, e.nombre_empresa
                FROM contratacion c
                LEFT JOIN empresa e ON c.empresa_rif = e.rif
                WHERE c.estado = 1
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo contrataciones: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    def __obtener_contratacion_por_id_db(self, id_contratacion):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT * FROM contratacion WHERE id_contratacion = %s AND estado = 1"
            cursor.execute(sql, (id_contratacion,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error obteniendo contratación por ID: {e}")
            return None
        finally:
            if conexion:
                conexion.close()

    def __obtener_empresas_db(self):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT rif, nombre_empresa, cumple_requisitos FROM empresa WHERE estado = 1 AND cumple_requisitos = 1"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo empresas: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    # ========== MÉTODOS PÚBLICOS (Fachada) ==========

    def registrar(self, datos):
        """Método público para registrar contratación."""
        try:
            self.set_descripcion(datos.get('descripcion'))
            self.set_empresa_ganadora(datos.get('empresa_ganadora'))
            self.set_numero_contrato(datos.get('numero_contrato'))
            self.set_monto(datos.get('monto'))
            self.set_fecha_inicio_procedimiento(datos.get('fecha_inicio_procedimiento'))
            self.set_fecha_adjudicacion(datos.get('fecha_adjudicacion'))
            self.set_tipo_contrato(datos.get('tipo_contrato'))
            self.set_modalidad(datos.get('modalidad'))
            self.set_objeto(datos.get('objeto'))
            self.set_observacion(datos.get('observacion'))
            self.set_fecha_registro(datos.get('fecha_registro'))
            self.set_empresa_rif(datos.get('empresa_rif'))
            return self.__registrar_contratacion_db()
        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            print(f"Error inesperado al registrar: {e}")
            return False, "Error interno al registrar."

    def actualizar(self, datos):
        """Método público para actualizar contratación."""
        try:
            self.set_id_contratacion(int(datos.get('id_contratacion')))
            self.set_descripcion(datos.get('descripcion'))
            self.set_empresa_ganadora(datos.get('empresa_ganadora'))
            self.set_numero_contrato(datos.get('numero_contrato'))
            self.set_monto(datos.get('monto'))
            self.set_fecha_inicio_procedimiento(datos.get('fecha_inicio_procedimiento'))
            self.set_fecha_adjudicacion(datos.get('fecha_adjudicacion'))
            self.set_tipo_contrato(datos.get('tipo_contrato'))
            self.set_modalidad(datos.get('modalidad'))
            self.set_objeto(datos.get('objeto'))
            self.set_observacion(datos.get('observacion'))
            self.set_fecha_registro(datos.get('fecha_registro'))
            self.set_empresa_rif(datos.get('empresa_rif'))
            return self.__actualizar_contratacion_db()
        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            print(f"Error inesperado al actualizar: {e}")
            return False, "Error interno al actualizar."

    def eliminar(self, id_contratacion):
        """Método público para borrado lógico de contratación."""
        return self.__eliminar_logico_db(id_contratacion)

    def obtener_todas(self):
        """Método público para obtener todas las contrataciones activas."""
        return self.__obtener_todas_contrataciones_db()

    def obtener_por_id(self, id_contratacion):
        """Método público para obtener contratación por ID."""
        return self.__obtener_contratacion_por_id_db(id_contratacion)

    def obtener_empresas(self):
        """Método público para obtener empresas válidas para contratación."""
        return self.__obtener_empresas_db()

    def validar_numero_contrato_existente(self, numero_contrato, excluir_id=None):
        """Método público para validar número de contrato duplicado."""
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            if excluir_id:
                cursor.execute(
                    "SELECT 1 FROM contratacion WHERE numero_contrato = %s AND id_contratacion != %s AND estado = 1 LIMIT 1",
                    (numero_contrato, excluir_id)
                )
            else:
                cursor.execute(
                    "SELECT 1 FROM contratacion WHERE numero_contrato = %s AND estado = 1 LIMIT 1",
                    (numero_contrato,)
                )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error validando número de contrato: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()