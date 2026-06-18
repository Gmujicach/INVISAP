import os
import mysql.connector
from mysql.connector import Error


def connectionBD():
    """Return a new MySQL connection. Reads configuration from env vars with sane defaults."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'invilara'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'auth_plugin': os.getenv('DB_AUTH_PLUGIN', 'mysql_native_password')
    }

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
        raise Error('No se pudo establecer la conexión a la base de datos')
    except Error as error:
        raise Error(f"Error al conectar con la base de datos: {error}") from error



def connectionBD_invilara():
    """Wrapper para connectionBD que retorna None en caso de error para compatibilidad con modelos."""
    try:
        connection = connectionBD()
        if connection.is_connected():
            return connection
    except Exception as e:
        print(f"Error en la conexión a la base de datos: {e}")
        return None
    
def connectionBD_seguridad():
    """Return a new MySQL connection. Reads configuration from env vars with sane defaults."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '1234'),
        'database': os.getenv('DB_NAME_SEGURIDAD', 'invilara_seguridad'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'auth_plugin': os.getenv('DB_AUTH_PLUGIN', 'mysql_native_password')
    }

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
        raise Error('No se pudo establecer la conexión a la base de datos')
    except Error as error:
        raise Error(f"Error al conectar con la base de datos: {error}") from error



def connectionBD_invilara_seguridad():
    """Wrapper para connectionBD que retorna None en caso de error para compatibilidad con modelos."""
    try:
        connection = connectionBD_seguridad()
        if connection.is_connected():
            return connection
    except Exception as e:
        print(f"Error en la conexión a la base de datos: {e}")
        return None