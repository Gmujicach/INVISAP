

import os
import mysql.connector
from mysql.connector import Error


def connectionBD():
    """Return a new MySQL connection. Reads configuration from env vars with sane defaults."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'crud_python'),
            charset='utf8mb4'
        )
        if connection.is_connected():
            return connection
        raise Error('No se pudo establecer la conexión a la base de datos')
    except Error as error:
        # Re-raise so callers can handle/log accordingly
        raise
