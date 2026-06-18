import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from conexion.conexionBD import connectionBD

class EvidenciaModel:
    def __init__(self):
        # Atributos privados para encapsulamiento
        self.__id_evidencia = None
        self.__fotos = []
        self.__etapas = {}
        self.__url_archivos = None
        self.__fecha_registro = None
        self.__estado = 1
        
        # Directorio de carga
        self.upload_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'evidencias')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)

    # --- Getters y Setters ---
    def set_fotos(self, files):
        if not (3 <= len(files) <= 5):
            raise ValueError("Debe seleccionar entre 3 y 5 imágenes por informe.")
        self.__fotos = files

    def set_url_archivos(self, url):
        self.__url_archivos = url
        
    def set_etapas(self, form_data):
        self.__etapas = {f"foto-{i}": form_data.get(f"etapa-foto-{i}") for i in range(len(self.__fotos))}

    # --- Métodos de Lógica de Negocio ---
    def __comprimir_y_guardar_imagen(self, file):
        """Comprime y guarda una imagen, retornando su nueva URL."""
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"
        path = os.path.join(self.upload_folder, unique_name)
        
        # Compresión con Pillow
        img = Image.open(file.stream)
        img.save(path, optimize=True, quality=80) # Calidad del 80%
        
        # Retorna la URL relativa para guardar en la BD
        return f"static/uploads/evidencias/{unique_name}"

    def __guardar_evidencias_db(self):
        """Guarda el informe y las evidencias asociadas en la base de datos."""
        conn = None
        cur = None
        try:
            conn = connectionBD()
            cur = conn.cursor()
            
            # Bucle para guardar cada foto con su etapa
            sql = "INSERT INTO evidencia (fotos, url_archivos, fecha_registro, estado, etapa) VALUES (%s, %s, %s, 1, %s)"
            for i, file in enumerate(self.__fotos):
                url = self.__comprimir_y_guardar_imagen(file)
                etapa = self.__etapas.get(f"foto-{i}", "antes") # 'antes' por defecto
                nombre_referencia = file.filename
                
                # En esta versión simplificada, cada foto es un registro
                cur.execute(sql, (nombre_referencia, url, datetime.now(), etapa))
                
            conn.commit()
            return True # Retornamos éxito

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error al guardar informe y evidencias: {e}")
            return None
        finally:
            if 'cur' in locals(): cur.close()
            if 'conn' in locals(): conn.close()

    def get_all_evidencias(self):
        conn = connectionBD()
        cur = conn.cursor(dictionary=True)
        try:
            # Consulta simple a la tabla evidencia
            sql = "SELECT * FROM evidencia WHERE estado = 1 ORDER BY fecha_registro DESC"
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    # --- Interfaz Pública ---
    def registrar_evidencias(self, files, form_data):
        self.set_fotos(files)
        self.set_etapas(form_data)
        return self.__guardar_evidencias_db()