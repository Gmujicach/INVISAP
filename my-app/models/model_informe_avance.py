"""
InformeAvanceModel — Modelo SOLID/POO para gestión de informes de avance de obra.
Implementa encapsulamiento, validaciones Regex, borrado lógico y comunicación con evidencias.
"""
import re
import uuid
import traceback
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara
from PIL import Image
import os


class InformeAvanceModel:
    """Repositorio de informes de avance con validación y encapsulamiento."""

    # Expresiones regulares para validación
    _RE_PORCENTAJE = re.compile(r'^([0-9]|[1-9][0-9]|100)$')
    _RE_TEXTO_CORTO = re.compile(r'^[\w\s\.,\-áéíóúÁÉÍÓÚñÑ]{3,100}$', re.UNICODE)
    _RE_OBSERVACIONES = re.compile(r'^[\w\s\.,\!\?\-áéíóúÁÉÍÓÚñÑ]{0,500}$', re.UNICODE)
    _RE_POBLACION = re.compile(r'^[\w\s\.,\-\(\)/áéíóúÁÉÍÓÚñÑ]{3,200}$', re.UNICODE)

    # Catálogos válidos (acepta con y sin acentos)
    ESTADOS_VALIDOS = {'Aprobado', 'En Ejecucion', 'En Ejecución', 'Culminado', 'Paralizado'}
    TIPOS_INFORME_VALIDOS = {'Ficha Inspeccion Tecnica', 'Ficha Inspección Técnica', 'Menor', 'Mayor', 'Avance Mensual'}
    MAX_IMAGENES_POR_ETAPA = 5

    def __init__(self):
        self.__id_informe = None
        self.__fecha = None
        self.__estado = None
        self.__poblacion_beneficiada = None
        self.__tipo_informe = None
        self.__observaciones = None
        self.__avance_id = None
        self.__porcentaje_avance = 0
        self.__gerente = None
        self.__evidencias_antes = []
        self.__evidencias_durante = []
        self.__evidencias_despues = []
        self.__estado_registro = 1
        self.__asegurar_tabla_informe()

    # ========== GETTERS Y SETTERS ==========
    
    def get_id_informe(self):
        return self.__id_informe
    
    def set_id_informe(self, valor):
        self.__id_informe = int(valor) if valor else None
    
    def get_fecha(self):
        return self.__fecha
    
    def set_fecha(self, valor):
        if valor is None or valor == '':
            self.__fecha = datetime.now()
        else:
            try:
                if isinstance(valor, str):
                    self.__fecha = datetime.strptime(valor, '%Y-%m-%d %H:%M:%S')
                else:
                    self.__fecha = valor
            except ValueError:
                self.__fecha = datetime.now()
    
    def get_estado(self):
        return self.__estado
    
    def set_estado(self, valor):
        valor = self._limpiar_texto(valor, 25)
        if valor == 'En Ejecución':
            valor = 'En Ejecucion'
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(self.ESTADOS_VALIDOS)}")
        self.__estado = valor
    
    def get_poblacion_beneficiada(self):
        return self.__poblacion_beneficiada
    
    def set_poblacion_beneficiada(self, valor):
        valor = self._limpiar_texto(valor, 45)
        if not valor or len(valor) < 3:
            raise ValueError("Población beneficiada inválida. Debe tener al menos 3 caracteres.")
        self.__poblacion_beneficiada = valor
    
    def get_tipo_informe(self):
        return self.__tipo_informe
    
    def set_tipo_informe(self, valor):
        valor = self._limpiar_texto(valor, 30)
        if valor not in self.TIPOS_INFORME_VALIDOS:
            raise ValueError(f"Tipo de informe inválido. Valores permitidos: {', '.join(self.TIPOS_INFORME_VALIDOS)}")
        self.__tipo_informe = valor
    
    def get_observaciones(self):
        return self.__observaciones
    
    def set_observaciones(self, valor):
        valor = self._limpiar_texto(valor, 500)
        if valor and not self._RE_OBSERVACIONES.match(valor):
            raise ValueError("Observaciones inválidas. Máximo 500 caracteres.")
        self.__observaciones = valor or "Sin observaciones"
    
    def set_evidencias_antes(self, lista_ids):
        if len(lista_ids) > self.MAX_IMAGENES_POR_ETAPA:
            raise ValueError(f"Máximo {self.MAX_IMAGENES_POR_ETAPA} imágenes permitidas en 'antes'")
        self.__evidencias_antes = lista_ids
    
    def set_evidencias_durante(self, lista_ids):
        if len(lista_ids) > self.MAX_IMAGENES_POR_ETAPA:
            raise ValueError(f"Máximo {self.MAX_IMAGENES_POR_ETAPA} imágenes permitidas en 'durante'")
        self.__evidencias_durante = lista_ids
    
    def set_evidencias_despues(self, lista_ids):
        if len(lista_ids) > self.MAX_IMAGENES_POR_ETAPA:
            raise ValueError(f"Máximo {self.MAX_IMAGENES_POR_ETAPA} imágenes permitidas en 'después'")
        self.__evidencias_despues = lista_ids
    
    def set_avance_id(self, valor):
        if valor is None:
            self.__avance_id = None
        else:
            self.__avance_id = str(valor)
    
    def set_porcentaje_avance(self, valor):
        try:
            porcentaje = int(valor or 0)
        except (TypeError, ValueError):
            porcentaje = 0
        self.__porcentaje_avance = max(0, min(100, porcentaje))
    
    def get_porcentaje_avance(self):
        return self.__porcentaje_avance
    
    def get_avance_id(self):
        return self.__avance_id
    
    def set_gerente(self, valor):
        if valor is not None and valor != '':
            self.__gerente = str(valor)
    
    def get_gerente(self):
        return self.__gerente

    @staticmethod
    def _limpiar_texto(texto, max_len=255):
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    def __asegurar_columna_poblacion(self, cur):
        """Asegura que exista la columna correcta 'poblacion_beneficiada' y elimina el typo 'poblacion_benefiada'."""
        cur.execute("SHOW COLUMNS FROM informe_avance_obra LIKE 'poblacion_beneficiada'")
        tiene_correcta = cur.fetchone()
        cur.execute("SHOW COLUMNS FROM informe_avance_obra LIKE 'poblacion_benefiada'")
        tiene_typo = cur.fetchone()

        if tiene_correcta and tiene_typo:
            cur.execute("UPDATE informe_avance_obra SET poblacion_beneficiada = `poblacion_benefiada` WHERE (poblacion_beneficiada IS NULL OR poblacion_beneficiada = '') AND `poblacion_benefiada` IS NOT NULL AND `poblacion_benefiada` <> ''")
            cur.execute("ALTER TABLE informe_avance_obra DROP COLUMN poblacion_benefiada")
            print("[DB] Datos migrados y columna typo 'poblacion_benefiada' eliminada (se conserva 'poblacion_beneficiada')")
        elif not tiene_correcta and tiene_typo:
            cur.execute("ALTER TABLE informe_avance_obra CHANGE COLUMN poblacion_benefiada poblacion_beneficiada VARCHAR(45) NOT NULL DEFAULT 'No especificado'")
            print("[DB] Columna 'poblacion_benefiada' renombrada a 'poblacion_beneficiada'")
        elif not tiene_correcta and not tiene_typo:
            cur.execute("ALTER TABLE informe_avance_obra ADD COLUMN poblacion_beneficiada VARCHAR(45) NOT NULL DEFAULT 'No especificado'")
            print("[DB] Columna 'poblacion_beneficiada' agregada a tabla informe_avance_obra")
        else:
            cur.execute("ALTER TABLE informe_avance_obra MODIFY COLUMN poblacion_beneficiada VARCHAR(45) NOT NULL DEFAULT 'No especificado'")
            print("[DB] Columna 'poblacion_beneficiada' ajustada con DEFAULT")

    def __asegurar_tabla_informe(self):
        """Corrige el typo de columna y asegura DEFAULT sin intervención manual."""
        try:
            conn = connectionBD_invilara()
            if conn:
                cur = conn.cursor()
                try:
                    self.__asegurar_columna_poblacion(cur)
                    conn.commit()

                    cur.execute("SHOW COLUMNS FROM informe_avance_obra LIKE 'estado_registro'")
                    if not cur.fetchone():
                        cur.execute("ALTER TABLE informe_avance_obra ADD COLUMN estado_registro TINYINT NOT NULL DEFAULT 1 COMMENT '1=Activo, 0=Inactivo (borrado logico)'")
                        conn.commit()
                        print("[DB] Columna 'estado_registro' agregada a tabla informe_avance_obra")
                except Exception as e:
                    print(f"[DB] Error al verificar columnas informe_avance_obra: {e}")
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla informe_avance_obra: {e}")

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========
    
    def __crear_avance_db(self, gerente_id, porcentaje, observaciones):
        conn = None
        cur = None
        id_avance = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            cur = conn.cursor()

            descripcion = self._limpiar_texto(observaciones or 'Sin descripción', 45) or 'Sin descripcion'
            porcentaje = max(0, min(100, int(porcentaje or 0)))
            id_avance = str(uuid.uuid4().hex[:12])

            # Usar SIEMPRE la clave compuesta real de una obra existente para
            # no violar la FK fk_avance_obra1 (avance -> obra). Seleccionamos
            # las 4 columnas del PK directamente desde una fila real de 'obra'.
            cur.execute(
                "SELECT id_obra, semaforo_id_semaforo, contratacion_id_contratacion, "
                "gestionar_proyectos_codigo_proyecto FROM obra ORDER BY id_obra DESC LIMIT 1"
            )
            row_obra = cur.fetchone()
            if row_obra:
                id_obra, id_semaforo, id_contratacion, codigo_proyecto = row_obra
            else:
                cur.execute("SELECT id_semaforo FROM semaforo ORDER BY id_semaforo DESC LIMIT 1")
                row_semaforo = cur.fetchone()
                id_semaforo = row_semaforo[0] if row_semaforo else 1
                id_obra = 1
                id_contratacion = 1
                codigo_proyecto = 'FRE-001'

            sql = """INSERT INTO avance (id_avance, descripcion, porcentaje_avance, gerente, fecha_avance, obra_id_obra, obra_semaforo_id_semaforo, obra_contratacion_id_contratacion, obra_gestionar_proyectos_codigo_proyecto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            params = (id_avance, descripcion, porcentaje, str(gerente_id) if gerente_id else '1', datetime.now().date(), id_obra, id_semaforo, id_contratacion, codigo_proyecto)
            cur.execute(sql, params)
            conn.commit()
            return str(id_avance)
        except Exception as e:
            print(f"Error __crear_avance_db: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def __registrar_informe_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            cur = conn.cursor()

            try:
                self.__asegurar_columna_poblacion(cur)
                conn.commit()
            except Exception as e:
                print(f"[DB] Error al asegurar columna poblacion_beneficiada: {e}")

            sql = """INSERT INTO informe_avance_obra (fecha, estado, poblacion_beneficiada, tipo_informe, evidencia_antes, evidencia_durante, evidencia_despues, avance_id_avance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            ev_antes = ','.join(map(str, self.__evidencias_antes)) if self.__evidencias_antes else ''
            ev_durante = ','.join(map(str, self.__evidencias_durante)) if self.__evidencias_durante else ''
            ev_despues = ','.join(map(str, self.__evidencias_despues)) if self.__evidencias_despues else ''

            poblacion = self.__poblacion_beneficiada or 'No especificado'
            cur.execute(sql, (self.__fecha or datetime.now(), self.__estado, poblacion, self.__tipo_informe, ev_antes, ev_durante, ev_despues, self.__avance_id))
            nuevo_id = cur.lastrowid

            if self.__avance_id:
                gerente_a_usar = self.__gerente or '1'
                obs = self._limpiar_texto(self.__observaciones or '', 45) or 'Sin observaciones'
                cur.execute("UPDATE avance SET descripcion = %s, porcentaje_avance = %s WHERE id_avance = %s",
                    (obs, self.__porcentaje_avance, self.__avance_id))

            conn.commit()
            return nuevo_id
        except Exception as e:
            print(f"Error __registrar_informe_db: {e}")
            if conn:
                conn.rollback()
            raise ValueError(f"Error en base de datos al registrar informe: {str(e)}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __actualizar_informe_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            cur = conn.cursor()

            sql = """UPDATE informe_avance_obra SET estado = %s, poblacion_beneficiada = %s, tipo_informe = %s, evidencia_antes = %s, evidencia_durante = %s, evidencia_despues = %s WHERE id_informe = %s"""
            
            ev_antes = ','.join(map(str, self.__evidencias_antes)) if self.__evidencias_antes else ''
            ev_durante = ','.join(map(str, self.__evidencias_durante)) if self.__evidencias_durante else ''
            ev_despues = ','.join(map(str, self.__evidencias_despues)) if self.__evidencias_despues else ''

            cur.execute(sql, (self.__estado, self.__poblacion_beneficiada or 'No especificado', self.__tipo_informe, ev_antes, ev_durante, ev_despues, self.__id_informe))

            cur.execute("SELECT avance_id_avance FROM informe_avance_obra WHERE id_informe = %s", (self.__id_informe,))
            avance_row = cur.fetchone()
            if avance_row and avance_row[0]:
                obs = self._limpiar_texto(self.__observaciones or '', 45) or 'Sin observaciones'
                cur.execute("UPDATE avance SET descripcion = %s, porcentaje_avance = %s WHERE id_avance = %s",
                    (obs, self.__porcentaje_avance, avance_row[0]))

            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            print(f"Error __actualizar_informe_db: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __eliminar_logico_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            cur = conn.cursor()

            try:
                cur.execute("UPDATE informe_avance_obra SET estado_registro = 0 WHERE id_informe = %s AND estado_registro = 1", (self.__id_informe,))
                if cur.rowcount > 0:
                    conn.commit()
                    return True
            except Exception:
                pass

            cur.execute("DELETE FROM informe_avance_obra WHERE id_informe = %s", (self.__id_informe,))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error __eliminar_logico_db: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __obtener_todos_informes_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            cur = conn.cursor(dictionary=True)
            sql = """SELECT i.*, a.porcentaje_avance, a.fecha_avance, a.gerente as gerente_id, e.nombre_empleado as gerente_nombre FROM informe_avance_obra i LEFT JOIN avance a ON i.avance_id_avance = a.id_avance LEFT JOIN empleados e ON a.gerente = e.id_empleados WHERE i.estado_registro = 1 ORDER BY i.fecha DESC"""
            cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            print(f"Error __obtener_todos_informes_db: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __obtener_informe_por_id_db(self, id_informe):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            cur = conn.cursor(dictionary=True)
            sql = """SELECT i.id_informe, i.fecha, i.estado, i.poblacion_beneficiada, i.tipo_informe, i.evidencia_antes, i.evidencia_durante, i.evidencia_despues, i.avance_id_avance, a.porcentaje_avance, a.descripcion as observaciones, a.gerente, e.nombre_empleado as gerente_nombre FROM informe_avance_obra i LEFT JOIN avance a ON i.avance_id_avance = a.id_avance LEFT JOIN empleados e ON a.gerente = e.id_empleados WHERE i.id_informe = %s"""
            cur.execute(sql, (id_informe,))
            informe = cur.fetchone()
            if informe:
                informe['evidencias'] = self.__obtener_evidencias_por_informe(cur, id_informe)
            return informe
        except Exception as e:
            print(f"Error __obtener_informe_por_id_db: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __obtener_evidencias_por_informe(self, cursor, id_informe):
        try:
            cursor.execute("SELECT * FROM vista_evidencia_informe WHERE id_informe = %s AND estado = 1 ORDER BY etapa, fecha_registro", (id_informe,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error __obtener_evidencias_por_informe: {e}")
            return []

    def __obtener_gerentes_activos_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id_empleados, nombre_empleado, cargo FROM empleados WHERE cargo IN ('Gerente', 'Inspector') AND estado = 1 ORDER BY nombre_empleado")
            return cur.fetchall()
        except Exception as e:
            print(f"Error __obtener_gerentes_activos_db: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __validar_informe_activo_db(self, id_informe):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            cur = conn.cursor()
            try:
                cur.execute("SELECT id_informe FROM informe_avance_obra WHERE id_informe = %s AND estado_registro = 1", (id_informe,))
            except Exception:
                cur.execute("SELECT id_informe FROM informe_avance_obra WHERE id_informe = %s", (id_informe,))
            return cur.fetchone() is not None
        except Exception:
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # ========== MÉTODOS PÚBLICOS ==========
    
    def registrar_informe(self, data):
        try:
            if not isinstance(data, dict):
                raise ValueError('Datos del informe inválidos.')

            payload = {k: (v if v is not None else '') for k, v in data.items()}

            self.set_estado(payload.get('estado'))
            self.set_poblacion_beneficiada(payload.get('poblacion_beneficiada'))
            self.set_tipo_informe(payload.get('tipo_informe'))
            self.set_observaciones(payload.get('observaciones', ''))
            self.set_fecha(payload.get('fecha'))
            self.set_porcentaje_avance(payload.get('porcentaje_avance', 0))
            self.set_gerente(payload.get('gerente_responsable_id'))

            avance_id = payload.get('avance_id_avance')
            gerente_id = payload.get('gerente_responsable_id')
            if not avance_id:
                avance_id = self.__crear_avance_db(gerente_id, payload.get('porcentaje_avance', 0), payload.get('observaciones', '') or 'Sin descripcion')
            
            if not avance_id:
                conn_fallback = connectionBD_invilara()
                if conn_fallback:
                    try:
                        cur_fallback = conn_fallback.cursor()
                        cur_fallback.execute("SELECT id_avance FROM avance LIMIT 1")
                        row = cur_fallback.fetchone()
                        if row and row[0]:
                            avance_id = row[0]
                    except Exception:
                        pass
                    finally:
                        try:
                            if cur_fallback:
                                cur_fallback.close()
                        except Exception:
                            pass
                        try:
                            if conn_fallback:
                                conn_fallback.close()
                        except Exception:
                            pass

            if not avance_id:
                raise ValueError("No se pudo crear ni vincular un avance de obra. Verifique que exista al menos una obra registrada.")

            self.set_avance_id(avance_id)
            self.__avance_id = avance_id

            if payload.get('evidencias_antes'):
                self.set_evidencias_antes([item for item in str(payload.get('evidencias_antes', '')).split(',') if item])
            if payload.get('evidencias_durante'):
                self.set_evidencias_durante([item for item in str(payload.get('evidencias_durante', '')).split(',') if item])
            if payload.get('evidencias_despues'):
                self.set_evidencias_despues([item for item in str(payload.get('evidencias_despues', '')).split(',') if item])

            return self.__registrar_informe_db()
        except ValueError as ve:
            print(f"Error de validación en registrar_informe: {ve}")
            raise ve
        except Exception as e:
            traceback.print_exc()
            print(f"Error inesperado al registrar informe: {e}")
            raise ValueError(f"Error interno al registrar: {str(e)}")

    def actualizar_informe(self, data):
        try:
            id_informe = int(data.get('id_informe'))
            if not self.__validar_informe_activo_db(id_informe):
                raise ValueError("El informe no existe o fue eliminado.")

            self.set_id_informe(id_informe)
            self.set_estado(data.get('estado'))
            self.set_poblacion_beneficiada(data.get('poblacion_beneficiada'))
            self.set_tipo_informe(data.get('tipo_informe'))
            self.set_observaciones(data.get('observaciones', ''))
            self.set_avance_id(data.get('avance_id_avance'))
            self.set_porcentaje_avance(data.get('porcentaje_avance', 0))
            self.set_gerente(data.get('gerente_responsable_id'))

            if data.get('evidencias_antes'):
                self.set_evidencias_antes([item for item in str(data.get('evidencias_antes', '')).split(',') if item])
            else:
                self.__evidencias_antes = []
            if data.get('evidencias_durante'):
                self.set_evidencias_durante([item for item in str(data.get('evidencias_durante', '')).split(',') if item])
            else:
                self.__evidencias_durante = []
            if data.get('evidencias_despues'):
                self.set_evidencias_despues([item for item in str(data.get('evidencias_despues', '')).split(',') if item])
            else:
                self.__evidencias_despues = []

            return self.__actualizar_informe_db()
        except ValueError as ve:
            print(f"Error de validación en actualizar_informe: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al actualizar informe: {e}")
            return False

    def eliminar_informe_logico(self, id_informe):
        try:
            id_val = int(id_informe)
            if not self.__validar_informe_activo_db(id_val):
                raise ValueError("El informe no existe o ya fue eliminado.")
            self.set_id_informe(id_val)
            return self.__eliminar_logico_db()
        except ValueError as ve:
            print(f"Error de validación en eliminar_informe_logico: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al eliminar informe: {e}")
            return False

    def obtener_todos_informes(self):
        return self.__obtener_todos_informes_db()

    def obtener_informe_por_id(self, id_informe):
        try:
            id_val = int(id_informe)
            return self.__obtener_informe_por_id_db(id_val)
        except (ValueError, TypeError):
            return None

    def obtener_gerentes_activos(self):
        return self.__obtener_gerentes_activos_db()

    def validar_informe_activo(self, id_informe):
        try:
            id_val = int(id_informe)
            return self.__validar_informe_activo_db(id_val)
        except (ValueError, TypeError):
            return False

    @staticmethod
    def comprimir_imagen(ruta_original, calidad=85):
        try:
            with Image.open(ruta_original) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                max_width = 1920
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_size = (max_width, int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                img.save(ruta_original, 'JPEG', quality=calidad, optimize=True)
                return True
        except Exception as e:
            print(f"Error al comprimir imagen: {e}")
            return False