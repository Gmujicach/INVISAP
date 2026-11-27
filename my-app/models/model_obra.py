"""
ObraModel — Modelo SOLID/POO para gestión de obras.
Implementa encapsulamiento, validaciones Regex, borrado lógico y semáforo.
"""

import re
from datetime import datetime
from models.base_model import BaseModel


class ObraModel(BaseModel):
    """Repositorio de obras con validación y encapsulamiento."""

    _RE_NUMERO_CONTRATO = re.compile(r'^[A-Za-z0-9\-\/\.\#\s]{1,20}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:°º²ºáéíóúÁÉÍÓÚñÑ]{1,200}$')
    _RE_TITULO = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:áéíóúÁÉÍÓÚñÑ]{3,45}$', re.UNICODE)
    _RE_UBICACION = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:áéíóúÁÉÍÓÚñÑ]{3,80}$', re.UNICODE)
    _RE_PERIODO = re.compile(r'^[\w\s]{1,10}$')

    _NUMEROS_CONTRATO_PLACEHOLDER = {'N/A', 'NA', 'S/N', 'SN', '-', '0'}

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_obra = None
        self.__titulo_obra = None
        self.__ubicacion_obra = None
        self.__periodo_ejecucion = None
        self.__fecha_inicio = None
        self.__fecha_fin = None
        self.__mediciones_obra = None
        self.__valuaciones = None
        self.__modificaciones_contrato = None
        self.__certificaciones_obras_ejecutadas = 0
        self.__numero_contrato = None
        self.__porcentaje_avance_obra = 0
        self.__estado = 1
        self.__contratacion_id_contratacion = None
        self.__gestionar_proyectos_codigo_proyecto = None
        self.__activo = 1
        self.__asegurar_tabla_obra()

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========

    def get_id_obra(self):
        return self.__id_obra

    def set_id_obra(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de obra debe ser un entero positivo.")
        self.__id_obra = valor

    def get_titulo_obra(self):
        return self.__titulo_obra

    def set_titulo_obra(self, valor):
        if not self._RE_TITULO.match(str(valor or '').strip()):
            raise ValueError("Título de obra inválido. Mínimo 3, máximo 45 caracteres.")
        self.__titulo_obra = self._limpiar_texto(valor, 45)

    def get_ubicacion_obra(self):
        return self.__ubicacion_obra

    def set_ubicacion_obra(self, valor):
        if not self._RE_UBICACION.match(str(valor or '').strip()):
            raise ValueError("Ubicación de obra inválida. Mínimo 3, máximo 80 caracteres.")
        self.__ubicacion_obra = self._limpiar_texto(valor, 80)

    def get_periodo_ejecucion(self):
        return self.__periodo_ejecucion

    def set_periodo_ejecucion(self, valor):
        if not self._RE_PERIODO.match(str(valor or '').strip()):
            raise ValueError("Período de ejecución inválido. Máximo 10 caracteres (ej: '2 meses').")
        self.__periodo_ejecucion = self._limpiar_texto(valor, 10)

    def get_fecha_inicio(self):
        return self.__fecha_inicio

    def set_fecha_inicio(self, valor):
        if not self._validar_fecha(valor):
            raise ValueError("Fecha de inicio inválida. Formato: YYYY-MM-DD.")
        self.__fecha_inicio = valor

    def get_fecha_fin(self):
        return self.__fecha_fin

    def set_fecha_fin(self, valor):
        if not self._validar_fecha(valor):
            raise ValueError("Fecha de fin inválida. Formato: YYYY-MM-DD.")
        self.__fecha_fin = valor

    def get_mediciones_obra(self):
        return self.__mediciones_obra

    def set_mediciones_obra(self, valor):
        if not self._es_texto_valido(valor, 45):
            raise ValueError("Mediciones de obra inválidas. Máximo 45 caracteres.")
        self.__mediciones_obra = self._limpiar_texto(valor, 45)

    def get_valuaciones(self):
        return self.__valuaciones

    def set_valuaciones(self, valor):
        if not self._es_texto_valido(valor, 100):
            raise ValueError("Valuaciones inválidas. Máximo 100 caracteres.")
        self.__valuaciones = self._limpiar_texto(valor, 100)

    def get_modificaciones_contrato(self):
        return self.__modificaciones_contrato

    def set_modificaciones_contrato(self, valor):
        if not self._es_texto_valido(valor, 100):
            raise ValueError("Modificaciones de contrato inválidas. Máximo 100 caracteres.")
        self.__modificaciones_contrato = self._limpiar_texto(valor, 100)

    def get_certificaciones_obras_ejecutadas(self):
        return self.__certificaciones_obras_ejecutadas

    def set_certificaciones_obras_ejecutadas(self, valor):
        try:
            v = int(valor or 0)
            if v < 0:
                raise ValueError
            self.__certificaciones_obras_ejecutadas = v
        except (TypeError, ValueError):
            raise ValueError("Certificaciones ejecutadas debe ser un número entero >= 0.")

    def get_numero_contrato(self):
        return self.__numero_contrato

    def set_numero_contrato(self, valor):
        if not self._RE_NUMERO_CONTRATO.match(str(valor or '').strip()):
            raise ValueError("Número de contrato inválido. Máximo 20 caracteres.")
        self.__numero_contrato = valor.strip()[:20]

    def get_porcentaje_avance_obra(self):
        return self.__porcentaje_avance_obra

    def set_porcentaje_avance_obra(self, valor):
        try:
            v = int(valor or 0)
            if not (0 <= v <= 100):
                raise ValueError
            self.__porcentaje_avance_obra = v
        except (TypeError, ValueError):
            raise ValueError("Porcentaje de avance debe ser un entero entre 0 y 100.")

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        try:
            self.__estado = int(valor)
        except (TypeError, ValueError):
            self.__estado = 1

    def get_contratacion_id_contratacion(self):
        return self.__contratacion_id_contratacion

    def set_contratacion_id_contratacion(self, valor):
        try:
            self.__contratacion_id_contratacion = int(valor) if valor else None
        except (TypeError, ValueError):
            self.__contratacion_id_contratacion = None

    def get_gestionar_proyectos_codigo_proyecto(self):
        return self.__gestionar_proyectos_codigo_proyecto

    def set_gestionar_proyectos_codigo_proyecto(self, valor):
        if valor:
            self.__gestionar_proyectos_codigo_proyecto = str(valor).strip()[:15]
        else:
            self.__gestionar_proyectos_codigo_proyecto = None

    def get_activo(self):
        return self.__activo

    def set_activo(self, valor):
        self.__activo = 1 if int(valor) else 0

    # ========== MÉTODOS PRIVADOS DE VALIDACIÓN ==========

    @staticmethod
    def _es_texto_valido(texto, max_len=100):
        if not texto or not str(texto).strip():
            return False
        texto = str(texto).strip()[:max_len]
        return bool(ObraModel._RE_TEXTO.match(texto))

    @staticmethod
    def _es_numero_contrato_valido(numero):
        if not numero or not str(numero).strip():
            return False
        return bool(ObraModel._RE_NUMERO_CONTRATO.match(str(numero).strip()))

    @staticmethod
    def _validar_fechas(fecha_inicio, fecha_fin):
        def _parse(valor):
            if valor is None:
                return None
            if hasattr(valor, 'year'):
                return valor
            texto = str(valor).strip()[:10]
            if not texto:
                return None
            try:
                return datetime.strptime(texto, '%Y-%m-%d')
            except ValueError:
                return None

        inicio = _parse(fecha_inicio)
        fin = _parse(fecha_fin)
        if inicio is None or fin is None:
            return True
        return fin >= inicio

    @staticmethod
    def _validar_fecha(fecha):
        if not fecha:
            return False
        try:
            datetime.strptime(str(fecha).strip()[:10], '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def __asegurar_tabla_obra(self):
        try:
            conexion = self.obtener_conexion_estricta()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SHOW COLUMNS FROM obra LIKE 'activo'")
                if not cursor.fetchone():
                    cursor.execute(
                        "ALTER TABLE obra ADD COLUMN activo TINYINT NOT NULL DEFAULT 1 "
                        "COMMENT '1=Activo, 0=Inactivo (borrado logico)'"
                    )
                    conexion.commit()
                cursor.close()
                conexion.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla obra: {e}")

    @staticmethod
    def _eliminar_trigger_semaforo():
        conexion = None
        try:
            conexion = ObraModel.obtener_conexion_estricta()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("DROP TRIGGER IF EXISTS actualizar_semaforo_obra")
                conexion.commit()
        except Exception as e:
            print(f"[ObraModel] Error eliminando trigger: {e}")
        finally:
            if conexion:
                conexion.close()

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========

    def __sql_validar_estado(self, id_estado):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM semaforo WHERE id_semaforo = %s AND estado_registro = 1 LIMIT 1", (id_estado,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel] Error validando estado: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_validar_contratacion(self, id_contratacion):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM contratacion WHERE id_contratacion = %s AND estado IN (0,1) LIMIT 1", (id_contratacion,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel] Error validando contratación: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_validar_proyecto(self, codigo_proyecto):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT 1 FROM proyecto WHERE codigo_proyecto = %s AND estado IN (0,1) LIMIT 1", (codigo_proyecto,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel] Error validando proyecto: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_validar_numero_contrato_duplicado(self, numero_contrato, excluir_id_obra=None):
        if str(numero_contrato).strip().upper() in self._NUMEROS_CONTRATO_PLACEHOLDER:
            return False
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            if excluir_id_obra:
                cursor.execute(
                    "SELECT 1 FROM obra WHERE numero_contrato = %s AND id_obra != %s AND estado = 1 LIMIT 1",
                    (numero_contrato, excluir_id_obra)
                )
            else:
                cursor.execute(
                    "SELECT 1 FROM obra WHERE numero_contrato = %s AND estado = 1 LIMIT 1",
                    (numero_contrato,)
                )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel] Error validando número contrato: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_insertar(self, datos):
        # Validaciones
        for campo in ['titulo_obra', 'ubicacion_obra', 'periodo_ejecucion', 'fecha_inicio', 'fecha_fin',
                      'mediciones_obra', 'valuaciones', 'modificaciones_contrato',
                      'certificaciones_obras_ejecutadas', 'numero_contrato', 'porcentaje_avance_obra',
                      'contratacion_id_contratacion', 'gestionar_proyectos_codigo_proyecto']:
            if campo not in datos or datos[campo] is None or str(datos[campo]).strip() == '':
                return False, f"El campo '{campo}' es obligatorio."

        if not self._es_texto_valido(datos.get('titulo_obra'), 45):
            return False, "Título de obra inválido."
        if not self._es_texto_valido(datos.get('ubicacion_obra'), 80):
            return False, "Ubicación de obra inválida."
        if not self._es_numero_contrato_valido(datos.get('numero_contrato')):
            return False, "Número de contrato inválido."
        if not self._es_texto_valido(datos.get('mediciones_obra'), 45):
            return False, "Mediciones de obra inválidas."
        if not self._es_texto_valido(datos.get('valuaciones'), 100):
            return False, "Valuaciones inválidas."
        if not self._es_texto_valido(datos.get('modificaciones_contrato'), 100):
            return False, "Modificaciones de contrato inválidas."
        if not self._es_texto_valido(datos.get('periodo_ejecucion'), 10):
            return False, "Período de ejecución inválido (máximo 10 caracteres, ej. '2 meses')."

        try:
            certificaciones = int(datos.get('certificaciones_obras_ejecutadas') or 0)
            porcentaje = int(datos.get('porcentaje_avance_obra') or 0)
            id_estado = int(datos.get('estado') or 0)
            id_contratacion = int(datos.get('contratacion_id_contratacion') or 0)
        except (TypeError, ValueError):
            return False, "Campos numéricos inválidos."

        if porcentaje < 0 or porcentaje > 100:
            return False, "Porcentaje de avance debe estar entre 0 y 100."
        if certificaciones < 0:
            return False, "Certificaciones ejecutadas debe ser mayor o igual a 0."

        # Auto-calcular estado según porcentaje
        if porcentaje >= 70:
            id_estado = 1
        elif porcentaje >= 30:
            id_estado = 2
        else:
            id_estado = 3

        if not self._validar_fechas(datos.get('fecha_inicio'), datos.get('fecha_fin')):
            return False, "La fecha de fin no puede ser anterior a la fecha de inicio."

        if self.__sql_validar_numero_contrato_duplicado(datos.get('numero_contrato')):
            return False, "El número de contrato ya está registrado en otra obra."

        if not self.__sql_validar_estado(id_estado):
            return False, "El estado seleccionado no existe."
        if not self.__sql_validar_contratacion(id_contratacion):
            return False, "La contratación seleccionada no existe."
        if not self.__sql_validar_proyecto(datos.get('gestionar_proyectos_codigo_proyecto')):
            return False, "El proyecto seleccionado no existe o está inactivo."

        # Asignar a atributos privados
        self.set_titulo_obra(datos.get('titulo_obra'))
        self.set_ubicacion_obra(datos.get('ubicacion_obra'))
        self.set_periodo_ejecucion(datos.get('periodo_ejecucion'))
        self.set_fecha_inicio(datos.get('fecha_inicio'))
        self.set_fecha_fin(datos.get('fecha_fin'))
        self.set_mediciones_obra(datos.get('mediciones_obra'))
        self.set_valuaciones(datos.get('valuaciones'))
        self.set_modificaciones_contrato(datos.get('modificaciones_contrato'))
        self.set_certificaciones_obras_ejecutadas(certificaciones)
        self.set_numero_contrato(datos.get('numero_contrato'))
        self.set_porcentaje_avance_obra(porcentaje)
        self.set_estado(id_estado)
        self.set_contratacion_id_contratacion(id_contratacion)
        self.set_gestionar_proyectos_codigo_proyecto(datos.get('gestionar_proyectos_codigo_proyecto'))

        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False, "Error de conexión a la base de datos."

        try:
            conexion.start_transaction()
            cursor = conexion.cursor()

            sql = """
                INSERT INTO obra (
                    titulo_obra, ubicacion_obra, periodo_ejecucion, fecha_inicio,
                    fecha_fin, mediciones_obra, valuaciones, modificaciones_contrato,
                    certificaciones_obras_ejecutadas, numero_contrato, porcentaje_avance_obra,
                    estado, contratacion_id_contratacion, gestionar_proyectos_codigo_proyecto,
                    activo
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
            """
            valores = (
                self.__titulo_obra,
                self.__ubicacion_obra,
                self.__periodo_ejecucion,
                self.__fecha_inicio,
                self.__fecha_fin,
                self.__mediciones_obra,
                self.__valuaciones,
                self.__modificaciones_contrato,
                self.__certificaciones_obras_ejecutadas,
                self.__numero_contrato,
                self.__porcentaje_avance_obra,
                self.__estado,
                self.__contratacion_id_contratacion,
                self.__gestionar_proyectos_codigo_proyecto
            )

            cursor.execute(sql, valores)
            id_obra = cursor.lastrowid
            conexion.commit()
            self.__id_obra = id_obra
            return True, id_obra
        except Exception as e:
            if conexion:
                try:
                    conexion.rollback()
                except Exception:
                    pass
            print(f"[ObraModel] Error insertando obra: {e}")
            return False, f"Error al registrar obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_actualizar(self, id_obra, datos):
        # Validaciones similares a insertar
        for campo in ['titulo_obra', 'ubicacion_obra', 'periodo_ejecucion', 'fecha_inicio', 'fecha_fin',
                      'mediciones_obra', 'valuaciones', 'modificaciones_contrato',
                      'certificaciones_obras_ejecutadas', 'numero_contrato', 'porcentaje_avance_obra',
                      'contratacion_id_contratacion', 'gestionar_proyectos_codigo_proyecto']:
            if campo not in datos or datos[campo] is None or str(datos[campo]).strip() == '':
                return False, f"El campo '{campo}' es obligatorio."

        if not self._es_texto_valido(datos.get('titulo_obra'), 45):
            return False, "Título de obra inválido."
        if not self._es_texto_valido(datos.get('ubicacion_obra'), 80):
            return False, "Ubicación de obra inválida."
        if not self._es_numero_contrato_valido(datos.get('numero_contrato')):
            return False, "Número de contrato inválido."
        if not self._es_texto_valido(datos.get('mediciones_obra'), 45):
            return False, "Mediciones de obra inválidas."
        if not self._es_texto_valido(datos.get('valuaciones'), 100):
            return False, "Valuaciones inválidas."
        if not self._es_texto_valido(datos.get('modificaciones_contrato'), 100):
            return False, "Modificaciones de contrato inválidas."
        if not self._es_texto_valido(datos.get('periodo_ejecucion'), 10):
            return False, "Período de ejecución inválido (máximo 10 caracteres, ej. '2 meses')."

        try:
            certificaciones = int(datos.get('certificaciones_obras_ejecutadas') or 0)
            porcentaje = int(datos.get('porcentaje_avance_obra') or 0)
            id_estado = int(datos.get('estado') or 0)
            id_contratacion = int(datos.get('contratacion_id_contratacion') or 0)
        except (TypeError, ValueError):
            return False, "Campos numéricos inválidos."

        if porcentaje < 0 or porcentaje > 100:
            return False, "Porcentaje de avance debe estar entre 0 y 100."
        if certificaciones < 0:
            return False, "Certificaciones ejecutadas debe ser mayor o igual a 0."

        # Auto-calcular estado según porcentaje
        if porcentaje >= 70:
            id_estado = 1
        elif porcentaje >= 30:
            id_estado = 2
        else:
            id_estado = 3

        if not self._validar_fechas(datos.get('fecha_inicio'), datos.get('fecha_fin')):
            return False, "La fecha de fin no puede ser anterior a la fecha de inicio."

        numero_contrato = str(datos.get('numero_contrato')).strip()[:20]
        if self.__sql_validar_numero_contrato_duplicado(numero_contrato, excluir_id_obra=id_obra):
            return False, "El número de contrato ya está registrado en otra obra."

        if not self.__sql_validar_estado(id_estado):
            return False, "El estado seleccionado no existe."
        if not self.__sql_validar_contratacion(id_contratacion):
            return False, "La contratación seleccionada no existe."
        if not self.__sql_validar_proyecto(datos.get('gestionar_proyectos_codigo_proyecto')):
            return False, "El proyecto seleccionado no existe o está inactivo."

        # Asignar a atributos privados
        self.set_titulo_obra(datos.get('titulo_obra'))
        self.set_ubicacion_obra(datos.get('ubicacion_obra'))
        self.set_periodo_ejecucion(datos.get('periodo_ejecucion'))
        self.set_fecha_inicio(datos.get('fecha_inicio'))
        self.set_fecha_fin(datos.get('fecha_fin'))
        self.set_mediciones_obra(datos.get('mediciones_obra'))
        self.set_valuaciones(datos.get('valuaciones'))
        self.set_modificaciones_contrato(datos.get('modificaciones_contrato'))
        self.set_certificaciones_obras_ejecutadas(certificaciones)
        self.set_numero_contrato(numero_contrato)
        self.set_porcentaje_avance_obra(porcentaje)
        self.set_estado(id_estado)
        self.set_contratacion_id_contratacion(id_contratacion)
        self.set_gestionar_proyectos_codigo_proyecto(datos.get('gestionar_proyectos_codigo_proyecto'))

        self._eliminar_trigger_semaforo()
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False, "Error de conexión a la base de datos."

        try:
            conexion.start_transaction()
            cursor = conexion.cursor()

            sql = """
                UPDATE obra SET
                    titulo_obra = %s, ubicacion_obra = %s, periodo_ejecucion = %s,
                    fecha_inicio = %s, fecha_fin = %s, mediciones_obra = %s,
                    valuaciones = %s, modificaciones_contrato = %s,
                    certificaciones_obras_ejecutadas = %s, numero_contrato = %s,
                    porcentaje_avance_obra = %s, estado = %s,
                    contratacion_id_contratacion = %s, gestionar_proyectos_codigo_proyecto = %s
                WHERE id_obra = %s AND activo = 1
            """
            valores = (
                self.__titulo_obra,
                self.__ubicacion_obra,
                self.__periodo_ejecucion,
                self.__fecha_inicio,
                self.__fecha_fin,
                self.__mediciones_obra,
                self.__valuaciones,
                self.__modificaciones_contrato,
                self.__certificaciones_obras_ejecutadas,
                self.__numero_contrato,
                self.__porcentaje_avance_obra,
                self.__estado,
                self.__contratacion_id_contratacion,
                self.__gestionar_proyectos_codigo_proyecto,
                id_obra
            )

            cursor.execute(sql, valores)
            conexion.commit()
            return True, cursor.rowcount
        except Exception as e:
            if conexion:
                try:
                    conexion.rollback()
                except Exception:
                    pass
            print(f"[ObraModel] Error actualizando obra: {e}")
            return False, f"Error al actualizar obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_eliminar(self, id_obra):
        self._eliminar_trigger_semaforo()
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False, "Error de conexión a la base de datos."

        try:
            conexion.start_transaction()
            cursor = conexion.cursor()

            cursor.execute("SELECT id_obra FROM obra WHERE id_obra = %s AND estado = 1", (id_obra,))
            if not cursor.fetchone():
                return False, "La obra no existe o ya fue eliminada."

            cursor.execute("UPDATE obra SET estado = 0 WHERE id_obra = %s AND estado = 1", (id_obra,))
            conexion.commit()
            return True, cursor.rowcount
        except Exception as e:
            if conexion:
                try:
                    conexion.rollback()
                except Exception:
                    pass
            print(f"[ObraModel] Error eliminando obra: {e}")
            return False, f"Error al eliminar obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_obtener_todas(self):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT o.*, s.color, s.descripcion
                FROM obra o
                LEFT JOIN semaforo s ON o.estado = s.id_semaforo
                WHERE o.activo = 1
                ORDER BY o.id_obra DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel] Error obteniendo obras: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_obtener_por_id(self, id_obra):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT o.*, s.color, s.descripcion
                FROM obra o
                LEFT JOIN semaforo s ON o.estado = s.id_semaforo
                WHERE o.id_obra = %s AND o.activo = 1
            """
            cursor.execute(sql, (id_obra,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[ObraModel] Error obteniendo obra por ID: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_listar_estados(self):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_semaforo, color, descripcion AS nombre FROM semaforo WHERE estado_registro = 1")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel] Error listando estados: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_listar_contrataciones(self):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_contratacion, numero_contrato, empresa_ganadora FROM contratacion WHERE estado IN (0,1) ORDER BY id_contratacion DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel] Error listando contrataciones: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_listar_proyectos(self):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT codigo_proyecto, descripcion_tecnica, fecha_planificacion FROM proyecto WHERE estado IN (0,1) ORDER BY codigo_proyecto DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel] Error listando proyectos: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __sql_obtener_avances_por_obra(self, id_obra):
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return []
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = """
                SELECT a.*, i.fecha AS fecha_informe, i.tipo_informe
                FROM avance a
                LEFT JOIN informe_avance_obra i ON a.id_avance = i.avance_id_avance
                WHERE a.obra_id_obra = %s
                ORDER BY a.fecha_avance DESC
            """
            cursor.execute(sql, (id_obra,))
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel] Error obteniendo avances por obra: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    # ========== MÉTODOS PÚBLICOS (Fachada) ==========

    def registrar(self, datos):
        """Método público para registrar obra."""
        return self.__sql_insertar(datos)

    def actualizar(self, id_obra, datos):
        """Método público para actualizar obra."""
        return self.__sql_actualizar(id_obra, datos)

    def eliminar(self, id_obra):
        """Método público para borrado lógico de obra."""
        return self.__sql_eliminar(id_obra)

    def obtener_todas(self):
        """Método público para obtener todas las obras activas."""
        return self.__sql_obtener_todas()

    def obtener_por_id(self, id_obra):
        """Método público para obtener obra por ID."""
        return self.__sql_obtener_por_id(id_obra)

    def obtener_avances_por_obra(self, id_obra):
        """Método público para obtener los avances registrados de una obra."""
        return self.__sql_obtener_avances_por_obra(id_obra)

    def validar_estado(self, id_estado):
        """Método público para validar estado de semáforo."""
        return self.__sql_validar_estado(id_estado)

    def validar_contratacion(self, id_contratacion):
        """Método público para validar contratación."""
        return self.__sql_validar_contratacion(id_contratacion)

    def validar_proyecto(self, codigo_proyecto):
        """Método público para validar proyecto."""
        return self.__sql_validar_proyecto(codigo_proyecto)

    def listar_estados(self):
        """Método público para listar estados de semáforo."""
        return self.__sql_listar_estados()

    def listar_contrataciones(self):
        """Método público para listar contrataciones."""
        return self.__sql_listar_contrataciones()

    def listar_proyectos(self):
        """Método público para listar proyectos."""
        return self.__sql_listar_proyectos()

    def validar_numero_contrato(self, numero_contrato, excluir_id=None):
        """Método público para validar número de contrato duplicado."""
        return self.__sql_validar_numero_contrato_duplicado(numero_contrato, excluir_id)


def asegurar_tabla_obra():
    """Asegura que la columna 'activo' exista en la tabla obra.

    Función de compatibilidad: instancia ObraModel, cuyo __init__ ejecuta la
    verificación/ALTER de la columna 'activo'.
    """
    ObraModel()