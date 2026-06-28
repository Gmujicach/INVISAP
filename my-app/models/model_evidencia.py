<<<<<<< HEAD
"""
EvidenciaModel — Modelo SOLID/POO para gestión de evidencias fotográficas.
Implementa encapsulamiento, validaciones Regex, borrado lógico, compresión de imágenes.
"""

=======
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
import os
import re
import uuid
import io
from datetime import datetime
from PIL import Image
from conexion.conexionBD import connectionBD_invilara

class EvidenciaModel:
<<<<<<< HEAD
    """Repositorio de evidencias fotográficas con compresión y validación."""

    # Regex para validar nombres y URLs (VARCHAR 45 y 90 en la BD)
    _RE_NOMBRE_ARCHIVO = re.compile(r'^[\w\-. áéíóúÁÉÍÓÚñÑ()]{1,100}\.[a-zA-Z0-9]{1,5}$')
    _RE_URL = re.compile(r'^[\w\-/. ]{10,90}$')  
    _ETAPAS_VALIDAS = {'antes', 'durante', 'despues'}
    
=======
    _RE_ETAPA = re.compile(r'^(antes|durante|despues)$')
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
    MAX_IMAGENES = 5
    MIN_IMAGENES = 3
    CALIDAD_COMPRESION = 80
    MAX_DIMENSION = 1920

    def __init__(self):
        self.__id_evidencia = None
        self.__archivos = []
        self.__etapas = []
        self.__estado = 1
        self.__upload_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'evidencias')
        if not os.path.exists(self.__upload_folder):
            os.makedirs(self.__upload_folder, exist_ok=True)

    def get_id_evidencia(self):
        return self.__id_evidencia

    def set_id_evidencia(self, valor):
        if not isinstance(valor, int) or valor <= 0:
<<<<<<< HEAD
            raise ValueError("ID de evidencia debe ser un entero positivo.")
=======
            raise ValueError("ID invalido")
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
        self.__id_evidencia = valor

    def __validar_etapas_regex(self, etapas):
        if not etapas or not isinstance(etapas, (list, tuple)):
            raise ValueError("No se recibieron etapas")
        for i, etapa in enumerate(etapas):
            if not isinstance(etapa, str):
                raise ValueError(f"La etapa {i} no es un texto valido")
            etapa_limpia = etapa.strip().lower()
            if not self._RE_ETAPA.match(etapa_limpia):
                raise ValueError(f"Etapa invalida: '{etapa}' - Debe ser 'antes', 'durante' o 'despues'")
        return True

<<<<<<< HEAD
    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 o 1.")
        self.__estado = valor

    # ========== MÉTODOS PRIVADOS DE VALIDACIÓN ==========
    def _validar_nombre_archivo(self, nombre: str) -> bool:
        return bool(self._RE_NOMBRE_ARCHIVO.match(nombre))

    def _validar_url(self, url: str) -> bool:
        return bool(self._RE_URL.match(url))

    @staticmethod
    def _limpiar_texto(texto: str, max_len: int = 100) -> str:
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    def __extraer_etapas(self, form_data, num_files):
        etapas = []
        for i in range(num_files):
            etapa = form_data.get(f"etapa-foto-{i}")
            if etapa:
                etapa = etapa.strip().lower()
                if etapa not in self._ETAPAS_VALIDAS:
                    raise ValueError(f"Etapa '{etapa}' no válida.")
                etapas.append(etapa)
        
        # Fallback para otros formatos
        if not etapas:
            etapas_list = form_data.getlist('etapas')
            for etapa in etapas_list:
                etapa = etapa.strip().lower()
                if etapa in self._ETAPAS_VALIDAS:
                    etapas.append(etapa)
        
        while len(etapas) < num_files:
            etapas.append('antes')
        return etapas[:num_files]

    # ========== COMPRESIÓN Y GUARDADO DE IMAGEN ==========
    def __comprimir_y_guardar_imagen(self, file):
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]
        
        # Truncar nombre base para que la URL completa no exceda 90 chars
        base_name = base_name[:50]
        unique_name = f"{uuid.uuid4().hex[:12]}_{base_name}.jpg"
=======
    def __comprimir_y_guardar_imagen(self, file):
        unique_name = f"{uuid.uuid4().hex}.jpg"
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
        path = os.path.join(self.__upload_folder, unique_name)
        try:
            file_bytes = file.read()
<<<<<<< HEAD
            if not file_bytes:
                raise ValueError(f"El archivo '{filename}' está vacío.")
            
=======
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
            img = Image.open(io.BytesIO(file_bytes))
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])
                else:
                    background.paste(img)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            if max(img.size) > self.MAX_DIMENSION:
                img.thumbnail((self.MAX_DIMENSION, self.MAX_DIMENSION), Image.Resampling.LANCZOS)
            img.save(path, format='JPEG', optimize=True, quality=self.CALIDAD_COMPRESION)
            return f"uploads/evidencias/{unique_name}"
<<<<<<< HEAD

        except Exception as e:
            raise ValueError(f"Error al procesar '{filename}': {e}")
=======
        except Exception as e:
            raise ValueError(f"Error al procesar la imagen: {str(e)}")
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac

    def __guardar_evidencias_db(self):
<<<<<<< HEAD
        """
        Guarda cada imagen como una fila independiente en la BD.
        Cumple con el tipo ENUM de la columna 'etapa' y el límite VARCHAR(90).
        """
        conn = None
        cur = None
        ids_insertados = []
        try:
            conn = connectionBD_invilara()
            if not conn:
                raise Exception("Error de conexión a la base de datos.")
            cur = conn.cursor()

            sql = "INSERT INTO evidencia (fotos, url_archivos, fecha_registro, estado, etapa) VALUES (%s, %s, %s, %s, %s)"
            
            for i, file in enumerate(self.__archivos):
                url = self.__comprimir_y_guardar_imagen(file)
                if not self._validar_url(url):
                    raise ValueError(f"URL inválida: {url}")
                
                etapa = self.__etapas[i]
                nombre_referencia = self._limpiar_texto(file.filename, 45)
                
=======
        conn = connectionBD_invilara()
        cur = conn.cursor()
        ids_insertados = []
        try:
            sql = "INSERT INTO evidencia (fotos, url_archivos, fecha_registro, estado, etapa) VALUES (%s, %s, %s, %s, %s)"
            for i, file in enumerate(self.__archivos):
                url = self.__comprimir_y_guardar_imagen(file)
                etapa = self.__etapas[i].strip().lower()
                nombre_referencia = re.sub(r'[<>\'";\\]', '', file.filename).strip()[:45]
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
                params = (nombre_referencia, url, datetime.now(), 1, etapa)
                cur.execute(sql, params)
                ids_insertados.append(cur.lastrowid)
            conn.commit()
            return ids_insertados
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error en base de datos: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def __actualizar_evidencias_db(self, id_evidencia):
<<<<<<< HEAD
        """Actualiza un registro específico de evidencia (1:1)."""
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
            cur = conn.cursor(dictionary=True)

            cur.execute("SELECT url_archivos FROM evidencia WHERE id_evidencia = %s AND estado = 1", (id_evidencia,))
            row = cur.fetchone()
            if not row: raise ValueError("No existe el registro activo.")

            # Eliminar físico antiguo
            p = os.path.join(os.path.dirname(__file__), '..', 'static', row['url_archivos'])
            if os.path.exists(p): os.remove(p)

            file = self.__archivos[0]
            url = self.__comprimir_y_guardar_imagen(file)
            etapa = self.__etapas[0]
            nombre_referencia = self._limpiar_texto(file.filename, 45)

            sql = "UPDATE evidencia SET fotos = %s, url_archivos = %s, etapa = %s WHERE id_evidencia = %s"
=======
        conn = connectionBD_invilara()
        cur = conn.cursor()
        try:
            file = self.__archivos[0]
            url = self.__comprimir_y_guardar_imagen(file)
            etapa = self.__etapas[0].strip().lower()
            nombre_referencia = re.sub(r'[<>\'";\\]', '', file.filename).strip()[:45]
            sql = "UPDATE evidencia SET fotos = %s, url_archivos = %s, etapa = %s WHERE id_evidencia = %s AND estado = 1"
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
            cur.execute(sql, (nombre_referencia, url, etapa, id_evidencia))
            conn.commit()
            return cur.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Error en base de datos: {str(e)}")
        finally:
            cur.close()
            conn.close()

    def __eliminar_logico_db(self, id_evidencia):
        conn = connectionBD_invilara()
        cur = conn.cursor()
        try:
<<<<<<< HEAD
            conn = connectionBD_invilara()
            cur = conn.cursor()
=======
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
            cur.execute("UPDATE evidencia SET estado = 0 WHERE id_evidencia = %s", (id_evidencia,))
            conn.commit()
            return cur.rowcount > 0
        finally:
            cur.close()
            conn.close()

    def __obtener_evidencia_por_id_db(self, id_evidencia):
        conn = connectionBD_invilara()
        cur = conn.cursor(dictionary=True)
        try:
<<<<<<< HEAD
            conn = connectionBD_invilara()
            cur = conn.cursor(dictionary=True)
=======
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
            cur.execute("SELECT * FROM evidencia WHERE id_evidencia = %s AND estado = 1", (id_evidencia,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def __obtener_todas_evidencias_db(self):
        conn = connectionBD_invilara()
        cur = conn.cursor(dictionary=True)
        try:
<<<<<<< HEAD
            conn = connectionBD_invilara()
            cur = conn.cursor(dictionary=True)
=======
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
            cur.execute("SELECT * FROM evidencia WHERE estado = 1 ORDER BY fecha_registro DESC")
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def __validar_evidencia_activa_db(self, id_evidencia):
        conn = connectionBD_invilara()
        cur = conn.cursor()
        try:
<<<<<<< HEAD
            conn = connectionBD_invilara()
            cur = conn.cursor()
            cur.execute("SELECT id_evidencia FROM evidencia WHERE id_evidencia = %s AND estado = 1", (id_evidencia,))
=======
            cur.execute("SELECT 1 FROM evidencia WHERE id_evidencia = %s AND estado = 1", (id_evidencia,))
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
            return cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

    def registrar_evidencias(self, files, etapas):
        if not files or len(files) == 0:
            raise ValueError("No se recibieron archivos")
        if not etapas or len(etapas) == 0:
            raise ValueError("No se recibieron etapas")
        if len(files) != len(etapas):
            raise ValueError(f"Inconsistencia: {len(files)} imagenes vs {len(etapas)} etapas")
        if not (self.MIN_IMAGENES <= len(files) <= self.MAX_IMAGENES):
<<<<<<< HEAD
            raise ValueError(f"Debe subir entre {self.MIN_IMAGENES} y {self.MAX_IMAGENES} fotos.")
        self.__archivos = list(files)
        self.__etapas = self.__extraer_etapas(form_data, len(files))
=======
            raise ValueError(f"Debe subir entre {self.MIN_IMAGENES} y {self.MAX_IMAGENES} imagenes")
        self.__validar_etapas_regex(etapas)
        self.__archivos = files
        self.__etapas = etapas
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
        return self.__guardar_evidencias_db()

    def actualizar_evidencia(self, id_evidencia, files, etapas):
        if not self.__validar_evidencia_activa_db(id_evidencia):
<<<<<<< HEAD
            raise ValueError("No existe.")
        if not files:
            raise ValueError("Debe seleccionar una foto.")
        self.__archivos = list(files)
        self.__etapas = self.__extraer_etapas(form_data, len(files))
=======
            raise ValueError("La evidencia no existe")
        if not files or len(files) == 0:
            raise ValueError("Debe seleccionar una imagen para modificar")
        if len(files) != 1:
            raise ValueError("Solo se permite una imagen para modificar")
        if not etapas or len(etapas) == 0:
            raise ValueError("Debe seleccionar una etapa")
        if len(etapas) != 1:
            raise ValueError("Solo se permite una etapa para modificar")
        self.__validar_etapas_regex(etapas)
        self.__archivos = files
        self.__etapas = etapas
>>>>>>> 2403694eeee3cf3342e685fba13279be51fc44ac
        return self.__actualizar_evidencias_db(id_evidencia)

    def eliminar_evidencia(self, id_evidencia):
        return self.__eliminar_logico_db(id_evidencia)

    def obtener_evidencia_por_id(self, id_evidencia):
        return self.__obtener_evidencia_por_id_db(id_evidencia)

    def obtener_todas_evidencias(self):
        return self.__obtener_todas_evidencias_db()

    def validar_evidencia_activa(self, id_evidencia):
        return self.__validar_evidencia_activa_db(id_evidencia)