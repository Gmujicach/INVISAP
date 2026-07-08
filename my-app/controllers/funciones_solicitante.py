from conexion.conexionBD import connectionBD_invilara as connectionBD
from services.bitacora_service import BitacoraService
from flask import session

def crear_solicitante(datos):
    try:
        conexion = connectionBD()
        if not conexion: return 0
        cursor = conexion.cursor()
        try:
            sql = """INSERT INTO persona (cedula_persona, direccion, parroquia, municipio, telefono, correo) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""

            valores = (datos.get('cedula_persona'), datos.get('direccion'), datos.get('parroquia'), 
                       datos.get('municipio'), datos.get('telefono'), datos.get('correo'))

            cursor.execute(sql, valores)
            conexion.commit()
            if cursor.rowcount:
                BitacoraService.registrar_accion(
                    session, 'Gerencias', 'CREAR',
                    f'Registró un solicitante con cédula: {datos.get("cedula_persona")}'
                )
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al crear solicitante: {e}")
        return 0

def obtener_solicitantes():
    try:
        conexion = connectionBD()
        if not conexion: return []
        cursor = conexion.cursor(dictionary=True)
        try:
            sql = """
                SELECT p.*, COALESCE(CONCAT(pa.nombre, ' ', pa.apellido), i.razon_social, c.nombre_comunidad) AS nombre_solicitante
                FROM persona p
                LEFT JOIN particular pa ON p.id_persona = pa.persona_id_persona
                LEFT JOIN institucion i ON p.id_persona = i.persona_id_persona
                LEFT JOIN comunidad c ON p.id_persona = c.persona_id_persona
                ORDER BY p.id_persona DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al obtener solicitantes: {e}")
        return []

def obtener_solicitante_por_id(id_persona):
    try:
        conexion = connectionBD()
        if not conexion: return None
        cursor = conexion.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM persona WHERE id_persona = %s"
            cursor.execute(sql, (id_persona,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al obtener solicitante por id: {e}")
        return None

def actualizar_solicitante(datos):
    try:
        conexion = connectionBD()
        if not conexion: return 0
        cursor = conexion.cursor()
        try:
            sql = """UPDATE persona SET cedula_persona = %s, direccion = %s, parroquia = %s, 
                     municipio = %s, telefono = %s, correo = %s 
                     WHERE id_persona = %s"""

            valores = (datos.get('cedula_persona'), datos.get('direccion'), datos.get('parroquia'), 
                       datos.get('municipio'), datos.get('telefono'), datos.get('correo'), datos.get('id_persona'))
            cursor.execute(sql, valores)
            conexion.commit()
            if cursor.rowcount:
                BitacoraService.registrar_accion(
                    session, 'Gerencias', 'EDITAR',
                    f'Actualizó el solicitante ID: {datos.get("id_persona")}'
                )
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return 0

def eliminar_solicitante(id_persona):
    try:
        conexion = connectionBD()
        if not conexion: return 0
        cursor = conexion.cursor()
        try:
            sql = "DELETE FROM persona WHERE id_persona = %s"
            cursor.execute(sql, (id_persona,))
            conexion.commit()
            if cursor.rowcount:
                BitacoraService.registrar_accion(
                    session, 'Gerencias', 'ELIMINAR',
                    f'Eliminó el solicitante ID: {id_persona}'
                )
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return 0