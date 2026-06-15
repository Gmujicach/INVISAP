"""
funciones_solicitud.py — Controlador de Solicitudes.

Principio SRP: Solo coordina entre router y modelo.
No contiene lógica de negocio ni SQL.
"""
from models.model_solicitudes import SolicitudModel


def _get_modelo() -> SolicitudModel:
    """Fábrica del modelo (DRY)."""
    return SolicitudModel()


def obtener_solicitudes() -> list:
    """Retorna todas las solicitudes registradas."""
    return _get_modelo().obtener_todas_las_solicitudes()


def crear_solicitud(datos_formulario: dict):
    """
    Crea una nueva solicitud.
    Retorna el ID de la nueva solicitud o False si falla.
    """
    if not datos_formulario.get('tipo_solicitud') or not datos_formulario.get('problematica'):
        return False
    return _get_modelo().crear_nueva_solicitud(datos_formulario)


def obtener_solicitud_por_id(id_solicitud) -> dict | None:
    """Retorna los datos de una solicitud específica."""
    if not id_solicitud:
        return None
    return _get_modelo().obtener_solicitud_por_id(id_solicitud)


def actualizar_solicitud(id_solicitud, datos_formulario: dict) -> bool:
    """Actualiza el estatus y problemática de una solicitud."""
    if not id_solicitud or not datos_formulario:
        return False
    return _get_modelo().actualizar_solicitud(id_solicitud, datos_formulario)


def eliminar_solicitud(id_solicitud) -> bool:
    """Elimina una solicitud por su ID."""
    if not id_solicitud:
        return False
    return _get_modelo().eliminar_solicitud(id_solicitud)


def obtener_estadisticas_solicitudes() -> dict:
    """Retorna estadísticas agrupadas por estatus."""
    return _get_modelo().obtener_estadisticas()