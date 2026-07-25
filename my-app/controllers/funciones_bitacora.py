"""
funciones_bitacora.py — Controlador de Bitácora.

Principio SRP: Solo coordina entre router y modelo.
No contiene lógica de negocio ni SQL.
"""
from models.model_bitacora import BitacoraModel


def _get_modelo() -> BitacoraModel:
    """Fábrica del modelo (DRY)."""
    return BitacoraModel()


def obtener_bitacora() -> list:
    """Retorna todos los registros de la bitácora (máx 500)."""
    return _get_modelo().obtener_todos()


def filtrar_bitacora(usuario: str = None, modulo: str = None, accion: str = None, page: int = 1, per_page: int = 10) -> list:
    """Filtra la bitácora combinando todos los criterios activos con AND."""
    modelo = _get_modelo()
    return modelo.filtrar_por_criterios(
        usuario=usuario, modulo=modulo, accion=accion,
        page=page, per_page=per_page
    )


def contar_bitacora_filtrada(usuario: str = None, modulo: str = None, accion: str = None) -> int:
    """Cuenta el total de registros filtrados sin paginar."""
    modelo = _get_modelo()
    return modelo.contar_filtrados(
        usuario=usuario, modulo=modulo, accion=accion
    )


def obtener_estadisticas_bitacora() -> dict:
    """Retorna conteo de registros por tipo de acción."""
    return _get_modelo().estadisticas_por_accion()
