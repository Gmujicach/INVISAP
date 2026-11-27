"""
SolicitudModel — Modelo SOLID/DRY para gestión de solicitudes.
Refactorizado con encapsulamiento, getters/setters y validaciones Regex.
"""
import re
from datetime import datetime
from models.base_model import BaseModel


class SolicitudModel(BaseModel):
    """Repositorio y entidad de solicitudes."""

    __RE_CEDULA = re.compile(r'^\d{7,10}$')
    __RE_TELEFONO = re.compile(r'^(0414|0424|0412|0416|0426|0251)-?\d{7}$')
    __RE_CORREO = re.compile(r'^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$')
    __RE_TEXTO = re.compile(r'^[\w\s\.,\-áéíóúÁÉÍÓÚñÑ]{2,100}$', re.UNICODE)
    __RE_PROBLEMATICA = re.compile(r'^[\w\s\.,\!\?\-áéíóúÁÉÍÓÚñÑ]{15,500}$', re.UNICODE)

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

    # Límite de caracteres de la columna `solicitudes.problematica`, contando
    # el prefijo "[Categoría] " que se antepone al texto del solicitante.
    LIMITE_PROBLEMATICA = 512
    __columna_problematica_verificada = False

    def __init__(self, id_solicitudes=None):
        self.__id_solicitudes = id_solicitudes
        self.__tipo_solicitud = None
        self.__estatus_solicitud = 'Pendiente'
        self.__problematica = None
        self.__fecha = None
        self.__solicitante_data = {} # Almacena datos del solicitante

    # --- GETTERS Y SETTERS CON VALIDACIÓN (ENCAPSULAMIENTO) ---
    def get_id(self):
        return self.__id_solicitudes

    def get_tipo_solicitud(self):
        return self.__tipo_solicitud

    def set_tipo_solicitud(self, valor):
        valor = str(valor or '').strip()
        if valor not in self.TIPOS_SOLICITANTE_VALIDOS:
            raise ValueError(f"Tipo de solicitud '{valor}' inválido.")
        self.__tipo_solicitud = valor

    def get_estatus_solicitud(self):
        return self.__estatus_solicitud

    def set_estatus_solicitud(self, valor):
        valor = self.__limpiar(valor, 20)
        if valor not in self.ESTATUS_VALIDOS:
            valor = 'Pendiente'
        self.__estatus_solicitud = valor

    def get_problematica(self):
        return self.__problematica

    def set_problematica(self, valor, tipo_problematica=None):
        tipo_prob = self.__limpiar(tipo_problematica, 50) if tipo_problematica else ""

        if tipo_prob and tipo_prob not in self.TIPOS_PROBLEMATICA_VALIDOS:
            raise ValueError(f"Categoría de problemática '{tipo_prob}' inválida.")

        prefijo = f"[{tipo_prob}] " if tipo_prob else ""
        # El texto libre se recorta para que prefijo + descripción nunca
        # superen el tamaño real de la columna en la base de datos.
        limite_texto = max(15, self.LIMITE_PROBLEMATICA - len(prefijo))
        problematica_libre = self.__limpiar(valor, limite_texto)

        if not problematica_libre and not tipo_prob:
            raise ValueError("Debe describir la problemática de la solicitud.")

        problematica_final = f"{prefijo}{problematica_libre}".strip()

        if not self.__RE_PROBLEMATICA.match(problematica_final) and len(problematica_final.strip()) < 15:
            raise ValueError("La problemática debe tener al menos 15 caracteres válidos y evitar inyecciones.")
        self.__problematica = problematica_final[:self.LIMITE_PROBLEMATICA]

    def get_fecha(self):
        return self.__fecha

    def set_fecha(self, valor=None):
        fecha_raw = str(valor or '').strip()
        self.__fecha = fecha_raw.replace('T', ' ') if fecha_raw else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def set_solicitante_data(self, datos: dict):
        """Asigna y valida los datos del solicitante dependiendo del tipo."""
        tipo = self.__tipo_solicitud
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

        if not self.__RE_CEDULA.match(str(cedula)):
            raise ValueError("Cédula inválida. Debe tener entre 7 y 10 dígitos numéricos sin puntos ni guiones.")
            
        if not self.__RE_CORREO.match(correo):
            raise ValueError("Formato de correo electrónico inválido.")
            
        if not self.__RE_TELEFONO.match(telefono):
            raise ValueError("Formato de teléfono inválido (ej: 04121234567 o 0412-1234567).")
            
        municipio = self.__limpiar(municipio, 45)
        if municipio and municipio not in self.MUNICIPIOS_VALIDOS:
            raise ValueError(f"El municipio '{municipio}' no es válido.")
            
        parroquia = self.__limpiar(parroquia, 45)
        if not parroquia:
            raise ValueError("Debe seleccionar una parroquia válida.")

        self.__solicitante_data = {
            'tipo_solicitante': tipo,
            'cedula_persona': self.__limpiar(cedula, 10),
            'direccion': self.__limpiar(direccion, 200),
            'parroquia': parroquia,
            'municipio': municipio,
            'telefono': self.__limpiar(telefono, 12),
            'correo': self.__limpiar(correo, 45)
        }

        # Campos específicos por tipo
        if tipo == 'Comunidad':
            self.__solicitante_data['nombre_comunidad'] = self.__limpiar(datos.get('com_nombre', ''), 100)
            self.__solicitante_data['ambito'] = self.__limpiar(datos.get('com_ambito', ''), 45)
            self.__solicitante_data['sector'] = self.__limpiar(datos.get('com_sector', ''), 45)
        elif tipo == 'Institucion':
            self.__solicitante_data['nombre_representante'] = self.__limpiar(datos.get('inst_director_nombre', ''), 45)
            self.__solicitante_data['razon_social'] = self.__limpiar(datos.get('inst_nombre', ''), 120)
        elif tipo == 'Particular':
            self.__solicitante_data['nombre'] = self.__limpiar(datos.get('part_nombre', ''), 45)
            self.__solicitante_data['apellido'] = self.__limpiar(datos.get('part_apellido', ''), 45)


    # --- MÉTODOS PRIVADOS (Base de Datos) ---
    @staticmethod
    def __con():
        return SolicitudModel.obtener_conexion()

    @staticmethod
    def __cerrar(conn, cursor):
        try:
            if cursor: cursor.close()
        except Exception: pass
        try:
            if conn: conn.close()
        except Exception: pass

    @staticmethod
    def __limpiar(valor: str, max_len: int = 255) -> str:
        if not isinstance(valor, str):
            valor = str(valor or '')
        return re.sub(r'[<>\'";\\]', '', valor).strip()[:max_len]

    def __formatear_fecha(self, fecha):
        if fecha is None: return ''
        if isinstance(fecha, datetime): return fecha.strftime('%a %d-%m-%Y %I:%M:%S %p')
        if isinstance(fecha, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f'):
                try: return datetime.strptime(fecha, fmt).strftime('%a %d-%m-%Y %I:%M:%S %p')
                except ValueError: continue
            return fecha
        return str(fecha)

    def __sql_buscar_persona(self, cursor, cedula: str):
        sql = "SELECT id_persona FROM persona WHERE cedula_persona = %s LIMIT 1"
        cursor.execute(sql, (cedula,))
        row = cursor.fetchone()
        return row['id_persona'] if isinstance(row, dict) else (row[0] if row else None)

    def __sql_insertar_persona(self, cursor, datos: dict) -> int:
        for _ in range(3):
            cursor.execute("SELECT COALESCE(MAX(id_persona), 0) + 1 AS siguiente_id FROM persona")
            fila = cursor.fetchone()
            siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)

            sql = """
                INSERT INTO persona (id_persona, cedula_persona, direccion, parroquia, municipio, telefono, correo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cedula = int(''.join(filter(str.isdigit, str(datos['cedula_persona']))) or 0)
            try:
                cursor.execute(sql, (
                    siguiente_id, cedula, datos['direccion'], datos['parroquia'],
                    datos['municipio'], datos['telefono'], datos['correo']
                ))
                return siguiente_id
            except Exception as e:
                error_code = getattr(e, 'errno', None)
                if error_code is None and e.args:
                    error_code = e.args[0]
                if error_code != 1062:
                    raise
                if hasattr(cursor, 'connection') and cursor.connection:
                    cursor.connection.rollback()

        raise ValueError("No se pudo reservar un ID único para persona tras 3 intentos")

    def __sql_insertar_subtipo(self, cursor, persona_id: int, datos: dict):
        tipo = datos['tipo_solicitante']
        if tipo == 'Particular':
            for _ in range(3):
                cursor.execute("SELECT COALESCE(MAX(id_particular), 0) + 1 AS siguiente_id FROM particular")
                fila = cursor.fetchone()
                siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)
                sql = "INSERT INTO particular (id_particular, nombre, apellido, persona_id_persona) VALUES (%s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (siguiente_id, datos.get('nombre'), datos.get('apellido'), persona_id))
                    return
                except Exception as e:
                    error_code = getattr(e, 'errno', None)
                    if error_code is None and e.args:
                        error_code = e.args[0]
                    if error_code != 1062:
                        raise
                    if hasattr(cursor, 'connection') and cursor.connection:
                        cursor.connection.rollback()
            raise ValueError("No se pudo reservar un ID único para particular tras 3 intentos")
        elif tipo == 'Comunidad':
            for _ in range(3):
                cursor.execute("SELECT COALESCE(MAX(id_comunidad), 0) + 1 AS siguiente_id FROM comunidad")
                fila = cursor.fetchone()
                siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)
                sql = "INSERT INTO comunidad (id_comunidad, nombre_comunidad, ambito, sector, persona_id_persona) VALUES (%s, %s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (siguiente_id, datos.get('nombre_comunidad'), datos.get('ambito'), datos.get('sector'), persona_id))
                    return
                except Exception as e:
                    error_code = getattr(e, 'errno', None)
                    if error_code is None and e.args:
                        error_code = e.args[0]
                    if error_code != 1062:
                        raise
                    if hasattr(cursor, 'connection') and cursor.connection:
                        cursor.connection.rollback()
            raise ValueError("No se pudo reservar un ID único para comunidad tras 3 intentos")
        elif tipo == 'Institucion':
            for _ in range(3):
                cursor.execute("SELECT COALESCE(MAX(id_institucion), 0) + 1 AS siguiente_id FROM institucion")
                fila = cursor.fetchone()
                siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)
                sql = "INSERT INTO institucion (id_institucion, nombre_representante, razon_social, persona_id_persona) VALUES (%s, %s, %s, %s)"
                try:
                    cursor.execute(sql, (siguiente_id, datos.get('nombre_representante'), datos.get('razon_social'), persona_id))
                    return
                except Exception as e:
                    error_code = getattr(e, 'errno', None)
                    if error_code is None and e.args:
                        error_code = e.args[0]
                    if error_code != 1062:
                        raise
                    if hasattr(cursor, 'connection') and cursor.connection:
                        cursor.connection.rollback()
            raise ValueError("No se pudo reservar un ID único para institucion tras 3 intentos")

    def __sql_crear_prioridad_pendiente(self, cursor) -> int:
        cursor.execute(
            """INSERT INTO prioridad
               (rango_prioridad, origen, fecha_asignacion, responsable_ajuste,
                justificacion_cambio, estado)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (1.0, 'pendiente', self.__fecha, 'Sistema', 'Pendiente de clasificación IA', 0),
        )
        return cursor.lastrowid

    @staticmethod
    def __asegurar_columna_problematica(conn):
        """Amplía `solicitudes.problematica` si el esquema es menor que el límite del modelo.

        Evita el error MySQL 1406 (Data too long) cuando el prefijo de categoría
        y la descripción supera el VARCHAR definido en instalaciones antiguas.
        """
        if SolicitudModel.__columna_problematica_verificada:
            return
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW COLUMNS FROM solicitudes LIKE 'problematica'")
            columna = cursor.fetchone()
            if isinstance(columna, dict):
                tipo = str(columna.get('Type') or columna.get('type') or '').lower()
            elif columna:
                tipo = str(columna[1]).lower()
            else:
                tipo = ''
            if tipo:
                match = re.search(r'\((\d+)\)', tipo)
                longitud = int(match.group(1)) if match else 0
                if not tipo.startswith('text') and longitud < SolicitudModel.LIMITE_PROBLEMATICA:
                    cursor.execute(
                        f"ALTER TABLE solicitudes MODIFY COLUMN problematica "
                        f"VARCHAR({SolicitudModel.LIMITE_PROBLEMATICA}) NOT NULL"
                    )
                    conn.commit()
                    print(f"[SolicitudModel] Columna solicitudes.problematica ampliada a VARCHAR({SolicitudModel.LIMITE_PROBLEMATICA}).")
            SolicitudModel.__columna_problematica_verificada = True
        except Exception as e:
            print(f"[SolicitudModel] No se pudo verificar solicitudes.problematica: {e}")
        finally:
            if cursor:
                cursor.close()

    # --- MÉTODOS PÚBLICOS (API del Modelo) ---
    def guardar(self) -> int | bool:
        """Guarda la nueva solicitud usando los atributos instanciados."""
        if not self.__tipo_solicitud or not self.__problematica or not self.__solicitante_data:
            return False

        conn = cursor = None
        try:
            conn = self.__con()
            if not conn: return False
            self.__asegurar_columna_problematica(conn)
            cursor = conn.cursor(dictionary=True)

            persona_id = self.__sql_buscar_persona(cursor, self.__solicitante_data['cedula_persona'])
            if not persona_id:
                persona_id = self.__sql_insertar_persona(cursor, self.__solicitante_data)
                self.__sql_insertar_subtipo(cursor, persona_id, self.__solicitante_data)

            if not persona_id: return False

            prioridad_id = self.__sql_crear_prioridad_pendiente(cursor)

            sql_solicitud = """
                INSERT INTO solicitudes (fecha, tipo_solicitud, estatus_solicitud, problematica,
                                         persona_id_persona, prioridad_id_gestion_prioridad)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_solicitud, (
                self.__fecha, self.__tipo_solicitud, self.__estatus_solicitud,
                self.__problematica, persona_id, prioridad_id
            ))

            self.__id_solicitudes = cursor.lastrowid
            conn.commit()
            return self.__id_solicitudes
        except Exception as e:
            print(f"Error guardar: {e}")
            if conn: conn.rollback()
            return False
        finally:
            self.__cerrar(conn, cursor)

    def actualizar(self) -> bool:
        """Actualiza la solicitud actual (solo estatus y problemática)."""
        if not self.__id_solicitudes:
            return False
            
        conn = cursor = None
        try:
            conn = self.__con()
            if not conn: return False
            self.__asegurar_columna_problematica(conn)
            cursor = conn.cursor()
            sql = "UPDATE solicitudes SET estatus_solicitud = %s, problematica = %s WHERE id_solicitudes = %s"
            cursor.execute(sql, (self.__estatus_solicitud, self.__problematica, self.__id_solicitudes))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error actualizar: {e}")
            if conn: conn.rollback()
            return False
        finally:
            self.__cerrar(conn, cursor)

    @classmethod
    def actualizar_estatus(cls, id_solicitud: int, nuevo_estatus: str) -> bool:
        """Actualiza el estatus de una solicitud específica."""
        conn = cursor = None
        try:
            conn = cls.__con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "UPDATE solicitudes SET estatus_solicitud = %s WHERE id_solicitudes = %s"
            cursor.execute(sql, (nuevo_estatus, id_solicitud))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error actualizar_estatus: {e}")
            if conn: conn.rollback()
            return False
        finally:
            cls.__cerrar(conn, cursor)

    def eliminar(self) -> bool:
        """Elimina la solicitud actual de la BD."""
        if not self.__id_solicitudes:
            return False
            
        conn = cursor = None
        try:
            conn = self.__con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "DELETE FROM solicitudes WHERE id_solicitudes = %s"
            cursor.execute(sql, (self.__id_solicitudes,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            if conn: conn.rollback()
            return False
        finally:
            self.__cerrar(conn, cursor)

    # --- MÉTODOS DE BÚSQUEDA ---
    @classmethod
    def obtener_todas(cls) -> list:
        conn = cursor = None
        try:
            conn = cls.__con()
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
                row['fecha_formateada'] = instancia_temp.__formatear_fecha(row.get('fecha'))
            return rows
        except Exception as e:
            print(f"Error obtener_todas: {e}")
            return []
        finally:
            cls.__cerrar(conn, cursor)

    @classmethod
    def buscar_por_id(cls, id_solicitud: int):
        conn = cursor = None
        try:
            conn = cls.__con()
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
                row['fecha_formateada'] = cls().__formatear_fecha(row.get('fecha'))
            return row
        except Exception as e:
            print(f"Error buscar_por_id: {e}")
            return None
        finally:
            cls.__cerrar(conn, cursor)

    @classmethod
    def obtener_estadisticas(cls) -> dict:
        conn = cursor = None
        try:
            conn = cls.__con()
            if not conn: return {}
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT estatus_solicitud, COUNT(*) as total FROM solicitudes GROUP BY estatus_solicitud"
            cursor.execute(sql)
            return {r['estatus_solicitud']: r['total'] for r in cursor.fetchall()}
        except Exception: return {}
        finally: cls.__cerrar(conn, cursor)

    @classmethod
    def obtener_estadisticas_por_tipo(cls) -> dict:
        conn = cursor = None
        try:
            conn = cls.__con()
            if not conn: return {}
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT tipo_solicitud, COUNT(*) as total FROM solicitudes GROUP BY tipo_solicitud"
            cursor.execute(sql)
            return {r['tipo_solicitud']: r['total'] for r in cursor.fetchall()}
        except Exception: return {}
        finally: cls.__cerrar(conn, cursor)

    @classmethod
    def obtener_estadisticas_por_parroquia(cls) -> list:
        conn = cursor = None
        try:
            conn = cls.__con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT p.parroquia, COUNT(s.id_solicitudes) as total
                FROM solicitudes s
                JOIN persona p ON s.persona_id_persona = p.id_persona
                GROUP BY p.parroquia
                ORDER BY total DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception: return []
        finally: cls.__cerrar(conn, cursor)

    @classmethod
    def obtener_solicitudes_priorizadas(cls, limite=10) -> list:
        conn = cursor = None
        try:
            conn = cls.__con()
            if not conn: return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    s.id_solicitudes,
                    DATE_FORMAT(s.fecha, '%d/%m/%Y %H:%i') as fecha,
                    s.tipo_solicitud,
                    s.estatus_solicitud,
                    s.problematica,
                    p.parroquia,
                    p.municipio,
                    pr.rango_prioridad as prioridad
                FROM solicitudes s
                JOIN persona p ON s.persona_id_persona = p.id_persona
                JOIN prioridad pr ON s.prioridad_id_gestion_prioridad = pr.id_gestion_prioridad
                WHERE s.estatus_solicitud IN ('Pendiente', 'En Proceso')
                  AND s.estado = 1
                  AND pr.estado = 1
                ORDER BY pr.rango_prioridad ASC, s.fecha DESC
                LIMIT %s
            """
            cursor.execute(sql, (limite,))
            rows = cursor.fetchall()
            instancia = cls()
            for row in rows:
                row['fecha_formateada'] = instancia.__formatear_fecha(row.get('fecha'))
            return rows
        except Exception: return []
        finally: cls.__cerrar(conn, cursor)

    @classmethod
    def obtener_solicitudes_pendientes(cls) -> list:
        conn = cursor = None
        try:
            conn = cls.__con()
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
                WHERE s.estatus_solicitud = 'Pendiente'
                ORDER BY s.fecha DESC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            instancia_temp = cls()
            for row in rows:
                row['fecha_formateada'] = instancia_temp.__formatear_fecha(row.get('fecha'))
            return rows
        except Exception as e:
            print(f"Error obtener_solicitudes_pendientes: {e}")
            return []
        finally:
            cls.__cerrar(conn, cursor)