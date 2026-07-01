"""
InformeAvanceModel — Modelo SOLID/POO para gestión de informes de avance de obra.
Implementa encapsulamiento, validaciones Regex, borrado lógico y comunicación con evidencias.
"""
import re
import uuid
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara
from PIL import Image
import os


class InformeAvanceModel:
    """Repositorio de informes de avance con validación y encapsulamiento."""

    # Expresiones regulares para validación (Principio de Responsabilidad Única)
    _RE_PORCENTAJE = re.compile(r'^([0-9]|[1-9][0-9]|100)$')  # 0-100
    _RE_TEXTO_CORTO = re.compile(r'^[\w\s\.,\-áéíóúÁÉÍÓÚñÑ]{3,100}$', re.UNICODE)
    _RE_OBSERVACIONES = re.compile(r'^[\w\s\.,\!\?\-áéíóúÁÉÍÓÚñÑ]{0,500}$', re.UNICODE)
    _RE_POBLACION = re.compile(r'^[\w\s\.,\-\(\)/áéíóúÁÉÍÓÚñÑ]{3,200}$', re.UNICODE)
    
    # Catálogos válidos (TODO: migrar a tablas catálogo según Prof. Cadenas)
    ESTADOS_VALIDOS = {'Aprobado', 'En Ejecucion', 'Culminado', 'Paralizado'}
    TIPOS_INFORME_VALIDOS = {'Ficha Inspeccion Tecnica', 'Menor', 'Mayor', 'Avance Mensual'}
    
    MAX_IMAGENES_POR_ETAPA = 5  # Límite según Prof. Cadenas

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_informe = None
        self.__fecha = None
        self.__estado = None
        self.__poblacion_beneficiada = None
        self.__tipo_informe = None
        self.__observaciones = None
        self.__avance_id = None
        self.__evidencias_antes = []  # Lista de IDs
        self.__evidencias_durante = []
        self.__evidencias_despues = []
        self.__estado_registro = 1  # 1=Activo, 0=Inactivo (Borrado Lógico)

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========
    
    def get_id_informe(self):
        return self.__id_informe
    
    def set_id_informe(self, valor):
        self.__id_informe = int(valor) if valor else None
    
    def get_fecha(self):
        return self.__fecha
    
    def set_fecha(self, valor):
        """Fecha automática si no se proporciona"""
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
        """Validación de estado"""
        valor = self._limpiar_texto(valor, 25)
        if valor not in self.ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Valores permitidos: {', '.join(self.ESTADOS_VALIDOS)}")
        self.__estado = valor
    
    def get_poblacion_beneficiada(self):
        return self.__poblacion_beneficiada
    
    def set_poblacion_beneficiada(self, valor):
        """Validación con Regex"""
        valor = self._limpiar_texto(valor, 45)
        if not valor or len(valor) < 3:
            raise ValueError("Población beneficiada inválida. Debe tener al menos 3 caracteres.")
        self.__poblacion_beneficiada = valor
    
    def get_tipo_informe(self):
        return self.__tipo_informe
    
    def set_tipo_informe(self, valor):
        """Validación de tipo"""
        valor = self._limpiar_texto(valor, 30)
        if valor not in self.TIPOS_INFORME_VALIDOS:
            raise ValueError(f"Tipo de informe inválido. Valores permitidos: {', '.join(self.TIPOS_INFORME_VALIDOS)}")
        self.__tipo_informe = valor
    
    def get_observaciones(self):
        return self.__observaciones
    
    def set_observaciones(self, valor):
        """Campo de observaciones técnicas"""
        valor = self._limpiar_texto(valor, 500)
        if valor and not self._RE_OBSERVACIONES.match(valor):
            raise ValueError("Observaciones inválidas. Máximo 500 caracteres.")
        self.__observaciones = valor or "Sin observaciones"
    
    def set_evidencias_antes(self, lista_ids):
        """Limitar a MAX_IMAGENES_POR_ETAPA"""
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
    
    def get_avance_id(self):
        return self.__avance_id
    
    @staticmethod
    def _limpiar_texto(texto, max_len=255):
        """Limpieza de datos contra inyección SQL"""
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    def __crear_avance_db(self, gerente_id, porcentaje, observaciones):
        """Crea un registro en tabla avance resolviendo dependencias automáticamente"""
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                raise ValueError("No se pudo conectar a BD para crear avance")
            cur = conn.cursor()

            id_avance = str(uuid.uuid4().hex[:12])

            descripcion = (observaciones or 'Sin descripción')[:45]

            try:
                porcentaje = int(porcentaje) if porcentaje else 0
            except (ValueError, TypeError):
                porcentaje = 0
            porcentaje = max(0, min(100, porcentaje))

            cur.execute("SELECT MAX(id_semaforo) FROM semaforo")
            max_sem = cur.fetchone()[0]
            id_semaforo = (max_sem or 0) + 1
            cur.execute(
                "INSERT IGNORE INTO semaforo (id_semaforo, estado, color, descripcion) VALUES (%s, %s, %s, %s)",
                (id_semaforo, 'Activo', 'VERDE', 'Semáforo generado automáticamente')
            )

            cur.execute(
                "SELECT id_obra FROM obra WHERE semaforo_id_semaforo=%s AND contratacion_id_contratacion=%s AND gestionar_proyectos_codigo_proyecto=%s",
                (id_semaforo, 1, 'FRE-001')
            )
            row = cur.fetchone()
            if row:
                id_obra = row[0]
            else:
                cur.execute("SELECT MAX(id_obra) FROM obra")
                max_obra = cur.fetchone()[0]
                id_obra = (max_obra or 0) + 1
                cur.execute(
                    """INSERT INTO obra (id_obra, titulo_obra, ubicacion_obra, periodo_ejecucion, fecha_inicio, fecha_fin,
                                       mediciones_obra, valuaciones, modificaciones_contrato,
                                       certificaciones_obras_ejecutadas, numero_contrato,
                                       porcentaje_avance_obra, semaforo_id_semaforo,
                                       contratacion_id_contratacion, gestionar_proyectos_codigo_proyecto)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (id_obra, 'Obra Generada', 'Sin ubicacion', 1, datetime.now().date(), datetime.now().date(),
                     'N/A', 'N/A', 'N/A', 0, 'N/A', porcentaje, id_semaforo, 1, 'FRE-001')
                )

            sql = """
                INSERT INTO avance (id_avance, descripcion, porcentaje_avance, gerente, fecha_avance,
                                    obra_id_obra, obra_semaforo_id_semaforo,
                                    obra_contratacion_id_contratacion, obra_gestionar_proyectos_codigo_proyecto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                id_avance,
                descripcion,
                porcentaje,
                str(gerente_id),
                datetime.now().date(),
                id_obra,
                id_semaforo,
                1,
                'FRE-001'
            )
            cur.execute(sql, params)
            conn.commit()
            return str(id_avance)
        except Exception as e:
            if conn:
                conn.rollback()
            raise ValueError(f"Error al crear avance: {str(e)}")
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========
    
    def __registrar_informe_db(self):
        """Método PRIVADO para insertar informe en BD"""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Consulta parametrizada (seguridad contra inyección)
            sql = """
                INSERT INTO informe_avance_obra 
                (fecha, estado, poblacion_beneficiada, tipo_informe, 
                 evidencia_antes, evidencia_durante, evidencia_despues, avance_id_avance)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convertir listas de evidencias a string separado por comas
            ev_antes = ','.join(map(str, self.__evidencias_antes)) if self.__evidencias_antes else ''
            ev_durante = ','.join(map(str, self.__evidencias_durante)) if self.__evidencias_durante else ''
            ev_despues = ','.join(map(str, self.__evidencias_despues)) if self.__evidencias_despues else ''
            
            cur.execute(sql, (
                self.__fecha or datetime.now(),
                self.__estado,
                self.__poblacion_beneficiada,
                self.__tipo_informe,
                ev_antes,
                ev_durante,
                ev_despues,
                self.__avance_id
            ))
            
            conn.commit()
            return cur.lastrowid
            
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
        """Método PRIVADO para actualizar informe"""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            sql = """
                UPDATE informe_avance_obra 
                SET estado = %s, poblacion_beneficiada = %s, tipo_informe = %s,
                    evidencia_antes = %s, evidencia_durante = %s, evidencia_despues = %s
                WHERE id_informe = %s
            """
            
            ev_antes = ','.join(map(str, self.__evidencias_antes)) if self.__evidencias_antes else ''
            ev_durante = ','.join(map(str, self.__evidencias_durante)) if self.__evidencias_durante else ''
            ev_despues = ','.join(map(str, self.__evidencias_despues)) if self.__evidencias_despues else ''
            
            cur.execute(sql, (
                self.__estado,
                self.__poblacion_beneficiada,
                self.__tipo_informe,
                ev_antes,
                ev_durante,
                ev_despues,
                self.__id_informe
            ))
            
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
        """
        BORRADO LÓGICO (Prof. Escalona - OBLIGATORIO)
        TODO: Agregar campo 'estado_registro' a la tabla
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Por ahora borrado físico (cambiar cuando se agregue campo estado_registro)
            sql = "DELETE FROM informe_avance_obra WHERE id_informe = %s"
            # TODO: UPDATE informe_avance_obra SET estado_registro = 0 WHERE id_informe = %s
            
            cur.execute(sql, (self.__id_informe,))
            conn.commit()
            return cur.rowcount > 0
            
        except Exception as e:
            print(f"Error __eliminar_logico_db: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __obtener_todos_informes_db(self):
        """Método PRIVADO que obtiene todos los informes"""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            
            cur = conn.cursor(dictionary=True)
            
            sql = """
                SELECT i.*, a.porcentaje_avance, a.gerente, a.fecha_avance,
                       e.nombre_empleado as gerente_nombre
                FROM informe_avance_obra i
                LEFT JOIN avance a ON i.avance_id_avance = a.id_avance
                LEFT JOIN empleados e ON a.gerente = e.id_empleados
                ORDER BY i.fecha DESC
            """
            
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
        """Método PRIVADO que obtiene un informe específico"""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            
            cur = conn.cursor(dictionary=True)
            
            sql = """
                SELECT i.*, a.porcentaje_avance, a.gerente, a.descripcion as avance_descripcion
                FROM informe_avance_obra i
                LEFT JOIN avance a ON i.avance_id_avance = a.id_avance
                WHERE i.id_informe = %s
            """
            
            cur.execute(sql, (id_informe,))
            informe = cur.fetchone()
            
            if informe:
                # Obtener evidencias usando la VISTA (Prof. Cadenas)
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
        """Usa la VISTA vista_evidencia_informe (Prof. Cadenas)"""
        try:
            sql = """
                SELECT * FROM vista_evidencia_informe 
                WHERE id_informe = %s AND estado = 1
                ORDER BY etapa, fecha_registro
            """
            cursor.execute(sql, (id_informe,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error __obtener_evidencias_por_informe: {e}")
            return []
    
    def __obtener_gerentes_activos_db(self):
        """
        Obtiene empleados con cargo 'Gerente' o 'Inspector' (Prof. Jhoanly)
        Filtrado por rol según especificación
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            
            cur = conn.cursor(dictionary=True)
            
            sql = """
                SELECT id_empleados, nombre_empleado, cargo 
                FROM empleados 
                WHERE cargo IN ('Gerente', 'Inspector') AND estado = 1
                ORDER BY nombre_empleado
            """
            
            cur.execute(sql)
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
        """Validación en tiempo real (Prof. Escalona)"""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            sql = "SELECT id_informe FROM informe_avance_obra WHERE id_informe = %s"
            cur.execute(sql, (id_informe,))
            
            return cur.fetchone() is not None
            
        except Exception:
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # ========== MÉTODOS PÚBLICOS (Interfaz Pública - Capa de Seguridad) ==========
    
    def registrar_informe(self, data):
        """Método PÚBLICO que actúa como interfaz para registrar informes"""
        try:
            self.set_estado(data.get('estado'))
            self.set_poblacion_beneficiada(data.get('poblacion_beneficiada'))
            self.set_tipo_informe(data.get('tipo_informe'))
            self.set_observaciones(data.get('observaciones', ''))
            self.set_fecha(data.get('fecha'))
            
            avance_id = data.get('avance_id_avance')
            gerente_id = data.get('gerente_responsable_id')
            if not avance_id:
                avance_id = self.__crear_avance_db(
                    gerente_id or 1,
                    data.get('porcentaje_avance', 0),
                    data.get('observaciones', '') or 'Sin descripción'
                )
            self.set_avance_id(avance_id)
            
            self.__avance_id = avance_id
            
            if data.get('evidencias_antes'):
                self.set_evidencias_antes(data.get('evidencias_antes').split(','))
            if data.get('evidencias_durante'):
                self.set_evidencias_durante(data.get('evidencias_durante').split(','))
            if data.get('evidencias_despues'):
                self.set_evidencias_despues(data.get('evidencias_despues').split(','))
            
            return self.__registrar_informe_db()
            
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al registrar informe: {e}")
            raise ValueError(f"Error interno al registrar: {str(e)}")
    
    def actualizar_informe(self, data):
        """Método PÚBLICO para actualizar informe"""
        try:
            id_informe = int(data.get('id_informe'))
            
            if not self.__validar_informe_activo_db(id_informe):
                raise ValueError("El informe no existe o fue eliminado.")
            
            self.set_id_informe(id_informe)
            self.set_estado(data.get('estado'))
            self.set_poblacion_beneficiada(data.get('poblacion_beneficiada'))
            self.set_tipo_informe(data.get('tipo_informe'))
            self.set_observaciones(data.get('observaciones', ''))
            
            return self.__actualizar_informe_db()
            
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al actualizar informe: {e}")
            return False
    
    def eliminar_informe_logico(self, id_informe):
        """Método PÚBLICO para borrado lógico"""
        try:
            id_val = int(id_informe)
            
            if not self.__validar_informe_activo_db(id_val):
                raise ValueError("El informe no existe o ya fue eliminado.")
            
            self.set_id_informe(id_val)
            return self.__eliminar_logico_db()
            
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al eliminar informe: {e}")
            return False
    
    def obtener_todos_informes(self):
        """Método PÚBLICO para obtener todos los informes"""
        return self.__obtener_todos_informes_db()
    
    def obtener_informe_por_id(self, id_informe):
        """Método PÚBLICO para obtener un informe específico"""
        try:
            id_val = int(id_informe)
            return self.__obtener_informe_por_id_db(id_val)
        except (ValueError, TypeError):
            return None
    
    def obtener_gerentes_activos(self):
        """Método PÚBLICO para obtener gerentes/inspectores"""
        return self.__obtener_gerentes_activos_db()
    
    def validar_informe_activo(self, id_informe):
        """Método PÚBLICO para validación en tiempo real"""
        try:
            id_val = int(id_informe)
            return self.__validar_informe_activo_db(id_val)
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def comprimir_imagen(ruta_original, calidad=85):
        """
        Compresión de imágenes (Prof. Cadenas)
        Usa Pillow para reducir tamaño sin perder calidad
        """
        try:
            with Image.open(ruta_original) as img:
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar si es muy grande
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