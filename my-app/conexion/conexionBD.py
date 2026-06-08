

import os
import mysql.connector
from mysql.connector import Error


def connectionBD():
    """Return a new MySQL connection. Reads configuration from env vars with sane defaults."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'balto04*'),
        'database': os.getenv('DB_NAME', 'crud_python'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'auth_plugin': os.getenv('DB_AUTH_PLUGIN', 'mysql_native_password')
    }

    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'balto04*'),
            database=os.getenv('DB_NAME', 'crud_python'),
            charset='utf8mb4'
        )
        if connection.is_connected():
            return connection
        raise Error('No se pudo establecer la conexión a la base de datos')
    except Error as error:
        raise Error(f"Error al conectar con la base de datos: {error}") from error



def connectionBD_invilara():
    # 1. Declaramos la variable de conexión inicializada en None
    connection = None
    try:
        # 2. Intentamos establecer la conexión con el conector de MySQL
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'balto04*'), # Asegúrate de que esta sea tu clave
            database='invilara', # Apuntando al nombre de la BD en tu .sql
            charset='utf8mb4'               # Puerto por defecto de MySQL
        )
        
        # 3. Verificamos si la conexión fue exitosa
        if connection.is_connected():
            print("Conexión exitosa a la base de datos Invilara.")
            return connection
            
    except Error as e:
        # 4. Capturamos cualquier error (ej. credenciales inválidas o servicio apagado)
        print(f"Error al conectar a MySQL: {e}")
        return None
    