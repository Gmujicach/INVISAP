"""
BaseConexionBD — Único punto de acceso a la base de datos para todo el sistema.

hereda de esta clase (o de `models.base_model.BaseModel`, que ya la hereda) y
obtiene su conexión mediante los métodos de esta interfaz.

Los cuatro getters son equivalentes 1:1 con las funciones de `conexionBD`, por lo
que la semántica de manejo de errores se conserva exactamente:
"""
from conexion.conexionBD import (
    connectionBD,
    connectionBD_invilara,
    connectionBD_seguridad,
    connectionBD_invilara_seguridad,
    get_db_config,
)


class BaseConexionBD:
    """Proveedor común de conexiones para la jerarquía de modelos y servicios."""

    @staticmethod
    def configuracion_db():
        """Diccionario de configuración de la base principal (respaldos, diagnósticos)."""
        return get_db_config()

    @staticmethod
    def obtener_conexion():
        """Conexión a la base principal. Devuelve None si no se pudo conectar."""
        return connectionBD_invilara()

    @staticmethod
    def obtener_conexion_estricta():
        """Conexión a la base principal. Lanza mysql.connector.Error si falla."""
        return connectionBD()

    @staticmethod
    def obtener_conexion_seguridad():
        """Conexión a la base de seguridad. Lanza mysql.connector.Error si falla."""
        return connectionBD_seguridad()

    @staticmethod
    def obtener_conexion_seguridad_segura():
        """Conexión a la base de seguridad. Devuelve None si no se pudo conectar."""
        return connectionBD_invilara_seguridad()
