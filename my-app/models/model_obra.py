from conexion.conexionBD import connectionBD
from models.base_model import BaseModel
import re


class ObraModel(BaseModel):
    _RE_NUMERO_CONTRATO = re.compile(r'^[A-Za-z0-9\-\/\.\#\s]{1,20}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:°º²ºáéíóúÁÉÍÓÚñÑ]{1,200}$')

    @staticmethod
    def _con():
        return connectionBD()

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
        """Valida que la fecha de fin no sea anterior a la de inicio.

        Retorna True cuando las fechas son válidas o cuando alguna no puede
        interpretarse (la validación estricta de formato la realiza MySQL).
        """
        from datetime import datetime

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
    def _eliminar_trigger_semaforo():
        conn = None
        try:
            conn = connectionBD()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DROP TRIGGER IF EXISTS actualizar_semaforo_obra")
                conn.commit()
        except Exception as e:
            print(f"[ObraModel._eliminar_trigger_semaforo] Error: {e}")
        finally:
            if conn:
                conn.close()

    def _sql_obtener_todas(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return []
            cursor = conn.cursor(dictionary=True)
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
            print(f"[ObraModel._sql_obtener_todas] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_obtener_por_id(self, id_obra: int) -> dict:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return None
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT o.*, s.color, s.descripcion 
                FROM obra o
                LEFT JOIN semaforo s ON o.estado = s.id_semaforo
                WHERE o.id_obra = %s AND o.activo = 1
            """
            cursor.execute(sql, (id_obra,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[ObraModel._sql_obtener_por_id] Error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_validar_estado(self, id_estado) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM semaforo WHERE id_semaforo = %s AND estado_registro = 1 LIMIT 1", (id_estado,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel._sql_validar_estado] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_validar_contratacion(self, id_contratacion) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM contratacion WHERE id_contratacion = %s AND estado IN (0,1) LIMIT 1", (id_contratacion,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel._sql_validar_contratacion] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_validar_proyecto(self, codigo_proyecto) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return False
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM proyecto WHERE codigo_proyecto = %s AND estado IN (0,1) LIMIT 1", (codigo_proyecto,))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"[ObraModel._sql_validar_proyecto] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Valores genéricos que no deben tratarse como número de contrato único
    _NUMEROS_CONTRATO_PLACEHOLDER = {'N/A', 'NA', 'S/N', 'SN', '-', '0'}

    def _sql_validar_numero_contrato_duplicado(self, numero_contrato: str, excluir_id_obra: int = None) -> bool:
        # Los valores placeholder (N/A, S/N, etc.) pueden repetirse sin ser duplicados reales.
        if str(numero_contrato).strip().upper() in self._NUMEROS_CONTRATO_PLACEHOLDER:
            return False
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return False
            cursor = conn.cursor()
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
            print(f"[ObraModel._sql_validar_numero_contrato_duplicado] Error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_insertar(self, datos: dict) -> tuple:
        conn = cursor = None
        try:
            campos_requeridos = [
                'titulo_obra', 'ubicacion_obra', 'periodo_ejecucion',
                'fecha_inicio', 'fecha_fin', 'mediciones_obra',
                'valuaciones', 'modificaciones_contrato',
                'certificaciones_obras_ejecutadas', 'numero_contrato',
                'porcentaje_avance_obra',
                'contratacion_id_contratacion', 'gestionar_proyectos_codigo_proyecto'
            ]

            for campo in campos_requeridos:
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
                id_estado_manual = int(datos.get('estado') or 0)
                id_contratacion = int(datos.get('contratacion_id_contratacion') or 0)
            except (TypeError, ValueError):
                return False, "Campos numéricos inválidos. Verifique certificaciones, avance, estado y contratación."

            if porcentaje < 0 or porcentaje > 100:
                return False, "Porcentaje de avance debe estar entre 0 y 100."
            if certificaciones < 0:
                return False, "Certificaciones ejecutadas debe ser mayor o igual a 0."

            if porcentaje >= 70:
                id_estado = 1
            elif porcentaje >= 30:
                id_estado = 2
            else:
                id_estado = 3

            if not self._validar_fechas(datos.get('fecha_inicio'), datos.get('fecha_fin')):
                return False, "La fecha de fin no puede ser anterior a la fecha de inicio."

            if self._sql_validar_numero_contrato_duplicado(datos.get('numero_contrato')):
                return False, "El número de contrato ya está registrado en otra obra."

            if not self._sql_validar_estado(id_estado):
                return False, "El estado seleccionado no existe."
            if not self._sql_validar_contratacion(id_contratacion):
                return False, "La contratación seleccionada no existe."
            if not self._sql_validar_proyecto(datos.get('gestionar_proyectos_codigo_proyecto')):
                return False, "El proyecto seleccionado no existe o está inactivo."

            conn = self._con()
            if not conn:
                return False, "Error de conexión a la base de datos."

            conn.start_transaction()
            cursor = conn.cursor()

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
                str(datos.get('titulo_obra')).strip()[:45],
                str(datos.get('ubicacion_obra')).strip()[:80],
                str(datos.get('periodo_ejecucion')).strip()[:10],
                datos.get('fecha_inicio'),
                datos.get('fecha_fin'),
                str(datos.get('mediciones_obra')).strip()[:45],
                str(datos.get('valuaciones')).strip()[:100],
                str(datos.get('modificaciones_contrato')).strip()[:100],
                certificaciones,
                str(datos.get('numero_contrato')).strip()[:20],
                porcentaje,
                id_estado,
                id_contratacion,
                str(datos.get('gestionar_proyectos_codigo_proyecto')).strip()[:15]
            )

            cursor.execute(sql, valores)
            id_obra = cursor.lastrowid
            conn.commit()
            return True, id_obra
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ObraModel._sql_insertar] Error crítico: {e}")
            return False, f"Error al registrar obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_actualizar(self, id_obra: int, datos: dict) -> tuple:
        conn = cursor = None
        try:
            obra_existente = self._sql_obtener_por_id(id_obra)
            if not obra_existente:
                return False, "La obra no existe o fue eliminada."

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
                id_estado_manual = int(datos.get('estado') or 0)
                id_contratacion = int(datos.get('contratacion_id_contratacion') or 0)
            except (TypeError, ValueError):
                return False, "Campos numéricos inválidos. Verifique certificaciones, avance, estado y contratación."

            if porcentaje < 0 or porcentaje > 100:
                return False, "Porcentaje de avance debe estar entre 0 y 100."
            if certificaciones < 0:
                return False, "Certificaciones ejecutadas debe ser mayor o igual a 0."

            if porcentaje >= 70:
                id_estado = 1
            elif porcentaje >= 30:
                id_estado = 2
            else:
                id_estado = 3

            if not self._validar_fechas(datos.get('fecha_inicio'), datos.get('fecha_fin')):
                return False, "La fecha de fin no puede ser anterior a la fecha de inicio."

            numero_contrato = str(datos.get('numero_contrato')).strip()[:20]
            if self._sql_validar_numero_contrato_duplicado(numero_contrato, excluir_id_obra=id_obra):
                return False, "El número de contrato ya está registrado en otra obra."

            if not self._sql_validar_estado(id_estado):
                return False, "El estado seleccionado no existe."
            if not self._sql_validar_contratacion(id_contratacion):
                return False, "La contratación seleccionada no existe."
            if not self._sql_validar_proyecto(datos.get('gestionar_proyectos_codigo_proyecto')):
                return False, "El proyecto seleccionado no existe o está inactivo."

            self._eliminar_trigger_semaforo()
            conn = self._con()
            if not conn:
                return False, "Error de conexión a la base de datos."

            conn.start_transaction()
            cursor = conn.cursor()

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
                str(datos.get('titulo_obra')).strip()[:45],
                str(datos.get('ubicacion_obra')).strip()[:80],
                str(datos.get('periodo_ejecucion')).strip()[:10],
                datos.get('fecha_inicio'),
                datos.get('fecha_fin'),
                str(datos.get('mediciones_obra')).strip()[:45],
                str(datos.get('valuaciones')).strip()[:100],
                str(datos.get('modificaciones_contrato')).strip()[:100],
                certificaciones,
                numero_contrato,
                porcentaje,
                id_estado,
                id_contratacion,
                str(datos.get('gestionar_proyectos_codigo_proyecto')).strip()[:15],
                id_obra
            )

            cursor.execute(sql, valores)
            conn.commit()
            return True, cursor.rowcount
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ObraModel._sql_actualizar] Error crítico: {e}")
            return False, f"Error al actualizar obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_eliminar(self, id_obra: int) -> tuple:
        conn = cursor = None
        try:
            # El borrado lógico es un UPDATE de estado; eliminamos el trigger
            # BEFORE UPDATE de semáforo para evitar interferencias, igual que en actualizar.
            self._eliminar_trigger_semaforo()
            conn = self._con()
            if not conn:
                return False, "Error de conexión a la base de datos."

            conn.start_transaction()
            cursor = conn.cursor()

            cursor.execute("SELECT id_obra FROM obra WHERE id_obra = %s AND estado = 1", (id_obra,))
            if not cursor.fetchone():
                return False, "La obra no existe o ya fue eliminada."

            cursor.execute("UPDATE obra SET estado = 0 WHERE id_obra = %s AND estado = 1", (id_obra,))
            conn.commit()
            return True, cursor.rowcount
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            print(f"[ObraModel._sql_eliminar] Error: {e}")
            return False, f"Error al eliminar obra: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_listar_estados(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_semaforo, color, descripcion AS nombre FROM semaforo WHERE estado_registro = 1")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel._sql_listar_estados] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_listar_contrataciones(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id_contratacion, numero_contrato, empresa_ganadora FROM contratacion WHERE estado IN (0,1) ORDER BY id_contratacion DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel._sql_listar_contrataciones] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def _sql_listar_proyectos(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn:
                return []
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT codigo_proyecto, descripcion_tecnica, fecha_planificacion FROM proyecto WHERE estado IN (0,1) ORDER BY codigo_proyecto DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"[ObraModel._sql_listar_proyectos] Error: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def obtener_obra_por_id(self, id_obra: int) -> dict:
        return self._sql_obtener_por_id(id_obra)

    def obtener_todas(self) -> list:
        return self._sql_obtener_todas()

    def registrar_obra(self, datos: dict) -> tuple:
        return self._sql_insertar(datos)

    def actualizar_obra(self, id_obra: int, datos: dict) -> tuple:
        return self._sql_actualizar(id_obra, datos)

    def eliminar_obra(self, id_obra: int) -> tuple:
        return self._sql_eliminar(id_obra)

    def validar_estado(self, id_estado) -> bool:
        return self._sql_validar_estado(id_estado)

    def validar_contratacion(self, id_contratacion) -> bool:
        return self._sql_validar_contratacion(id_contratacion)

    def validar_proyecto(self, codigo_proyecto) -> bool:
        return self._sql_validar_proyecto(codigo_proyecto)

    def listar_estados(self) -> list:
        return self._sql_listar_estados()

    def listar_contrataciones(self) -> list:
        return self._sql_listar_contrataciones()

    def listar_proyectos(self) -> list:
        return self._sql_listar_proyectos()
