"""
funciones_bitacora.py — Controlador de Bitácora.

Principio SRP: Solo coordina entre router y modelo.
No contiene lógica de negocio ni SQL.
"""
from typing import Optional, Tuple, Dict, List


def _get_modelo():
    from models.model_bitacora import BitacoraModel
    return BitacoraModel()


def filtrar_bitacora(usuario: str = None, modulo: str = None, accion: str = None) -> list:
    """Filtra la bitácora por criterio."""
    modelo = _get_modelo()
    usuario = (usuario or '').strip().lower()
    modulo = (modulo or '').strip().lower()
    accion = (accion or '').upper().strip()
    return modelo._sql_obtener_paginado(usuario=usuario or None, modulo=modulo or None, accion=accion or None, page=1, per_page=500)[0]


def obtener_estadisticas_bitacora() -> dict:
    """Retorna conteo de registros por tipo de acción."""
    return _get_modelo().estadisticas_por_accion()


def obtener_bitacora_paginada(page: int = 1, per_page: int = 10,
                              usuario: str = None, modulo: str = None, accion: str = None) -> Tuple[List[Dict], Dict]:
    """Retorna registros paginados y metadatos de paginación."""
    modelo = _get_modelo()
    usuario = (usuario or '').strip().lower()
    modulo = (modulo or '').strip().lower()
    accion = (accion or '').upper().strip()

    registros, total = modelo._sql_obtener_paginado(
        page=page,
        per_page=per_page,
        usuario=usuario or None,
        modulo=modulo or None,
        accion=accion or None
    )

    total_pages = max((total + per_page - 1) // per_page, 1)
    page = max(int(page or 1), 1)
    if page > total_pages:
        page = total_pages

    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1,
        'next_num': page + 1,
        'pages': list(range(1, total_pages + 1)),
    }
    return registros, pagination
