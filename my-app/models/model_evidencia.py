"""
EvidenciaModel — Modelo SOLID/POO para gestión de evidencias fotográficas.
Implementa encapsulamiento, validaciones Regex, borrado lógico y compresión de imágenes.
"""
import os
import re
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from conexion.conexionBD import connectionBD_invilara


class EvidenciaModel:
    """Repositorio de evidencias fotográficas con compresión y validación."""

    # Expresiones regulares para validación (Principio de Responsabilidad Única)
    _RE_NOMBRE_ARCHIVO = re.compile(r'^[\w\-. áéíóúÁÉÍÓÚñÑ()]{1,100}\.(jpg|jpeg|png|gif|webp)$', re.IGNORECASE)
    _RE_URL = re.compile(r'^[\w\-/. ]{10,200}$')
    _ETAPAS_VALIDAS = {'antes', 'durante', 'despues'}
    
    # Configuración de compresión
    MAX_IMAGENES = 5
    MIN_IMAGENES = 3
    CALIDAD_COMPRESION = 80  # Calidad del 80% según instrucciones del profesor
    MAX_DIMENSION = 1920  # Redimensionar si es mayor a 1920px

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_evidencia = None
        self.__fotos = []
        self.__url_archivos = []
        self.__fecha_registro = None
        self.__estado = 1  # 1 = Activo, 0 = Inactivo (Borrado Lógico)
        self.__etapas = {}  # Diccionario {index: etapa}
        
        # Directorio de carga
        self.__upload_folder = os.path.join(
            os.path.dirname(__file__), '..', 'static', 'uploads', 'evidencias'
        )
        if not os.path.exists(self.__upload_folder):
            os.makedirs(self.__upload_folder)

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========
    
    def get_id_evidencia(self):
        return self.__id_evidencia
    
    def set_id_evidencia(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de evidencia debe ser un entero positivo.")
        self.__id_evidencia = valor
    
    def get_fotos(self):
        return self.__fotos
    
    def set_fotos(self, files):
        """Valida y establece los archivos de fotos."""
        if not isinstance(files, list):
            files = list(files)
        
        if not (self.MIN_IMAGENES <= len(files) <= self.MAX_IMAGENES):
            raise ValueError(
                f"Debe seleccionar entre {self.MIN_IMAGENES} y {self.MAX_IMAGENES} imágenes."
            )
        
        # Validar cada archivo
        for file in files:
            if not self._validar_nombre_archivo(file.filename):
                raise ValueError(
                    f"Archivo '{file.filename}' no tiene un formato válido. "
                    "Solo se permiten JPG, PNG, GIF, WEBP."
                )
        
        self.__fotos = files
    
    def get_etapas(self):
        return self.__etapas
    
    def set_etapas(self, form_data):
        """Extrae y valida las etapas desde el formulario."""
        etapas_dict = {}
        for i in range(len(self.__fotos)):
            etapa = form_data.get(f"etapa-foto-{i}", "antes").strip().lower()
            if etapa not in self._ETAPAS_VALIDAS:
                raise ValueError(
                    f"Etapa '{etapa}' no válida. Use: antes, durante o despues."
                )
            etapas_dict[i] = etapa
        self.__etapas = etapas_dict
    
    def get_estado(self):
        return self.__estado
    
    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 (inactivo) o 1 (activo).")
        self.__estado = valor

    # ========== VALIDACIONES (Método Aparte - Responsabilidad Única) ==========
    
    def _validar_nombre_archivo(self, nombre: str) -> bool:
        """Valida el nombre del archivo con Regex."""
        return bool(self._RE_NOMBRE_ARCHIVO.match(nombre))
    
    def _validar_url(self, url: str) -> bool:
        """Valida la URL del archivo con Regex."""
        return bool(self._RE_URL.match(url))
    
    @staticmethod
    def _limpiar_texto(texto: str, max_len: int = 100) -> str:
        """Limpia y sanitiza texto para evitar inyecciones."""
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    # ========== MÉTODOS PRIVADOS DE LÓGICA DE NEGOCIO ==========
    
    def __comprimir_y_guardar_imagen(self, file):
        """
        Comprime y guarda una imagen, retornando su URL relativa.
        Implementa compresión según instrucciones del profesor Cadenas.
        """
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"
        path = os.path.join(self.__upload_folder, unique_name)
        
        try:
            # Abrir imagen con Pillow
            img = Image.open(file.stream)
            
            # Convertir a RGB si es necesario (para PNG con transparencia)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Redimensionar si es muy grande (optimización)
            if max(img.size) > self.MAX_DIMENSION:
                img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.Resampling.LANCZOS)
            
            # Guardar con compresión del 80%
            img.save(path, format='JPEG', optimize=True, quality=self.CALIDAD_COMPRESION)
            
            # Retornar URL relativa para la BD
            return f"uploads/evidencias/{unique_name}"
            
        except Exception as e:
            print(f"Error al comprimir imagen {filename}: {e}")
            raise ValueError(f"No se pudo procesar la imagen {filename}")
    
    def __guardar_evidencias_db(self):
        """
        Método PRIVADO que guarda las evidencias en la base de datos.
        Usa consultas parametrizadas (marcadores) para evitar inyecciones.
        """
        conn = None
        cur = None
        ids_insertados = []
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # SQL parametrizado con marcadores de posición
            sql = """
                INSERT INTO evidencia 
                (fotos, url_archivos, fecha_registro, estado, etapa) 
                VALUES (%s, %s, %s, %s, %s)
            """
            
            # Insertar cada foto con su etapa correspondiente
            for i, file in enumerate(self.__fotos):
                # Comprimir y guardar imagen
                url = self.__comprimir_y_guardar_imagen(file)
                
                # Validar URL generada
                if not self._validar_url(url):
                    raise ValueError(f"URL generada no válida: {url}")
                
                etapa = self.__etapas.get(i, "antes")
                nombre_referencia = self._limpiar_texto(file.filename, 45)
                
                # Ejecutar con parámetros (evita inyección SQL)
                cur.execute(sql, (
                    nombre_referencia,
                    url,
                    datetime.now(),
                    1,  # Estado activo
                    etapa
                ))
                
                ids_insertados.append(cur.lastrowid)
            
            conn.commit()
            return ids_insertados  # Retorna lista de IDs insertados
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error al guardar evidencias en BD: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __actualizar_evidencias_db(self, id_evidencia: int):
        """
        Método PRIVADO que actualiza las evidencias existentes.
        Reemplaza las imágenes antiguas por las nuevas.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor(dictionary=True)
            
            # Obtener URLs antiguas para eliminar archivos físicos
            cur.execute(
                "SELECT url_archivos FROM evidencia WHERE id_evidencia = %s AND estado = 1",
                (id_evidencia,)
            )
            row = cur.fetchone()
            
            if not row:
                return False
            
            url_antigua = row['url_archivos']
            
            # Eliminar archivo físico antiguo
            if url_antigua:
                path_antiguo = os.path.join(
                    os.path.dirname(__file__), '..', 'static', url_antigua
                )
                if os.path.exists(path_antiguo):
                    try:
                        os.remove(path_antiguo)
                    except Exception as e:
                        print(f"No se pudo eliminar archivo antiguo: {e}")
            
            # Comprimir y guardar nueva imagen (solo la primera si hay varias)
            nueva_url = self.__comprimir_y_guardar_imagen(self.__fotos[0])
            nueva_etapa = self.__etapas.get(0, "antes")
            nuevo_nombre = self._limpiar_texto(self.__fotos[0].filename, 45)
            
            # Actualizar registro en BD
            sql = """
                UPDATE evidencia 
                SET fotos = %s, url_archivos = %s, etapa = %s 
                WHERE id_evidencia = %s AND estado = 1
            """
            cur.execute(sql, (nuevo_nombre, nueva_url, nueva_etapa, id_evidencia))
            conn.commit()
            
            return cur.rowcount > 0
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar evidencia: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __eliminar_logico_db(self, id_evidencia: int):
        """
        Método PRIVADO que realiza el borrado LÓGICO.
        No elimina físicamente, solo cambia el estado a 0.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Borrado lógico: cambiar estado a 0
            sql = "UPDATE evidencia SET estado = 0 WHERE id_evidencia = %s"
            cur.execute(sql, (id_evidencia,))
            conn.commit()
            
            return cur.rowcount > 0
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error en borrado lógico: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __obtener_evidencia_por_id_db(self, id_evidencia: int):
        """Método PRIVADO que obtiene una evidencia por su ID."""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            
            cur = conn.cursor(dictionary=True)
            
            sql = """
                SELECT id_evidencia, fotos, url_archivos, fecha_registro, etapa, estado
                FROM evidencia 
                WHERE id_evidencia = %s AND estado = 1
            """
            cur.execute(sql, (id_evidencia,))
            return cur.fetchone()
            
        except Exception as e:
            print(f"Error al obtener evidencia: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __obtener_todas_evidencias_db(self):
        """Método PRIVADO que obtiene todas las evidencias activas."""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            
            cur = conn.cursor(dictionary=True)
            
            # Consulta solo evidencias activas (estado = 1)
            sql = """
                SELECT id_evidencia, fotos, url_archivos, fecha_registro, etapa, estado
                FROM evidencia 
                WHERE estado = 1 
                ORDER BY fecha_registro DESC
            """
            cur.execute(sql)
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error al obtener evidencias: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __validar_evidencia_activa_db(self, id_evidencia: int) -> bool:
        """
        Método PRIVADO que valida si una evidencia existe y está activa.
        Validación en tiempo real según instrucciones del profesor.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            sql = "SELECT id_evidencia FROM evidencia WHERE id_evidencia = %s AND estado = 1"
            cur.execute(sql, (id_evidencia,))
            return cur.fetchone() is not None
            
        except Exception:
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # ========== MÉTODOS PÚBLICOS (Interfaz Pública - Capa de Seguridad) ==========
    
    def registrar_evidencias(self, files, form_data):
        """
        Método PÚBLICO que actúa como interfaz para registrar evidencias.
        Valida datos y llama al método privado.
        """
        try:
            self.set_fotos(files)
            self.set_etapas(form_data)
            return self.__guardar_evidencias_db()
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al registrar: {e}")
            return None
    
    def actualizar_evidencia(self, id_evidencia, files, form_data):
        """
        Método PÚBLICO que actúa como interfaz para actualizar evidencias.
        """
        try:
            # Validar que la evidencia existe y está activa
            if not self.__validar_evidencia_activa_db(id_evidencia):
                raise ValueError("La evidencia no existe o fue eliminada.")
            
            self.set_fotos(files)
            self.set_etapas(form_data)
            return self.__actualizar_evidencias_db(id_evidencia)
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al actualizar: {e}")
            return False
    
    def eliminar_evidencia(self, id_evidencia):
        """
        Método PÚBLICO que actúa como interfaz para el borrado lógico.
        """
        try:
            id_val = int(id_evidencia)
            if id_val <= 0:
                raise ValueError("ID inválido.")
            
            # Validar existencia antes de eliminar
            if not self.__validar_evidencia_activa_db(id_val):
                raise ValueError("La evidencia no existe o ya fue eliminada.")
            
            return self.__eliminar_logico_db(id_val)
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al eliminar: {e}")
            return False
    
    def obtener_evidencia_por_id(self, id_evidencia):
        """Método PÚBLICO para obtener una evidencia específica."""
        try:
            id_val = int(id_evidencia)
            if id_val <= 0:
                return None
            return self.__obtener_evidencia_por_id_db(id_val)
        except (ValueError, TypeError):
            return None
    
    def obtener_todas_evidencias(self):
        """Método PÚBLICO para obtener todas las evidencias activas."""
        return self.__obtener_todas_evidencias_db()
    
    def validar_evidencia_activa(self, id_evidencia):
        """
        Método PÚBLICO para validar existencia en tiempo real.
        Usado por Ajax/Fetch desde el frontend.
        """
        try:
            id_val = int(id_evidencia)
            return self.__validar_evidencia_activa_db(id_val)
        except (ValueError, TypeError):
            return False