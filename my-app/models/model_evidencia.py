"""
EvidenciaModel — Modelo SOLID/POO para gestión de evidencias fotográficas.
Implementa encapsulamiento, validaciones Regex, borrado lógico, compresión de imágenes,
y logs detallados para depuración.
Una única fila por conjunto de evidencias (3-5 imágenes).
"""

import os
import re
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from conexion.conexionBD import connectionBD_invilara


class EvidenciaModel:
    """Repositorio de evidencias fotográficas con compresión y validación."""

    # Regex flexible: solo verifica que tenga una extensión (cualquier extensión)
    _RE_NOMBRE_ARCHIVO = re.compile(r'^[\w\-. áéíóúÁÉÍÓÚñÑ()]{1,100}\.[a-zA-Z0-9]{1,5}$')
    _RE_URL = re.compile(r'^[\w\-/. ]{10,200}$')
    _ETAPAS_VALIDAS = {'antes', 'durante', 'despues'}
    
    MAX_IMAGENES = 5
    MIN_IMAGENES = 3
    CALIDAD_COMPRESION = 80
    MAX_DIMENSION = 1920

    def __init__(self):
        self.__id_evidencia = None
        self.__nombres_archivos = []
        self.__urls = []
        self.__etapas = []
        self.__fecha_registro = None
        self.__estado = 1
        
        self.__upload_folder = os.path.join(
            os.path.dirname(__file__), '..', 'static', 'uploads', 'evidencias'
        )
        if not os.path.exists(self.__upload_folder):
            os.makedirs(self.__upload_folder, exist_ok=True)
            print(f"[INFO] Carpeta de evidencias creada: {self.__upload_folder}")

    # ========== GETTERS Y SETTERS ==========
    def get_id_evidencia(self):
        return self.__id_evidencia

    def set_id_evidencia(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de evidencia debe ser un entero positivo.")
        self.__id_evidencia = valor

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 o 1.")
        self.__estado = valor

    # ========== MÉTODOS PRIVADOS DE VALIDACIÓN ==========
    def _validar_nombre_archivo(self, nombre: str) -> bool:
        """Valida que el nombre tenga una extensión, sin restringir formato."""
        return bool(self._RE_NOMBRE_ARCHIVO.match(nombre))

    def _validar_url(self, url: str) -> bool:
        """Valida que la URL generada tenga formato esperado."""
        return bool(self._RE_URL.match(url))

    @staticmethod
    def _limpiar_texto(texto: str, max_len: int = 100) -> str:
        """Sanitiza texto para evitar inyecciones."""
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    # ========== MÉTODO PRIVADO: EXTRAER ETAPAS ==========
    def __extraer_etapas(self, form_data, num_files):
        """
        Extrae las etapas del form_data. Soporta dos formatos:
        - 'etapa-foto-0', 'etapa-foto-1', etc. (desde inputs del form)
        - 'etapas' como lista (desde JS manual)
        """
        etapas = []
        
        # Intentar formato 'etapa-foto-{i}' primero
        for i in range(num_files):
            etapa = form_data.get(f"etapa-foto-{i}")
            if etapa:
                etapa = etapa.strip().lower()
                if etapa not in self._ETAPAS_VALIDAS:
                    raise ValueError(f"Etapa '{etapa}' no válida. Use: antes, durante o despues.")
                etapas.append(etapa)
        
        # Si no se encontraron etapas en formato 'etapa-foto-{i}', intentar 'etapas'
        if not etapas:
            etapas_list = form_data.getlist('etapas')
            if etapas_list:
                for etapa in etapas_list:
                    etapa = etapa.strip().lower()
                    if etapa not in self._ETAPAS_VALIDAS:
                        raise ValueError(f"Etapa '{etapa}' no válida. Use: antes, durante o despues.")
                    etapas.append(etapa)
        
        # Si aún no hay etapas, usar default
        if not etapas:
            etapas = ['antes'] * num_files
        
        # Asegurar que haya una etapa por archivo
        while len(etapas) < num_files:
            etapas.append('antes')
        
        return etapas[:num_files]

    # ========== COMPRESIÓN Y GUARDADO DE IMAGEN ==========
    def __comprimir_y_guardar_imagen(self, file):
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]
        unique_name = f"{uuid.uuid4().hex[:12]}_{base_name}.jpg"
        path = os.path.join(self.__upload_folder, unique_name)

        try:
            file.stream.seek(0)
            
            try:
                img = Image.open(file.stream)
            except UnidentifiedImageError:
                raise ValueError(f"No se pudo identificar la imagen '{filename}'. Formato no soportado.")
            except Exception as e:
                raise ValueError(f"Error al abrir la imagen '{filename}': {e}")

            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            if max(img.size) > self.MAX_DIMENSION:
                img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.Resampling.LANCZOS)

            img.save(path, format='JPEG', optimize=True, quality=self.CALIDAD_COMPRESION)
            print(f"[OK] Imagen guardada: {path} (tamaño: {os.path.getsize(path)} bytes)")

            return f"uploads/evidencias/{unique_name}"

        except Exception as e:
            print(f"[ERROR] __comprimir_y_guardar_imagen: {e}")
            raise ValueError(f"No se pudo procesar la imagen '{filename}': {e}")

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========
    def __guardar_evidencias_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                raise Exception("No se pudo conectar a la base de datos.")
            cur = conn.cursor()

            urls = []
            etapas = []
            nombres = []
            for i, file in enumerate(self.__nombres_archivos):
                print(f"[DEBUG] Procesando archivo {i}: {file.filename}")
                url = self.__comprimir_y_guardar_imagen(file)
                if not self._validar_url(url):
                    raise ValueError(f"URL generada no válida: {url}")
                urls.append(url)
                etapa = self.__etapas[i] if i < len(self.__etapas) else 'antes'
                etapas.append(etapa)
                nombres.append(file.filename)

            urls_str = ','.join(urls)
            etapas_str = ','.join(etapas)
            descripcion = ', '.join(nombres[:3]) if nombres else 'Evidencia'

            sql = """
                INSERT INTO evidencia 
                (fotos, url_archivos, fecha_registro, estado, etapa) 
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (descripcion[:100], urls_str, datetime.now(), 1, etapas_str)
            cur.execute(sql, params)
            conn.commit()
            nuevo_id = cur.lastrowid
            print(f"[OK] Insertado registro de evidencias con ID: {nuevo_id}")
            return nuevo_id

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] __guardar_evidencias_db: {e}")
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __actualizar_evidencias_db(self, id_evidencia):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                raise Exception("No se pudo conectar a la base de datos.")
            cur = conn.cursor(dictionary=True)

            cur.execute(
                "SELECT url_archivos FROM evidencia WHERE id_evidencia = %s AND estado = 1",
                (id_evidencia,)
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"No se encontró evidencia con ID {id_evidencia} o está inactiva.")

            urls_antiguas = row['url_archivos'].split(',') if row['url_archivos'] else []
            for url in urls_antiguas:
                path_antiguo = os.path.join(os.path.dirname(__file__), '..', 'static', url)
                if os.path.exists(path_antiguo):
                    try:
                        os.remove(path_antiguo)
                        print(f"[OK] Archivo antiguo eliminado: {path_antiguo}")
                    except Exception as e:
                        print(f"[WARN] No se pudo eliminar {path_antiguo}: {e}")

            nuevas_urls = []
            nuevas_etapas = []
            for i, file in enumerate(self.__nombres_archivos):
                print(f"[DEBUG] Actualizando archivo {i}: {file.filename}")
                url = self.__comprimir_y_guardar_imagen(file)
                if not self._validar_url(url):
                    raise ValueError(f"URL generada no válida: {url}")
                nuevas_urls.append(url)
                etapa = self.__etapas[i] if i < len(self.__etapas) else 'antes'
                nuevas_etapas.append(etapa)

            urls_str = ','.join(nuevas_urls)
            etapas_str = ','.join(nuevas_etapas)
            descripcion = ', '.join([f.filename for f in self.__nombres_archivos[:3]]) or 'Evidencia'

            sql = """
                UPDATE evidencia 
                SET fotos = %s, url_archivos = %s, etapa = %s 
                WHERE id_evidencia = %s AND estado = 1
            """
            cur.execute(sql, (descripcion[:100], urls_str, etapas_str, id_evidencia))
            conn.commit()
            afectados = cur.rowcount
            print(f"[OK] Actualizadas {afectados} fila(s) para ID {id_evidencia}")
            return afectados > 0

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] __actualizar_evidencias_db: {e}")
            raise
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __eliminar_logico_db(self, id_evidencia):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            cur = conn.cursor()
            sql = "UPDATE evidencia SET estado = 0 WHERE id_evidencia = %s"
            cur.execute(sql, (id_evidencia,))
            conn.commit()
            afectados = cur.rowcount
            print(f"[OK] Borrado lógico aplicado a ID {id_evidencia}, filas afectadas: {afectados}")
            return afectados > 0
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ERROR] __eliminar_logico_db: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __obtener_evidencia_por_id_db(self, id_evidencia):
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
            print(f"[ERROR] __obtener_evidencia_por_id_db: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __obtener_todas_evidencias_db(self):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            cur = conn.cursor(dictionary=True)
            sql = """
                SELECT id_evidencia, fotos, url_archivos, fecha_registro, etapa, estado
                FROM evidencia 
                WHERE estado = 1 
                ORDER BY fecha_registro DESC
            """
            cur.execute(sql)
            return cur.fetchall()
        except Exception as e:
            print(f"[ERROR] __obtener_todas_evidencias_db: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def __validar_evidencia_activa_db(self, id_evidencia):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            cur = conn.cursor()
            sql = "SELECT id_evidencia FROM evidencia WHERE id_evidencia = %s AND estado = 1"
            cur.execute(sql, (id_evidencia,))
            existe = cur.fetchone() is not None
            print(f"[DEBUG] Validación ID {id_evidencia}: {'existe' if existe else 'no existe'}")
            return existe
        except Exception as e:
            print(f"[ERROR] __validar_evidencia_activa_db: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # ========== MÉTODOS PÚBLICOS ==========
    def registrar_evidencias(self, files, form_data):
        try:
            if not (self.MIN_IMAGENES <= len(files) <= self.MAX_IMAGENES):
                raise ValueError(
                    f"Debe seleccionar entre {self.MIN_IMAGENES} y {self.MAX_IMAGENES} imágenes."
                )
            
            for f in files:
                if f.content_length == 0:
                    raise ValueError(f"El archivo '{f.filename}' está vacío.")
                if not self._validar_nombre_archivo(f.filename):
                    print(f"[WARN] El nombre '{f.filename}' no cumple el patrón, pero se intentará procesar.")

            self.__nombres_archivos = list(files)
            self.__etapas = self.__extraer_etapas(form_data, len(files))

            return self.__guardar_evidencias_db()

        except Exception as e:
            print(f"[ERROR] registrar_evidencias: {e}")
            raise

    def actualizar_evidencia(self, id_evidencia, files, form_data):
        try:
            if not self.__validar_evidencia_activa_db(id_evidencia):
                raise ValueError("La evidencia no existe o fue eliminada.")

            if not (self.MIN_IMAGENES <= len(files) <= self.MAX_IMAGENES):
                raise ValueError(
                    f"Debe seleccionar entre {self.MIN_IMAGENES} y {self.MAX_IMAGENES} imágenes."
                )
            
            for f in files:
                if f.content_length == 0:
                    raise ValueError(f"El archivo '{f.filename}' está vacío.")
                if not self._validar_nombre_archivo(f.filename):
                    print(f"[WARN] El nombre '{f.filename}' no cumple el patrón, pero se intentará procesar.")

            self.__nombres_archivos = list(files)
            self.__etapas = self.__extraer_etapas(form_data, len(files))

            return self.__actualizar_evidencias_db(id_evidencia)

        except Exception as e:
            print(f"[ERROR] actualizar_evidencia: {e}")
            raise

    def eliminar_evidencia(self, id_evidencia):
        try:
            id_val = int(id_evidencia)
            if id_val <= 0:
                raise ValueError("ID inválido.")
            if not self.__validar_evidencia_activa_db(id_val):
                raise ValueError("La evidencia no existe o ya fue eliminada.")
            return self.__eliminar_logico_db(id_val)
        except Exception as e:
            print(f"[ERROR] eliminar_evidencia: {e}")
            raise

    def obtener_evidencia_por_id(self, id_evidencia):
        try:
            id_val = int(id_evidencia)
            if id_val <= 0:
                return None
            return self.__obtener_evidencia_por_id_db(id_val)
        except (ValueError, TypeError):
            return None

    def obtener_todas_evidencias(self):
        return self.__obtener_todas_evidencias_db()

    def validar_evidencia_activa(self, id_evidencia):
        try:
            id_val = int(id_evidencia)
            return self.__validar_evidencia_activa_db(id_val)
        except (ValueError, TypeError):
            return False