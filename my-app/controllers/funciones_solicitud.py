from conexion.conexionBD import connectionBD
from flask import url_for


def procesar_form_solicitud(dataForm, foto=None):
    """Inserta un solicitante (según tipo) y luego la solicitud en la tabla gestionar_solicitudes."""
    try:
        tipo = dataForm.get('tipo_solicitud')
        estatus = dataForm.get('estatus')
        fecha = dataForm.get('fecha')
        problematica = dataForm.get('problematica')

        # Preparar datos del solicitante según el tipo
        nombre = ''
        parroquia = ''
        municipio = ''
        ambito = ''
        rif = ''
        cedula = ''
        correo = ''
        telefono = ''
        direccion = ''

        if tipo == 'Comunidad':
            nombre = dataForm.get('com_nombre') or ''
            rif_letra = dataForm.get('com_rif_letra') or ''
            rif_num = dataForm.get('com_rif_numero') or ''
            rif = f"{rif_letra}{rif_num}" if (rif_letra or rif_num) else ''
            cedula = dataForm.get('com_cedula') or ''
            correo = dataForm.get('com_correo') or ''
            telefono = dataForm.get('com_telefono') or ''
            direccion = ''
            parroquia = dataForm.get('com_parroquia') or ''
            municipio = dataForm.get('com_municipio') or ''
            ambito = dataForm.get('com_ambito') or ''

        elif tipo == 'Institucion':
            nombre = dataForm.get('inst_nombre') or ''
            direccion = dataForm.get('inst_direccion') or ''
            correo = dataForm.get('inst_correo') or ''
            telefono = dataForm.get('inst_telefono') or ''
            cedula = dataForm.get('inst_director_cedula') or ''
            # usar campos director como parte del nombre si hace falta
            cedula = str(cedula)

        else:  # Particular
            nombre = dataForm.get('part_nombre') or ''
            cedula = dataForm.get('part_cedula') or ''
            correo = dataForm.get('part_correo') or ''
            telefono = dataForm.get('part_telefono') or ''
            direccion = dataForm.get('part_direccion') or ''

        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Insertar solicitante y obtener id_comunidad
                sql_insert_solicitante = (
                    "INSERT INTO solicitante (nombre_solicitante, parroquia, municipio, ambito, rif, cedula, correo)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s)"
                )
                valores_solicitante = (nombre, parroquia, municipio, ambito, rif, cedula, correo)
                cursor.execute(sql_insert_solicitante, valores_solicitante)
                conexion_MySQLdb.commit()
                solicitante_id = cursor.lastrowid or 0

                # Insertar en gestionar_solicitudes
                sql_insert_solicitud = (
                    "INSERT INTO gestionar_solicitudes (fecha, telefono_solicitante, direccion_solicitante, tipo_solicitud, estatus_solicitud, problematica, tipo_solicitante, solicitante_id_comunidad)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                )
                valores_solicitud = (
                    fecha,
                    telefono,
                    direccion,
                    tipo,
                    estatus,
                    problematica,
                    tipo,
                    solicitante_id,
                )
                cursor.execute(sql_insert_solicitud, valores_solicitud)
                conexion_MySQLdb.commit()
                return cursor.rowcount

    except Exception as e:
        print(f"Error en procesar_form_solicitud: {e}")
        return None


def sql_lista_solicitudesBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT
                        g.id_solicitud,
                        g.fecha,
                        g.tipo_solicitud,
                        g.estatus_solicitud,
                        g.problematica,
                        s.nombre_solicitante,
                        s.cedula,
                        s.correo
                    FROM gestionar_solicitudes AS g
                    LEFT JOIN solicitante AS s ON s.id_comunidad = g.solicitante_id_comunidad
                    ORDER BY g.id_solicitud DESC
                """)
                cursor.execute(querySQL)
                solicitudes = cursor.fetchall()
        return solicitudes
    except Exception as e:
        print(f"Error en sql_lista_solicitudesBD: {e}")
        return []


def sql_detalles_solicitudesBD(idSolicitud):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT
                        g.id_solicitud,
                        DATE_FORMAT(g.fecha, '%d/%m/%Y %H:%i') AS fecha,
                        g.telefono_solicitante,
                        g.direccion_solicitante,
                        g.tipo_solicitud,
                        g.estatus_solicitud,
                        g.problematica,
                        s.*
                    FROM gestionar_solicitudes AS g
                    LEFT JOIN solicitante AS s ON s.id_comunidad = g.solicitante_id_comunidad
                    WHERE g.id_solicitud = %s
                    LIMIT 1
                """)
                cursor.execute(querySQL, (idSolicitud,))
                detalle = cursor.fetchone()
        return detalle
    except Exception as e:
        print(f"Error en sql_detalles_solicitudesBD: {e}")
        return None


def eliminar_solicitud(id_solicitud):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM gestionar_solicitudes WHERE id_solicitud = %s"
                cursor.execute(querySQL, (id_solicitud,))
                conexion_MySQLdb.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error en eliminar_solicitud: {e}")
        return []


def actualizar_solicitud(request):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                id_solicitud = request.form.get('id_solicitud')
                estatus = request.form.get('estatus')
                fecha = request.form.get('fecha')
                problematica = request.form.get('problematica')

                query = (
                    "UPDATE gestionar_solicitudes SET estatus_solicitud = %s, fecha = %s, problematica = %s WHERE id_solicitud = %s"
                )
                cursor.execute(query, (estatus, fecha, problematica, id_solicitud))
                conexion_MySQLdb.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error en actualizar_solicitud: {e}")
        return None
