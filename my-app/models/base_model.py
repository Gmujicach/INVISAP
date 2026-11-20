"""
BaseModel — Funcionalidades comunes reutilizables para todos los modelos.
Centraliza limpieza de texto y ejecución de SQL con manejo automático de conexiones.
"""
import re
from conexion.conexionBD import ConexionBD


class BaseModel(ConexionBD):
    """Clase base con utilidades compartidas para modelos del sistema."""

    @staticmethod
    def _limpiar_texto(texto, max_len=255):
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    @classmethod
    def _ejecutar_sql(cls, sql, params=None):
        conn = None
        cur = None
        try:
            conn = cls.obtener_conexion()
            if not conn:
                return None, None, None
            cur = conn.cursor()
            cur.execute(sql, params or ())
            return cur, conn, None
        except Exception as e:
            print(f"[BaseModel] Error ejecutando SQL: {e}")
            if conn:
                conn.rollback()
            if cur:
                cur.close()
            if conn:
                conn.close()
            return None, None, e

    @staticmethod
    def _cerrar_recursos(cur, conn):
        if cur:
            try:
                cur.close()
            except Exception as e:
                print(f"[BaseModel] Error cerrando cursor: {e}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[BaseModel] Error cerrando conexión: {e}")
