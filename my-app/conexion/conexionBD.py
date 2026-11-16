import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


def _load_env():
    """Load local configuration without overriding explicitly set environment variables."""
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(env_path, override=False)

_load_env()


def _get_env(key, default=''):
    """Obtener variable de entorno o valor por defecto."""
    val = os.getenv(key, '')
    return val if val else default


def get_db_config():
    """Retorna la configuración de conexión a la base de datos principal con pooling."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'invilara'),
        'port': int(_get_env('DB_PORT', '3306')),
        'connection_timeout': int(_get_env('DB_CONNECT_TIMEOUT', '5')),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'pool_name': 'invilara_pool',
        'pool_size': 10,
        'pool_reset_session': True,
    }
    auth_plugin = _get_env('DB_AUTH_PLUGIN', '')
    if auth_plugin:
        db_config['auth_plugin'] = auth_plugin
    return db_config

def connectionBD():
    """Return a new MySQL connection. Reads configuration from env vars with sane defaults."""
    db_config = get_db_config()

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
        raise Error('No se pudo establecer la conexión a la base de datos')
    except Error as error:
        raise Error(f"Error al conectar con la base de datos: {error}") from error

def connectionBD_invilara():
    """Wrapper para connectionBD que retorna un None en caso de error para compatibilidad con modelos."""
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
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME_SEGURIDAD', 'invilara_seguridad'),
        'port': int(_get_env('DB_PORT', '3306')),
        'connection_timeout': int(_get_env('DB_CONNECT_TIMEOUT', '5')),
        'charset': 'utf8mb4',
        'use_unicode': True,
        'pool_name': 'invilara_seguridad_pool',
        'pool_size': 10,
        'pool_reset_session': True,
    }
    auth_plugin = _get_env('DB_AUTH_PLUGIN', '')
    if auth_plugin:
        db_config['auth_plugin'] = auth_plugin

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

class ConexionBD:
    @staticmethod
    def configuracion_db():
        return get_db_config()
    @staticmethod
    def obtener_conexion():
        return connectionBD_invilara()
    @staticmethod
    def obtener_conexion_estricta():
        return connectionBD()
    @staticmethod
    def obtener_conexion_seguridad():
        return connectionBD_seguridad()
    @staticmethod
    def obtener_conexion_seguridad_segura():
        return connectionBD_invilara_seguridad()


# Aliases para uso directo por herencia/import flexible
ConexionBD_seguridad = ConexionBD.obtener_conexion_seguridad
ConexionBD_invilara = ConexionBD.obtener_conexion
ConexionBD_invilara_seguridad = ConexionBD.obtener_conexion_seguridad_segura
