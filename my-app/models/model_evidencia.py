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
        self.__etapas = {} # To store stage for each photo
        self.__observaciones = ""
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

    def set_etapas_y_observaciones(self, form_data):
        self.__etapas = {f"foto-{i}": form_data.get(f"etapa-foto-{i}") for i in range(len(self.__fotos))}
        self.__observaciones = form_data.get('observaciones', '')

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

    def __guardar_informe_y_evidencias_db(self):
        """Guarda el informe y las evidencias asociadas en la base de datos."""
        conn = None
        cur = None
        try:
            conn = connectionBD()
            cur = conn.cursor()

            # 1. Crear el registro principal en 'informe_avance_obra'
            sql_informe = "INSERT INTO informe_avance_obra (fecha, estado_informe, poblacion_beneficiada, tipo_informe, observaciones, estado) VALUES (%s, %s, %s, %s, %s, 1)"
            # These values should come from the form, here are placeholders
            cur.execute(sql_informe, (datetime.now(), 'En Proceso', 'N/A', 'Inspección', self.__observaciones))
            id_informe_nuevo = cur.lastrowid

            # 2. Guardar cada foto en la tabla 'evidencia' y enlazar en 'informe_has_evidencia'
            sql_evidencia = "INSERT INTO evidencia (url_foto, etapa, fecha_registro, estado) VALUES (%s, %s, %s, 1)"
            sql_link = "INSERT INTO informe_has_evidencia (id_informe, id_evidencia) VALUES (%s, %s)"
            
            for i, file in enumerate(self.__fotos):
                url = self.__comprimir_y_guardar_imagen(file)
                etapa = self.__etapas.get(f"foto-{i}", "antes") # Default to 'antes' if not specified
                cur.execute(sql_evidencia, (url, etapa, datetime.now()))
                id_evidencia_nueva = cur.lastrowid
                cur.execute(sql_link, (id_informe_nuevo, id_evidencia_nueva))

            conn.commit()
            return id_informe_nuevo
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
            # This query now gets reports and their associated photos
            sql = """
                SELECT 
                    iao.id_informe, 
                    iao.fecha, 
                    iao.observaciones,
                    (SELECT COUNT(*) FROM v_informe_evidencias WHERE id_informe = iao.id_informe) as num_fotos
                FROM informe_avance_obra iao
                WHERE iao.estado = 1
                ORDER BY iao.fecha DESC
            """
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    # --- Interfaz Pública ---
    def registrar_informe_con_evidencias(self, files, form_data):
        self.set_fotos(files)
        self.set_etapas_y_observaciones(form_data)
        return self.__guardar_informe_y_evidencias_db()