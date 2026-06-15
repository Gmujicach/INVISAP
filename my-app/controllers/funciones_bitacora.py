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


def filtrar_bitacora(usuario: str = None, modulo: str = None, accion: str = None) -> list:
    """Filtra la bitácora por criterio. Prioridad: usuario > módulo > acción."""
    modelo = _get_modelo()
    if usuario:
        return modelo.filtrar_por_usuario(usuario)
    if modulo:
        return modelo.filtrar_por_modulo(modulo)
    if accion:
        return modelo.filtrar_por_accion(accion)
    return modelo.obtener_todos()


def obtener_estadisticas_bitacora() -> dict:
    """Retorna conteo de registros por tipo de acción."""
    return _get_modelo().estadisticas_por_accion()
