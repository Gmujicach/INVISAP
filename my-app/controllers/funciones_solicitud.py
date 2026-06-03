from conexion.conexionBD import connectionBD

# CREATE: Inserción de un nuevo solicitante
def crear_solicitante(datos):
    try:
        # Usamos el context manager (with) para manejar de forma segura la apertura y cierre
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                sql = """INSERT INTO solicitante (nombre_solicitante, parroquia, municipio, ambito, rif, cedula, correo) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                
                # Procesamos la lógica para concatenar el tipo y el número de RIF antes de la inserción
                rif_completo = f"{datos['tipo_rif']}-{datos['numero_rif']}"
                
                valores = (datos['nombre_solicitante'], datos['parroquia'], datos['municipio'], 
                           datos['ambito'], rif_completo, datos['cedula'], datos['correo'])
                
                cursor.execute(sql, valores)
                conexion.commit() # Confirmación de la transacción en MySQL
                return cursor.rowcount
    except Exception as e:
        print(f"Error al crear solicitante: {e}")
        return 0

# READ: Obtener todos los registros para la vista de listado
def obtener_solicitantes():
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                sql = "SELECT * FROM solicitante ORDER BY id_comunidad DESC"
                cursor.execute(sql)
                return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener solicitantes: {e}")
        return []

# UPDATE: Modificar información de un solicitante existente
def actualizar_solicitante(datos):
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                sql = """UPDATE solicitante SET nombre_solicitante = %s, parroquia = %s, 
                         municipio = %s, ambito = %s, rif = %s, cedula = %s, correo = %s 
                         WHERE id_comunidad = %s"""
                
                rif_completo = f"{datos['tipo_rif']}-{datos['numero_rif']}"
                
                valores = (datos['nombre_solicitante'], datos['parroquia'], datos['municipio'], 
                           datos['ambito'], rif_completo, datos['cedula'], datos['correo'], datos['id_comunidad'])
                cursor.execute(sql, valores)
                conexion.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error al actualizar: {e}")
        return 0

# DELETE: Eliminar un registro
def eliminar_solicitante(id_comunidad):
    try:
        with connectionBD() as conexion:
            with conexion.cursor(dictionary=True) as cursor:
                sql = "DELETE FROM solicitante WHERE id_comunidad = %s"
                cursor.execute(sql, (id_comunidad,))
                conexion.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error al eliminar: {e}")
        return 0