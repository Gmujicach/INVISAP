"""
funciones_bitacora.py — Controlador de Bitácora.

Principio SRP: Solo coordina entre router y modelo.
No contiene lógica de negocio ni SQL.
"""
import re
from datetime import datetime
from models.model_bitacora import BitacoraModel


def _get_modelo() -> BitacoraModel:
    """Fábrica del modelo (DRY)."""
    return BitacoraModel()


def _limpiar_fecha(valor):
    if valor is None:
        return ''
    s = str(valor).strip()
    s = re.sub(r'\s*GMT\s*$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*[+-]\d{2}:?\d{2}$', '', s).strip()
    return s


def _formatear_fecha(valor):
    limpio = _limpiar_fecha(valor)
    if not limpio:
        return ''
    try:
        dt = datetime.strptime(limpio, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d/%m/%Y · %I:%M:%S %p')
    except Exception:
        return limpio


def _formatear_hora(valor):
    limpio = _limpiar_fecha(valor)
    if not limpio:
        return ''
    try:
        dt = datetime.strptime(limpio, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%I:%M:%S %p')
    except Exception:
        return limpio


def _formatear_registro(registro):
    if not registro:
        return registro
    registro = dict(registro)
    registro['fecha_raw'] = _limpiar_fecha(registro.get('fecha'))
    registro['hora_inicio_raw'] = _limpiar_fecha(registro.get('hora_inicio_sesion'))
    registro['hora_cierre_raw'] = _limpiar_fecha(registro.get('hora_cierre_sesion'))
    registro['fecha'] = _formatear_fecha(registro.get('fecha'))
    registro['hora_inicio_sesion'] = _formatear_hora(registro.get('hora_inicio_sesion'))
    registro['hora_cierre_sesion'] = _formatear_hora(registro.get('hora_cierre_sesion'))
    return registro


def _formatear_registros(registros):
    return [_formatear_registro(r) for r in registros]


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


def filtrar_bitacora_html(usuario: str = None, modulo: str = None, accion: str = None, page: int = 1, per_page: int = 10) -> list:
    """Filtra la bitácora y devuelve registros con fechas formateadas para la vista HTML."""
    modelo = _get_modelo()
    registros = modelo.filtrar_por_criterios(
        usuario=usuario, modulo=modulo, accion=accion,
        page=page, per_page=per_page
    )
    return _formatear_registros(registros)


def contar_bitacora_filtrada(usuario: str = None, modulo: str = None, accion: str = None) -> int:
    """Cuenta el total de registros filtrados sin paginar."""
    modelo = _get_modelo()
    return modelo.contar_filtrados(
        usuario=usuario, modulo=modulo, accion=accion
    )


def obtener_estadisticas_bitacora() -> dict:
    """Retorna conteo de registros por tipo de acción."""
    return _get_modelo().estadisticas_por_accion()
