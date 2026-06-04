from conexion.conexionBD import connectionBD


# CREATE: Inserción de un nuevo solicitante
def crear_solicitante(datos):
    try:
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = """INSERT INTO solicitante (nombre_solicitante, parroquia, municipio, ambito, rif, cedula, correo) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""

            rif_completo = f"{datos.get('tipo_rif','')}-{datos.get('numero_rif','')}"

            valores = (datos.get('nombre_solicitante'), datos.get('parroquia'), datos.get('municipio'),
                       datos.get('ambito'), rif_completo, datos.get('cedula'), datos.get('correo'))

            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al crear solicitante: {e}")
        return 0


# READ: Obtener todos los registros para la vista de listado
def obtener_solicitantes():
    try:
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM solicitante ORDER BY id_comunidad DESC"
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al obtener solicitantes: {e}")
        return []


# READ: Obtener un solicitante por id
def obtener_solicitante_por_id(id_comunidad):
    try:
        conexion = connectionBD()
        cursor = conexion.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM solicitante WHERE id_comunidad = %s"
            cursor.execute(sql, (id_comunidad,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al obtener solicitante por id: {e}")
        return None


# UPDATE: Modificar información de un solicitante existente
def actualizar_solicitante(datos):
    try:
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = """UPDATE solicitante SET nombre_solicitante = %s, parroquia = %s, 
                     municipio = %s, ambito = %s, rif = %s, cedula = %s, correo = %s 
                     WHERE id_comunidad = %s"""

            rif_completo = f"{datos.get('tipo_rif','')}-{datos.get('numero_rif','')}"

            valores = (datos.get('nombre_solicitante'), datos.get('parroquia'), datos.get('municipio'),
                       datos.get('ambito'), rif_completo, datos.get('cedula'), datos.get('correo'), datos.get('id_comunidad'))
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return 0


# DELETE: Eliminar un registro
def eliminar_solicitante(id_comunidad):
    try:
        conexion = connectionBD()
        cursor = conexion.cursor()
        try:
            sql = "DELETE FROM solicitante WHERE id_comunidad = %s"
            cursor.execute(sql, (id_comunidad,))
            conexion.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conexion.close()
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return 0