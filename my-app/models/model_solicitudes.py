"""
SolicitudModel — Modelo SOLID/DRY para gestión de solicitudes.
Refactorizado con encapsulamiento, getters/setters y validaciones Regex.
"""
import re
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara

class SolicitudModel:
    """Repositorio y entidad de solicitudes."""

    _RE_CEDULA = re.compile(r'^\d{7,10}$')
    _RE_TELEFONO = re.compile(r'^(0414|0424|0412|0416|0426|0251)-?\d{7}$')
    _RE_CORREO = re.compile(r'^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.,\-áéíóúÁÉÍÓÚñÑ]{2,100}$', re.UNICODE)
    _RE_PROBLEMATICA = re.compile(r'^[\w\s\.,\!\?\-áéíóúÁÉÍÓÚñÑ]{15,500}$', re.UNICODE)

    TIPOS_SOLICITANTE_VALIDOS = {'Comunidad', 'Institucion', 'Particular'}
    ESTATUS_VALIDOS = {'Pendiente', 'En Proceso', 'Completada', 'Procesada', 'PENDIENTE'}
    MUNICIPIOS_VALIDOS = {
        'Iribarren', 'Palavecino', 'Jiménez', 'Morán', 
        'Crespo', 'Urdaneta', 'Simón Planas', 'Andrés Eloy Blanco', 'Torres'
    }
    TIPOS_PROBLEMATICA_VALIDOS = {
        'Servicios Básicos (Agua, Luz, Gas)', 'Infraestructura y Vialidad',
        'Salud y Asistencia Médica', 'Educación y Deporte',
        'Seguridad Ciudadana', 'Vivienda', 'Otros'
    }

    def __init__(self, id_solicitudes=None):
        self._id_solicitudes = id_solicitudes
        self._tipo_solicitud = None
        self._estatus_solicitud = 'Pendiente'
        self._problematica = None
        self._fecha = None
        self._solicitante_data = {} # Almacena datos del solicitante

    # --- GETTERS Y SETTERS CON VALIDACIÓN (ENCAPSULAMIENTO) ---
    def get_id(self):
        return self._id_solicitudes

    def get_tipo_solicitud(self):
        return self._tipo_solicitud

    def set_tipo_solicitud(self, valor):
        valor = str(valor or '').strip()
        if valor not in self.TIPOS_SOLICITANTE_VALIDOS:
            raise ValueError(f"Tipo de solicitud '{valor}' inválido.")
        self._tipo_solicitud = valor

    def get_estatus_solicitud(self):
        return self._estatus_solicitud

    def set_estatus_solicitud(self, valor):
        valor = self._limpiar(valor, 20)
        if valor not in self.ESTATUS_VALIDOS:
            valor = 'Pendiente'
        self._estatus_solicitud = valor

    def get_problematica(self):
        return self._problematica

    def set_problematica(self, valor, tipo_problematica=None):
        problematica_libre = self._limpiar(valor, 500)
        tipo_prob = self._limpiar(tipo_problematica, 50) if tipo_problematica else ""

        if tipo_prob and tipo_prob not in self.TIPOS_PROBLEMATICA_VALIDOS:
            raise ValueError(f"Categoría de problemática '{tipo_prob}' inválida.")

        problematica_final = problematica_libre
        if tipo_prob and problematica_libre:
            problematica_final = f"[{tipo_prob}] {problematica_libre}"
        elif tipo_prob:
            problematica_final = tipo_prob

        if not self._RE_PROBLEMATICA.match(problematica_final) and len(problematica_final.strip()) < 15:
            raise ValueError("La problemática debe tener al menos 15 caracteres válidos y evitar inyecciones.")
        self._problematica = problematica_final

    def get_fecha(self):
        return self._fecha

    def set_fecha(self, valor=None):
        fecha_raw = str(valor or '').strip()
        self._fecha = fecha_raw.replace('T', ' ') if fecha_raw else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def set_solicitante_data(self, datos: dict):
        """Asigna y valida los datos del solicitante dependiendo del tipo."""
        tipo = self._tipo_solicitud
        if not tipo:
            raise ValueError("Debe establecer el tipo de solicitud primero.")
        
        # Extraer los datos dependiendo del tipo de solicitante
        if tipo == 'Comunidad':
            cedula = datos.get('com_cedula', '')
            telefono = datos.get('com_telefono', '')
            correo = datos.get('com_correo', '')
            municipio = datos.get('com_municipio', '')
            parroquia = datos.get('com_parroquia', '')
            direccion = datos.get('com_ambito', '') # Se usa el ámbito como dirección si es comunidad
        elif tipo == 'Institucion':
            cedula = datos.get('inst_director_cedula', '')
            telefono = datos.get('inst_telefono', '')
            correo = datos.get('inst_correo', '')
            municipio = datos.get('inst_municipio', '')
            parroquia = datos.get('inst_parroquia', '')
            direccion = datos.get('inst_direccion', '')
        elif tipo == 'Particular':
            cedula = datos.get('part_cedula', '')
            telefono = datos.get('part_telefono', '')
            correo = datos.get('part_correo', '')
            municipio = datos.get('part_municipio', '')
            parroquia = datos.get('part_parroquia', '')
            direccion = datos.get('part_direccion', '')
        else:
            raise ValueError("Tipo de solicitud desconocido.")

        if not self._RE_CEDULA.match(str(cedula)):
            raise ValueError("Cédula inválida. Debe tener entre 7 y 10 dígitos numéricos sin puntos ni guiones.")
            
        if not self._RE_CORREO.match(correo):
            raise ValueError("Formato de correo electrónico inválido.")
            
        if not self._RE_TELEFONO.match(telefono):
            raise ValueError("Formato de teléfono inválido (ej: 04121234567 o 0412-1234567).")
            
        municipio = self._limpiar(municipio, 45)
        if municipio and municipio not in self.MUNICIPIOS_VALIDOS:
            raise ValueError(f"El municipio '{municipio}' no es válido.")
            
        parroquia = self._limpiar(parroquia, 45)
        if not parroquia:
            raise ValueError("Debe seleccionar una parroquia válida.")

        self._solicitante_data = {
            'tipo_solicitante': tipo,
            'cedula_persona': self._limpiar(cedula, 10),
            'direccion': self._limpiar(direccion, 200),
            'parroquia': parroquia,
            'municipio': municipio,
            'telefono': self._limpiar(telefono, 12),
            'correo': self._limpiar(correo, 45)
        }

        # Campos específicos por tipo
        if tipo == 'Comunidad':
            self._solicitante_data['nombre_comunidad'] = self._limpiar(datos.get('com_nombre', ''), 100)
            self._solicitante_data['ambito'] = self._limpiar(datos.get('com_ambito', ''), 45)
            self._solicitante_data['sector'] = self._limpiar(datos.get('com_sector', ''), 45)
        elif tipo == 'Institucion':
            self._solicitante_data['nombre_representante'] = self._limpiar(datos.get('inst_director_nombre', ''), 45)
            self._solicitante_data['razon_social'] = self._limpiar(datos.get('inst_nombre', ''), 120)
        elif tipo == 'Particular':
            self._solicitante_data['nombre'] = self._limpiar(datos.get('part_nombre', ''), 45)
            self._solicitante_data['apellido'] = self._limpiar(datos.get('part_apellido', ''), 45)


    # --- MÉTODOS PRIVADOS (Base de Datos) ---
    @staticmethod
    def _con():
        return connectionBD_invilara()

    @staticmethod
    def _cerrar(conn, cursor):
        try:
            if cursor: cursor.close()
        except Exception: pass
        try:
            if conn: conn.close()
        except Exception: pass

    @staticmethod
    def _limpiar(valor: str, max_len: int = 255) -> str:
        if not isinstance(valor, str):
            valor = str(valor or '')
        return re.sub(r'[<>\'";\\]', '', valor).strip()[:max_len]

    def _formatear_fecha(self, fecha):
        if fecha is None: return ''
        if isinstance(fecha, datetime): return fecha.strftime('%a %d-%m-%Y %I:%M:%S %p')
        if isinstance(fecha, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
                try: return datetime.strptime(fecha, fmt).strftime('%a %d-%m-%Y %I:%M:%S %p')
                except ValueError: continue
            return fecha
        return str(fecha)

    def _sql_buscar_persona(self, cursor, cedula: str):
        sql = "SELECT id_persona FROM persona WHERE cedula_persona = %s LIMIT 1"
        cursor.execute(sql, (cedula,))
        row = cursor.fetchone()
        return row['id_persona'] if isinstance(row, dict) else (row[0] if row else None)

    def _sql_insertar_persona(self, cursor, datos: dict) -> int:
        sql = """
            INSERT INTO persona (cedula_persona, direccion, parroquia, municipio, telefono, correo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cedula = int(''.join(filter(str.isdigit, str(datos['cedula_persona']))) or 0)
        cursor.execute(sql, (
            cedula, datos['direccion'], datos['parroquia'], 
            datos['municipio'], datos['telefono'], datos['correo']
        ))
        return cursor.lastrowid

    def _sql_insertar_subtipo(self, cursor, persona_id: int, datos: dict):
        tipo = datos['tipo_solicitante']
        if tipo == 'Particular':
            sql = "INSERT INTO particular (nombre, apellido, persona_id_persona) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos.get('nombre'), datos.get('apellido'), persona_id))
        elif tipo == 'Comunidad':
            sql = "INSERT INTO comunidad (nombre_comunidad, ambito, sector, persona_id_persona) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (datos.get('nombre_comunidad'), datos.get('ambito'), datos.get('sector'), persona_id))
        elif tipo == 'Institucion':
            sql = "INSERT INTO institucion (nombre_representante, razon_social, persona_id_persona) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos.get('nombre_representante'), datos.get('razon_social'), persona_id))

    def _sql_asegurar_prioridad(self, cursor) -> int:
        cursor.execute("SELECT id_gestion_prioridad FROM prioridad LIMIT 1")
        row = cursor.fetchone()
        if row: return row['id_gestion_prioridad'] if isinstance(row, dict) else row[0]
        
        sql = """INSERT INTO prioridad (rango_prioridad, fecha_asignacion, responsable_ajuste, justificacion_cambio)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (1.0, datetime.now(), 'Sistema', 'Default'))
        return cursor.lastrowid


    # --- MÉTODOS PÚBLICOS (API del Modelo) ---
    def guardar(self) -> int | bool:
        """Guarda la nueva solicitud usando los atributos instanciados."""
        if not self._tipo_solicitud or not self._problematica or not self._solicitante_data:
            return False

        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor(dictionary=True)

            persona_id = self._sql_buscar_persona(cursor, self._solicitante_data['cedula_persona'])
            if not persona_id:
                persona_id = self._sql_insertar_persona(cursor, self._solicitante_data)
                self._sql_insertar_subtipo(cursor, persona_id, self._solicitante_data)

            if not persona_id: return False

            prioridad_id = self._sql_asegurar_prioridad(cursor)
            
            sql_solicitud = """
                INSERT INTO solicitudes (fecha, tipo_solicitud, estatus_solicitud, problematica, 
                                         persona_id_persona, prioridad_id_gestion_prioridad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_solicitud, (
                self._fecha, self._tipo_solicitud, self._estatus_solicitud, 
                self._problematica, persona_id, prioridad_id
            ))
            
            self._id_solicitudes = cursor.lastrowid
            conn.commit()
            return self._id_solicitudes
        except Exception as e:
            print(f"Error guardar: {e}")
            if conn: conn.rollback()
            return False
        finally:
            self._cerrar(conn, cursor)

    def actualizar(self) -> bool:
        """Actualiza la solicitud actual (solo estatus y problemática)."""
        if not self._id_solicitudes:
            return False
            
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "UPDATE solicitudes SET estatus_solicitud = %s, problematica = %s WHERE id_solicitudes = %s"
            cursor.execute(sql, (self._estatus_solicitud, self._problematica, self._id_solicitudes))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            if conn: conn.rollback()
            return False
        finally:
            self._cerrar(conn, cursor)

    def eliminar(self) -> bool:
        """Elimina la solicitud actual de la BD."""
        if not self._id_solicitudes:
            return False
            
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "DELETE FROM solicitudes WHERE id_solicitudes = %s"
            cursor.execute(sql, (self._id_solicitudes,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            if conn: conn.rollback()
            return False
        finally:
            self._cerrar(conn, cursor)

    # --- MÉTODOS DE BÚSQUEDA ---
    @classmethod
    def obtener_todas(cls) -> list:
        conn = cursor = None
        try:
            conn = cls._con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT s.id_solicitudes AS id_solicitud, s.fecha, s.tipo_solicitud, s.estatus_solicitud,
                       s.problematica, p.cedula_persona, p.direccion AS direccion_solicitante, p.telefono AS telefono_solicitante, p.correo,
                       p.municipio, p.parroquia,
                       COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) as nombre_solicitante
                FROM solicitudes s
                LEFT JOIN persona p ON s.persona_id_persona = p.id_persona
                LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                ORDER BY s.fecha DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # Instanciar temporalmente para formatear la fecha
            instancia_temp = cls()
            for row in rows: 
                row['fecha_formateada'] = instancia_temp._formatear_fecha(row.get('fecha'))
            return rows
        except Exception as e:
            print(f"Error obtener_todas: {e}")
            return []
        finally:
            cls._cerrar(conn, cursor)

    @classmethod
    def buscar_por_id(cls, id_solicitud: int):
        conn = cursor = None
        try:
            conn = cls._con()
            if not conn: return None
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT s.id_solicitudes AS id_solicitud, s.*, p.cedula_persona, p.direccion AS direccion_solicitante, p.telefono AS telefono_solicitante, p.correo,
                       p.municipio, p.parroquia, com.ambito, com.sector,
                       COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) as nombre_solicitante,
                       COALESCE(part.nombre, '') as part_nombre, COALESCE(part.apellido, '') as part_apellido
                FROM solicitudes s
                LEFT JOIN persona p ON s.persona_id_persona = p.id_persona
                LEFT JOIN particular part ON p.id_persona = part.persona_id_persona
                LEFT JOIN institucion inst ON p.id_persona = inst.persona_id_persona
                LEFT JOIN comunidad com ON p.id_persona = com.persona_id_persona
                WHERE s.id_solicitudes = %s
            """
            cursor.execute(sql, (id_solicitud,))
            row = cursor.fetchone()
            if row: 
                row['fecha_formateada'] = cls()._formatear_fecha(row.get('fecha'))
            return row
        except Exception as e:
            print(f"Error buscar_por_id: {e}")
            return None
        finally:
            cls._cerrar(conn, cursor)

    @classmethod
    def obtener_estadisticas(cls) -> dict:
        conn = cursor = None
        try:
            conn = cls._con()
            if not conn: return {}
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT estatus_solicitud, COUNT(*) as total FROM solicitudes GROUP BY estatus_solicitud"
            cursor.execute(sql)
            return {r['estatus_solicitud']: r['total'] for r in cursor.fetchall()}
        except Exception: return {}
        finally: cls._cerrar(conn, cursor)