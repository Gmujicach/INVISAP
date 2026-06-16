"""
SolicitudModel — Modelo SOLID/DRY para gestión de solicitudes.
Adaptado al esquema de BD Invilara (Junio 2026).
"""
import re
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara

class SolicitudModel:
    """Repositorio de solicitudes y solicitantes."""

    _RE_CEDULA = re.compile(r'^\d{7,10}$')
    _RE_TELEFONO = re.compile(r'^(0414|0424|0412|0416|0426|0251)-?\d{7}$')
    _RE_CORREO = re.compile(r'^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.,\-áéíóúÁÉÍÓÚñÑ]{2,100}$', re.UNICODE)
    _RE_PROBLEMATICA = re.compile(r'^[\w\s\.,\!\?\-áéíóúÁÉÍÓÚñÑ]{15,500}$', re.UNICODE)

    TIPOS_SOLICITANTE_VALIDOS = {'Comunidad', 'Institucion', 'Particular'}
    ESTATUS_VALIDOS = {'Pendiente', 'En Proceso', 'Completada', 'Procesada', 'PENDIENTE'}

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

    def _validar_problematica(self, texto: str) -> bool:
        return len(texto.strip()) >= 15

    def _parse_solicitante_data(self, datos: dict) -> dict:
        """Extrae y normaliza datos del solicitante mapeados a la BD."""
        tipo = datos.get('tipo_solicitud', '').strip()

        if tipo == 'Comunidad':
            return {
                'tipo_solicitante': tipo,
                'nombre_comunidad': self._limpiar(datos.get('com_nombre', ''), 100),
                'ambito': self._limpiar(datos.get('com_ambito', ''), 45),
                'sector': self._limpiar(datos.get('com_sector', ''), 45),
                'cedula_persona': self._limpiar(datos.get('com_cedula', ''), 10),
                'direccion': self._limpiar(datos.get('com_ambito', ''), 200),
                'parroquia': self._limpiar(datos.get('com_parroquia', ''), 45),
                'municipio': self._limpiar(datos.get('com_municipio', ''), 45),
                'telefono': self._limpiar(datos.get('com_telefono', ''), 12),
                'correo': self._limpiar(datos.get('com_correo', ''), 45)
            }
        elif tipo == 'Institucion':
            return {
                'tipo_solicitante': tipo,
                'nombre_representante': self._limpiar(datos.get('inst_director_nombre', ''), 45),
                'razon_social': self._limpiar(datos.get('inst_nombre', ''), 120),
                'cedula_persona': self._limpiar(datos.get('inst_director_cedula', ''), 10),
                'direccion': self._limpiar(datos.get('inst_direccion', ''), 200),
                'parroquia': self._limpiar(datos.get('inst_parroquia', ''), 45),
                'municipio': self._limpiar(datos.get('inst_municipio', ''), 45),
                'telefono': self._limpiar(datos.get('inst_telefono', ''), 12),
                'correo': self._limpiar(datos.get('inst_correo', ''), 45)
            }
        elif tipo == 'Particular':
            return {
                'tipo_solicitante': tipo,
                'nombre': self._limpiar(datos.get('part_nombre', ''), 45),
                'apellido': self._limpiar(datos.get('part_apellido', ''), 45),
                'cedula_persona': self._limpiar(datos.get('part_cedula', ''), 10),
                'direccion': self._limpiar(datos.get('part_direccion', ''), 200),
                'parroquia': self._limpiar(datos.get('part_parroquia', ''), 45),
                'municipio': self._limpiar(datos.get('part_municipio', ''), 45),
                'telefono': self._limpiar(datos.get('part_telefono', ''), 12),
                'correo': self._limpiar(datos.get('part_correo', ''), 45)
            }
        return {}

    def _parse_solicitud_data(self, datos: dict) -> dict:
        fecha_raw = datos.get('fecha', '').strip()
        fecha = fecha_raw.replace('T', ' ') if fecha_raw else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        estatus = self._limpiar(datos.get('estatus_solicitud', datos.get('estatus', 'Pendiente')), 15) or 'Pendiente'
        tipo_problematica = self._limpiar(datos.get('tipo_problematica', ''), 50)
        problematica_libre = self._limpiar(datos.get('problematica', ''), 500)

        problematica_final = problematica_libre
        if tipo_problematica and problematica_libre:
            problematica_final = f"[{tipo_problematica}] {problematica_libre}"
        elif tipo_problematica:
            problematica_final = tipo_problematica

        return {
            'fecha': fecha,
            'tipo_solicitud': self._limpiar(datos.get('tipo_solicitud', ''), 45),
            'estatus_solicitud': estatus,
            'problematica': problematica_final,
        }

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
            cursor.execute(sql, (datos['nombre'], datos['apellido'], persona_id))
        elif tipo == 'Comunidad':
            sql = "INSERT INTO comunidad (nombre_comunidad, ambito, sector, persona_id_persona) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (datos['nombre_comunidad'], datos['ambito'], datos['sector'], persona_id))
        elif tipo == 'Institucion':
            sql = "INSERT INTO institucion (nombre_representante, razon_social, persona_id_persona) VALUES (%s, %s, %s)"
            cursor.execute(sql, (datos['nombre_representante'], datos['razon_social'], persona_id))

    def _sql_asegurar_prioridad(self, cursor) -> int:
        cursor.execute("SELECT id_gestion_prioridad FROM prioridad LIMIT 1")
        row = cursor.fetchone()
        if row: return row['id_gestion_prioridad'] if isinstance(row, dict) else row[0]
        
        sql = """INSERT INTO prioridad (rango_prioridad, fecha_asignacion, responsable_ajuste, justificacion_cambio)
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (1.0, datetime.now(), 'Sistema', 'Default'))
        return cursor.lastrowid

    def _sql_insertar_solicitud(self, cursor, datos: dict, persona_id: int, prioridad_id: int) -> int:
        sql = """
            INSERT INTO solicitudes (fecha, tipo_solicitud, estatus_solicitud, problematica, 
                                     persona_id_persona, prioridad_id_gestion_prioridad)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            datos['fecha'], datos['tipo_solicitud'], datos['estatus_solicitud'], 
            datos['problematica'], persona_id, prioridad_id
        ))
        return cursor.lastrowid

    def _sql_todas_solicitudes(self) -> list:
        conn = cursor = None
        try:
            conn = self._con()
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
            for row in rows: row['fecha_formateada'] = self._formatear_fecha(row.get('fecha'))
            return rows
        except Exception as e:
            print(f"Error _sql_todas_solicitudes: {e}")
            return []
        finally:
            self._cerrar(conn, cursor)

    def _sql_solicitud_por_id(self, id_solicitud: int):
        conn = cursor = None
        try:
            conn = self._con()
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
            if row: row['fecha_formateada'] = self._formatear_fecha(row.get('fecha'))
            return row
        except Exception as e:
            print(f"Error _sql_solicitud_por_id: {e}")
            return None
        finally:
            self._cerrar(conn, cursor)

    def _sql_actualizar_solicitud(self, id_solicitud: int, estatus: str, problematica: str) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "UPDATE solicitudes SET estatus_solicitud = %s, problematica = %s WHERE id_solicitudes = %s"
            cursor.execute(sql, (estatus, problematica, id_solicitud))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            if conn: conn.rollback()
            return False
        finally:
            self._cerrar(conn, cursor)

    def _sql_eliminar_solicitud(self, id_solicitud: int) -> bool:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor()
            sql = "DELETE FROM solicitudes WHERE id_solicitudes = %s"
            cursor.execute(sql, (id_solicitud,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            if conn: conn.rollback()
            return False
        finally:
            self._cerrar(conn, cursor)

    def obtener_todas_las_solicitudes(self) -> list:
        return self._sql_todas_solicitudes()

    def obtener_solicitud_por_id(self, id_solicitud) -> dict | None:
        try: id_val = int(id_solicitud)
        except (ValueError, TypeError): return None
        return self._sql_solicitud_por_id(id_val) if id_val > 0 else None

    def crear_nueva_solicitud(self, datos: dict) -> int | bool:
        tipo = datos.get('tipo_solicitud', '').strip()
        if tipo not in self.TIPOS_SOLICITANTE_VALIDOS: return False
        if not self._validar_problematica(datos.get('problematica', '')): return False

        solicitante_data = self._parse_solicitante_data(datos)
        solicitud_data = self._parse_solicitud_data(datos)

        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return False
            cursor = conn.cursor(dictionary=True)

            persona_id = self._sql_buscar_persona(cursor, solicitante_data['cedula_persona'])
            if not persona_id:
                persona_id = self._sql_insertar_persona(cursor, solicitante_data)
                self._sql_insertar_subtipo(cursor, persona_id, solicitante_data)

            if not persona_id: return False

            prioridad_id = self._sql_asegurar_prioridad(cursor)
            nueva_id = self._sql_insertar_solicitud(cursor, solicitud_data, persona_id, prioridad_id)
            conn.commit()
            return nueva_id
        except Exception as e:
            print(f"Error crear_nueva_solicitud: {e}")
            if conn: conn.rollback()
            return False
        finally:
            self._cerrar(conn, cursor)

    def actualizar_solicitud(self, id_solicitud, datos: dict) -> bool:
        try: id_val = int(id_solicitud)
        except (ValueError, TypeError): return False
        estatus = self._limpiar(datos.get('estatus_solicitud', datos.get('estatus', '')), 20)
        if estatus not in self.ESTATUS_VALIDOS: estatus = 'Pendiente'
        problematica = self._limpiar(datos.get('problematica', ''), 500)
        if not self._validar_problematica(problematica): return False
        return self._sql_actualizar_solicitud(id_val, estatus, problematica)

    def eliminar_solicitud(self, id_solicitud) -> bool:
        try: id_val = int(id_solicitud)
        except (ValueError, TypeError): return False
        return self._sql_eliminar_solicitud(id_val) if id_val > 0 else False

    def obtener_estadisticas(self) -> dict:
        conn = cursor = None
        try:
            conn = self._con()
            if not conn: return {}
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT estatus_solicitud, COUNT(*) as total FROM solicitudes GROUP BY estatus_solicitud"
            cursor.execute(sql)
            return {r['estatus_solicitud']: r['total'] for r in cursor.fetchall()}
        except Exception: return {}
        finally: self._cerrar(conn, cursor)