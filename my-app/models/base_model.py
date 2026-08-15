"""
BaseModel — Funcionalidades comunes reutilizables para todos los modelos.
Centraliza limpieza de texto y ejecución de SQL con manejo automático de conexiones.
"""
import re
from conexion.conexionBD import connectionBD_invilara


class BaseModel:
    """Clase base con utilidades compartidas para modelos del sistema."""

    @staticmethod
    def _limpiar_texto(texto, max_len=255):
        if not isinstance(texto, str):
            texto = str(texto or '')
        return re.sub(r'[<>\'";\\]', '', texto).strip()[:max_len]

    @staticmethod
    def _ejecutar_sql(sql, params=None):
        conn = None
        cur = None
        try:
            conn = connectionBD_invilara()
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
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass
