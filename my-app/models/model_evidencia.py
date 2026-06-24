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
        # Atributos PRIVADOS
        self.__id_evidencia = None
        self.__nombres_archivos = []      # Lista de archivos FileStorage
        self.__urls = []                  # Lista de URLs generadas
        self.__etapas = []                # Lista de etapas (una por imagen)
        self.__fecha_registro = None
        self.__estado = 1                 # 1 = Activo, 0 = Inactivo (Borrado Lógico)
        
        # Carpeta de carga
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

    # ========== COMPRESIÓN Y GUARDADO DE IMAGEN (MÉTODO PRIVADO) ==========
    def __comprimir_y_guardar_imagen(self, file):
        """
        Comprime y guarda una imagen en formato JPEG con calidad 80%.
        Retorna la URL relativa.
        """
        filename = secure_filename(file.filename)
        # Generar nombre único con extensión .jpg (uniforme)
        base_name = os.path.splitext(filename)[0]
        unique_name = f"{uuid.uuid4().hex[:12]}_{base_name}.jpg"
        path = os.path.join(self.__upload_folder, unique_name)

        try:
            # Resetear el stream para evitar lecturas parciales
            file.stream.seek(0)
            
            # Intentar abrir la imagen con Pillow
            try:
                img = Image.open(file.stream)
            except UnidentifiedImageError:
                raise ValueError(f"No se pudo identificar la imagen '{filename}'. Formato no soportado.")
            except Exception as e:
                raise ValueError(f"Error al abrir la imagen '{filename}': {e}")

            # Convertir a RGB si es necesario (para PNG con alfa, GIF, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    # Usar el canal alfa como máscara
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode not in ('RGB', 'L'):
                # Cualquier otro modo lo convertimos a RGB
                img = img.convert('RGB')

            # Redimensionar si es muy grande
            if max(img.size) > self.MAX_DIMENSION:
                img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.Resampling.LANCZOS)

            # Guardar como JPEG con compresión
            img.save(path, format='JPEG', optimize=True, quality=self.CALIDAD_COMPRESION)
            print(f"[OK] Imagen guardada: {path} (tamaño: {os.path.getsize(path)} bytes)")

            # URL relativa para la BD
            return f"uploads/evidencias/{unique_name}"

        except Exception as e:
            print(f"[ERROR] __comprimir_y_guardar_imagen: {e}")
            raise ValueError(f"No se pudo procesar la imagen '{filename}': {e}")

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========
    def __guardar_evidencias_db(self):
        """
        Inserta una única fila con todas las URLs y etapas concatenadas.
        Retorna el ID insertado.
        """
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
        """
        Reemplaza las URLs antiguas por las nuevas (borra archivos físicos antiguos).
        Retorna True si se actualizó correctamente.
        """
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            if not conn:
                raise Exception("No se pudo conectar a la base de datos.")
            cur = conn.cursor(dictionary=True)

            # Obtener URLs antiguas
            cur.execute(
                "SELECT url_archivos FROM evidencia WHERE id_evidencia = %s AND estado = 1",
                (id_evidencia,)
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"No se encontró evidencia con ID {id_evidencia} o está inactiva.")

            urls_antiguas = row['url_archivos'].split(',') if row['url_archivos'] else []
            # Eliminar archivos físicos antiguos
            for url in urls_antiguas:
                path_antiguo = os.path.join(os.path.dirname(__file__), '..', 'static', url)
                if os.path.exists(path_antiguo):
                    try:
                        os.remove(path_antiguo)
                        print(f"[OK] Archivo antiguo eliminado: {path_antiguo}")
                    except Exception as e:
                        print(f"[WARN] No se pudo eliminar {path_antiguo}: {e}")

            # Comprimir y guardar nuevas imágenes
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
        """Borrado lógico: cambia estado a 0."""
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
        """Obtiene una evidencia activa por su ID."""
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
        """Obtiene todas las evidencias activas ordenadas por fecha descendente."""
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
        """Valida si una evidencia existe y está activa (estado=1)."""
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

    # ========== MÉTODOS PÚBLICOS (INTERFAZ SEGURA) ==========
    def registrar_evidencias(self, files, form_data):
        """
        Método PÚBLICO para registrar un conjunto de evidencias.
        Valida cantidad, formatos y etapas, luego llama al método privado.
        """
        try:
            # Validar cantidad
            if not (self.MIN_IMAGENES <= len(files) <= self.MAX_IMAGENES):
                raise ValueError(
                    f"Debe seleccionar entre {self.MIN_IMAGENES} y {self.MAX_IMAGENES} imágenes."
                )
            # Validar cada archivo
            for f in files:
                if f.content_length == 0:
                    raise ValueError(f"El archivo '{f.filename}' está vacío.")
                if not self._validar_nombre_archivo(f.filename):
                    # Solo advertencia, permitimos continuar (Pillow hará la validación real)
                    print(f"[WARN] El nombre '{f.filename}' no cumple el patrón, pero se intentará procesar.")

            # Guardar lista de archivos
            self.__nombres_archivos = list(files)

            # Extraer y validar etapas del formulario
            etapas = []
            for i in range(len(files)):
                etapa = form_data.get(f"etapa-foto-{i}", "antes").strip().lower()
                if etapa not in self._ETAPAS_VALIDAS:
                    raise ValueError(f"Etapa '{etapa}' no válida. Use: antes, durante o despues.")
                etapas.append(etapa)
            self.__etapas = etapas

            # Llamar al método privado que guarda en BD
            return self.__guardar_evidencias_db()

        except Exception as e:
            print(f"[ERROR] registrar_evidencias: {e}")
            raise  # Re-lanzar para que el controlador lo capture

    def actualizar_evidencia(self, id_evidencia, files, form_data):
        """
        Método PÚBLICO para actualizar un conjunto de evidencias.
        Reemplaza todas las imágenes existentes por las nuevas.
        """
        try:
            # Validar existencia
            if not self.__validar_evidencia_activa_db(id_evidencia):
                raise ValueError("La evidencia no existe o fue eliminada.")

            # Validar cantidad
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

            # Extraer y validar etapas
            etapas = []
            for i in range(len(files)):
                etapa = form_data.get(f"etapa-foto-{i}", "antes").strip().lower()
                if etapa not in self._ETAPAS_VALIDAS:
                    raise ValueError(f"Etapa '{etapa}' no válida.")
                etapas.append(etapa)
            self.__etapas = etapas

            return self.__actualizar_evidencias_db(id_evidencia)

        except Exception as e:
            print(f"[ERROR] actualizar_evidencia: {e}")
            raise

    def eliminar_evidencia(self, id_evidencia):
        """
        Método PÚBLICO para borrado lógico de una evidencia.
        """
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
        """Método PÚBLICO para obtener una evidencia por ID."""
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
        """Método PÚBLICO para validar existencia en tiempo real (usado por Ajax)."""
        try:
            id_val = int(id_evidencia)
            return self.__validar_evidencia_activa_db(id_val)
        except (ValueError, TypeError):
            return False