from datetime import datetime
from conexion.conexionBD import connectionBD_invilara

class SolicitudModel:
    def __init__(self):
        # No mantenemos una conexión persistente; abrimos por operación
        pass

    def _parse_solicitante_data(self, datos):
        tipo_solicitante = datos.get('tipo_solicitud', '').strip()
        
        if tipo_solicitante == 'Comunidad':
            nombre = datos.get('com_nombre', '').strip()
            rif = f"{datos.get('com_rif_letra', '').strip()}-{datos.get('com_rif_numero', '').strip()}"
            parroquia = datos.get('com_parroquia', '').strip()
            municipio = datos.get('com_municipio', '').strip()
            ambito = datos.get('com_ambito', '').strip()
            cedula = datos.get('com_cedula', '').strip()
            correo = datos.get('com_correo', '').strip()
            
        elif tipo_solicitante == 'Institucion':
            nombre = datos.get('inst_nombre', '').strip()
            # CORRECCIÓN: Armamos un RIF válido basado en la cédula del director, no en el teléfono
            rif = f"G-{datos.get('inst_rif_numero', '').strip()}"
            # CORRECCIÓN: Enviamos 'No aplica' para evitar errores de campos vacíos en MySQL
            parroquia = 'No aplica'
            municipio = 'No aplica'
            ambito = datos.get('inst_direccion', '').strip()
            cedula = datos.get('inst_director_cedula', '').strip()
            correo = datos.get('inst_correo', '').strip()
            
        elif tipo_solicitante == 'Particular':
            nombre = datos.get('part_nombre', '').strip()
            rif = f"V-{datos.get('part_cedula', '').strip()}"
            parroquia = datos.get('part_parroquia', '').strip() 
            municipio = datos.get('part_municipio', '').strip()
            ambito = datos.get('part_direccion', '').strip()
            cedula = datos.get('part_cedula', '').strip()
            correo = datos.get('part_correo', '').strip()
            
        else:
            nombre = datos.get('nombre_solicitante', '').strip()
            rif = datos.get('rif', '').strip()
            parroquia = datos.get('parroquia', '').strip()
            municipio = datos.get('municipio', '').strip()
            ambito = datos.get('ambito', '').strip()
            cedula = datos.get('cedula', '').strip()
            correo = datos.get('correo', '').strip()

        return {
            'nombre_solicitante': nombre,
            'parroquia': parroquia,
            'municipio': municipio,
            'ambito': ambito,
            'rif': rif,
            'cedula': cedula,
            'correo': correo,
            'tipo_solicitante': tipo_solicitante
        }

    def _parse_solicitud_data(self, datos):
        fecha_raw = datos.get('fecha', '').strip()
        fecha = fecha_raw.replace('T', ' ') if fecha_raw else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        telefono = datos.get('com_telefono', '').strip() or datos.get('inst_telefono', '').strip() or datos.get('part_telefono', '').strip()
        
        # CORRECCIÓN: Para comunidad, la dirección debe ser "com_ambito" (la dirección específica), no el municipio
        direccion = datos.get('part_direccion', '').strip() or datos.get('inst_direccion', '').strip() or datos.get('com_ambito', '').strip()
        
        estatus = datos.get('estatus_solicitud', datos.get('estatus', 'PENDIENTE')).strip()
        if not estatus:
            estatus = 'PENDIENTE'

        return {
            'fecha': fecha,
            'telefono_solicitante': telefono,
            'direccion_solicitante': direccion,
            'tipo_solicitud': datos.get('tipo_solicitud', '').strip(),
            'estatus_solicitud': estatus,
            'problematica': datos.get('problematica', '').strip(),
            'tipo_solicitante': datos.get('tipo_solicitud', '').strip()
        }

    def _get_or_create_solicitante(self, cursor, solicitante_data):
        if not solicitante_data['rif'] and not solicitante_data['cedula']:
            return None

        search_sql = "SELECT id_solicitante FROM solicitante WHERE rif = %s OR cedula = %s LIMIT 1"
        cursor.execute(search_sql, (solicitante_data['rif'], solicitante_data['cedula']))
        result = cursor.fetchone()
        
        if result:
            return result['id_solicitante'] if isinstance(result, dict) else result[0]

        insert_sql = """INSERT INTO solicitante \
            (nombre_solicitante, parroquia, municipio, ambito, rif, cedula, correo)\
            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(insert_sql, (
            solicitante_data['nombre_solicitante'],
            solicitante_data['parroquia'],
            solicitante_data['municipio'],
            solicitante_data['ambito'],
            solicitante_data['rif'],
            solicitante_data['cedula'],
            solicitante_data['correo']
        ))
        return cursor.lastrowid

    def obtener_todas_las_solicitudes(self):
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            if conexion is None:
                return []
            cursor = conexion.cursor(dictionary=True)
            sql = """
            SELECT gs.*, s.nombre_solicitante, s.rif, s.cedula, s.correo
            FROM gestionar_solicitudes gs
            LEFT JOIN solicitante s ON gs.solicitante_id_comunidad = s.id_solicitante
            ORDER BY gs.id_solicitud DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener solicitudes: {e}")
            return []
        finally:
            if cursor is not None: cursor.close()
            if conexion is not None:
                try: conexion.close()
                except Exception: pass

    def obtener_solicitud_por_id(self, id_solicitud):
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            if conexion is None:
                return None
            cursor = conexion.cursor(dictionary=True)
            sql = """
            SELECT gs.*, s.*
            FROM gestionar_solicitudes gs
            LEFT JOIN solicitante s ON gs.solicitante_id_comunidad = s.id_solicitante
            WHERE gs.id_solicitud = %s
            """
            cursor.execute(sql, (id_solicitud,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener solicitud por id: {e}")
            return None
        finally:
            if cursor is not None: cursor.close()
            if conexion is not None:
                try: conexion.close()
                except Exception: pass

    def crear_nueva_solicitud(self, datos):
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            if conexion is None:
                return False
            cursor = conexion.cursor(dictionary=True)

            solicitante_data = self._parse_solicitante_data(datos)
            solicitud_data = self._parse_solicitud_data(datos)

            if not solicitud_data['tipo_solicitud'] or not solicitud_data['estatus_solicitud'] or not solicitud_data['problematica']:
                print("Faltan datos obligatorios de la solicitud")
                return False

            solicitante_id = self._get_or_create_solicitante(cursor, solicitante_data)
            if not solicitante_id:
                print("No se pudo crear o encontrar el solicitante")
                return False

            insert_sql = """INSERT INTO gestionar_solicitudes \
                (fecha, telefono_solicitante, direccion_solicitante, tipo_solicitud, estatus_solicitud, problematica, tipo_solicitante, solicitante_id_comunidad)\
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(insert_sql, (
                solicitud_data['fecha'],
                solicitud_data['telefono_solicitante'],
                solicitud_data['direccion_solicitante'],
                solicitud_data['tipo_solicitud'],
                solicitud_data['estatus_solicitud'], # Inyectamos la variable dinámica, no el string quemado
                solicitud_data['problematica'],
                solicitud_data['tipo_solicitante'],
                solicitante_id
            ))
            conexion.commit()
            return True
        except Exception as e:
            if conexion is not None:
                try: conexion.rollback()
                except Exception: pass
            print(f"Error al crear la solicitud: {e}")
            return False
        finally:
            if cursor is not None: cursor.close()
            if conexion is not None:
                try: conexion.close()
                except Exception: pass

    # SOLUCIÓN 3: Bloque añadido. Métodos necesarios para Modificar y Eliminar en MySQL
    def actualizar_solicitud(self, id_solicitud, datos):
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            
            estatus = datos.get('estatus_solicitud', '').strip()
            problematica = datos.get('problematica', '').strip()
            
            sql = """UPDATE gestionar_solicitudes 
                     SET estatus_solicitud = %s, problematica = %s 
                     WHERE id_solicitud = %s"""
            cursor.execute(sql, (estatus, problematica, id_solicitud))
            conexion.commit()
            
            return True
        except Exception as e:
            print(f"Error al actualizar la solicitud: {e}")
            return False
        finally:
            if cursor is not None: cursor.close()
            if conexion is not None:
                try: conexion.close()
                except Exception: pass

    def eliminar_solicitud(self, id_solicitud):
        conexion = None
        cursor = None
        try:
            conexion = connectionBD_invilara()
            if conexion is None:
                return False
            cursor = conexion.cursor()
            
            sql = "DELETE FROM gestionar_solicitudes WHERE id_solicitud = %s"
            cursor.execute(sql, (id_solicitud,))
            conexion.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar la solicitud: {e}")
            return False
        finally:
            if cursor is not None: cursor.close()
            if conexion is not None:
                try: conexion.close()
                except Exception: pass