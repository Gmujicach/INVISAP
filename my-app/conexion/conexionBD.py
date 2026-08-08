import os
import mysql.connector
from mysql.connector import Error

def _load_env():
    """Simple .env loader without external dependencies."""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

_load_env()

def _get_env(key, default=''):
    """Obtener variable de entorno o valor por defecto."""
    val = os.getenv(key, '')
    return val if val else default

def connectionBD():
    """Return a new MySQL connection. Reads configuration from env vars with sane defaults."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'invilara'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'auth_plugin': _get_env('DB_AUTH_PLUGIN', 'mysql_native_password')
    }
    
    print(f"[DEBUG] Conectando a MySQL: host={db_config['host']}, user={db_config['user']}, db={db_config['database']}")

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
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME_SEGURIDAD', 'invilara_seguridad'),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'auth_plugin': _get_env('DB_AUTH_PLUGIN', 'mysql_native_password')
    }

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
        raise Error('No se pudo establecer la conexión a la base de datos')
    except Error as error:
        raise Error(f"Error al conectar con la base de datos: {error}") from error


def connectionBD_invilara_seguridad():
    """Wrapper para connectionBD_seguridad que retorna None en caso de error para compatibilidad con modelos."""
    try:
        connection = connectionBD_seguridad()
        if connection.is_connected():
            return connection
    except Exception as e:
        print(f"Error en la conexión a la base de datos: {e}")
        return None