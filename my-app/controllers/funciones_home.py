
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file


def procesar_form_empleado(dataForm, foto_perfil):
    # Formateando Salario
    salario_sin_puntos = re.sub('[^0-9]+', '', dataForm['salario_empleado'])
    # convertir salario a INT
    salario_entero = int(salario_sin_puntos)

    result_foto_perfil = procesar_imagen_perfil(foto_perfil) if foto_perfil else None
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        try:
            sql = "INSERT INTO tbl_empleados (nombre_empleado, apellido_empleado, sexo_empleado, telefono_empleado, email_empleado, profesion_empleado, foto_empleado, salario_empleado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            valores = (dataForm['nombre_empleado'], dataForm['apellido_empleado'], dataForm['sexo_empleado'],
                       dataForm['telefono_empleado'], dataForm['email_empleado'], dataForm['profesion_empleado'], result_foto_perfil, salario_entero)
            cursor.execute(sql, valores)
            conexion_MySQLdb.commit()
            resultado_insert = cursor.rowcount
            return resultado_insert
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        return f'Se produjo un error en procesar_form_empleado: {str(e)}'


def procesar_imagen_perfil(foto):
    try:
        # Nombre original del archivo
        filename = secure_filename(foto.filename)
        extension = os.path.splitext(filename)[1]

        # Creando un string de 50 caracteres
        nuevoNameFile = (uuid.uuid4().hex + uuid.uuid4().hex)[:100]
        nombreFile = nuevoNameFile + extension

        # Construir la ruta completa de subida del archivo
        basepath = os.path.abspath(os.path.dirname(__file__))
        upload_dir = os.path.join(basepath, f'../static/fotos_empleados/')

        # Validar si existe la ruta y crearla si no existe
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            # Dando permiso a la carpeta
            os.chmod(upload_dir, 0o755)

        # Construir la ruta completa de subida del archivo
        upload_path = os.path.join(upload_dir, nombreFile)
        foto.save(upload_path)

        return nombreFile

    except Exception as e:
        print("Error al procesar archivo:", e)
        return []


# Lista de Empleados
def sql_lista_empleadosBD():
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = (f"""
                    SELECT 
                        e.id_empleado,
                        e.nombre_empleado, 
                        e.apellido_empleado,
                        e.salario_empleado,
                        e.foto_empleado,
                        CASE
                            WHEN e.sexo_empleado = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_empleado
                    FROM tbl_empleados AS e
                    ORDER BY e.id_empleado DESC
                    """)
            cursor.execute(querySQL,)
            empleadosBD = cursor.fetchall()
            return empleadosBD
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(
            f"Errro en la función sql_lista_empleadosBD: {e}")
        return None


# Detalles del Empleado
def sql_detalles_empleadosBD(idEmpleado):
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = ("""
                    SELECT 
                        e.id_empleado,
                        e.nombre_empleado, 
                        e.apellido_empleado,
                        e.salario_empleado,
                        CASE
                            WHEN e.sexo_empleado = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_empleado,
                        e.telefono_empleado, 
                        e.email_empleado,
                        e.profesion_empleado,
                        e.foto_empleado,
                        DATE_FORMAT(e.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro
                    FROM tbl_empleados AS e
                    WHERE id_empleado =%s
                    ORDER BY e.id_empleado DESC
                    """)
            cursor.execute(querySQL, (idEmpleado,))
            empleadosBD = cursor.fetchone()
            return empleadosBD
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(
            f"Errro en la función sql_detalles_empleadosBD: {e}")
        return None


# Funcion Empleados Informe (Reporte)
def empleadosReporte():
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = ("""
                    SELECT 
                        e.id_empleado,
                        e.nombre_empleado, 
                        e.apellido_empleado,
                        e.salario_empleado,
                        e.email_empleado,
                        e.telefono_empleado,
                        e.profesion_empleado,
                        DATE_FORMAT(e.fecha_registro, '%d de %b %Y %h:%i %p') AS fecha_registro,
                        CASE
                            WHEN e.sexo_empleado = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_empleado
                    FROM tbl_empleados AS e
                    ORDER BY e.id_empleado DESC
                    """)
            cursor.execute(querySQL,)
            empleadosBD = cursor.fetchall()
            return empleadosBD
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(
            f"Errro en la función empleadosReporte: {e}")
        return None



def buscarEmpleadoBD(search):
    try:
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = ("""
                        SELECT 
                            e.id_empleado,
                            e.nombre_empleado, 
                            e.apellido_empleado,
                            e.salario_empleado,
                            CASE
                                WHEN e.sexo_empleado = 1 THEN 'Masculino'
                                ELSE 'Femenino'
                            END AS sexo_empleado
                        FROM tbl_empleados AS e
                        WHERE e.nombre_empleado LIKE %s 
                        ORDER BY e.id_empleado DESC
                    """)
            search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
            mycursor.execute(querySQL, (search_pattern,))
            resultado_busqueda = mycursor.fetchall()
            return resultado_busqueda
        finally:
            mycursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoBD: {e}")
        return []


def buscarEmpleadoUnico(id):
    try:
        conexion_MySQLdb = connectionBD()
        mycursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = ("""
                        SELECT 
                            e.id_empleado,
                            e.nombre_empleado, 
                            e.apellido_empleado,
                            e.sexo_empleado,
                            e.telefono_empleado,
                            e.email_empleado,
                            e.profesion_empleado,
                            e.salario_empleado,
                            e.foto_empleado
                        FROM tbl_empleados AS e
                        WHERE e.id_empleado =%s LIMIT 1
                    """)
            mycursor.execute(querySQL, (id,))
            empleado = mycursor.fetchone()
            return empleado
        finally:
            mycursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoUnico: {e}")
        return []


def procesar_actualizacion_form(data):
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        try:
            # Extraer y procesar datos del formulario
            nombre_empleado = data.form['nombre_empleado']
            apellido_empleado = data.form['apellido_empleado']
            sexo_empleado = data.form['sexo_empleado']
            telefono_empleado = data.form['telefono_empleado']
            email_empleado = data.form['email_empleado']
            profesion_empleado = data.form['profesion_empleado']

            # Procesar salario eliminando caracteres no numéricos
            salario_sin_puntos = re.sub('[^0-9]+', '', data.form['salario_empleado'])
            salario_empleado = int(salario_sin_puntos)
            id_empleado = data.form['id_empleado']

            # Construir consulta SQL y parámetros dinámicamente
            query_base = """
                UPDATE tbl_empleados
                SET 
                    nombre_empleado = %s,
                    apellido_empleado = %s,
                    sexo_empleado = %s,
                    telefono_empleado = %s,
                    email_empleado = %s,
                    profesion_empleado = %s,
                    salario_empleado = %s
            """
            params = [
                nombre_empleado, apellido_empleado, sexo_empleado,
                telefono_empleado, email_empleado, profesion_empleado, salario_empleado
            ]

            # Verificar si se subió un archivo de foto
            if 'foto_empleado' in data.files and data.files['foto_empleado'].filename != '':
                file = data.files['foto_empleado']
                fotoForm = procesar_imagen_perfil(file)
                query_base += ", foto_empleado = %s"
                params.append(fotoForm)

            # Agregar condición WHERE
            query_base += " WHERE id_empleado = %s"
            params.append(id_empleado)

            # Ejecutar la consulta
            cursor.execute(query_base, params)
            conexion_MySQLdb.commit()

            return cursor.rowcount or []
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Ocurrió un error en procesar_actualizacion_form: {e}")
        return None


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor(dictionary=True)
        try:
            querySQL = "SELECT id, name_surname, email_user, pass_user, created_user FROM users"
            cursor.execute(querySQL,)
            usuariosBD = cursor.fetchall()
            return usuariosBD
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []

# Eliminar uEmpleado
def eliminarEmpleado(id_empleado, foto_empleado):
    try:
        conexion_MySQLdb = connectionBD()
        cursor = conexion_MySQLdb.cursor()
        try:
            querySQL = "DELETE FROM tbl_empleados WHERE id_empleado=%s"
            cursor.execute(querySQL, (id_empleado,))
            conexion_MySQLdb.commit()
            resultado_eliminar = cursor.rowcount

            if resultado_eliminar:
                basepath = path.dirname(__file__)
                url_File = path.join(basepath, '../static/fotos_empleados', foto_empleado)

                if path.exists(url_File):
                    remove(url_File)
            return resultado_eliminar
        finally:
            cursor.close()
            conexion_MySQLdb.close()
    except Exception as e:
        print(f"Error en eliminarEmpleado : {e}")
        return []
