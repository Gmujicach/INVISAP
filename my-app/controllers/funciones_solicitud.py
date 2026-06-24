"""
funciones_solicitud.py — Controlador de Solicitudes.
Coordina entre router y modelo, manejando los ValueErrors.
"""
from models.model_solicitudes import SolicitudModel

def obtener_solicitudes() -> list:
    """Retorna todas las solicitudes registradas."""
    return SolicitudModel.obtener_todas()

def crear_solicitud(datos_formulario: dict) -> dict:
    """
    Crea una nueva solicitud instanciando el modelo.
    Retorna dict {'success': bool, 'id': int, 'message': str}.
    """
    try:
        modelo = SolicitudModel()
        modelo.set_tipo_solicitud(datos_formulario.get('tipo_solicitud'))
        modelo.set_estatus_solicitud(datos_formulario.get('estatus'))
        modelo.set_problematica(datos_formulario.get('problematica'), datos_formulario.get('tipo_problematica'))
        modelo.set_fecha()
        modelo.set_solicitante_data(datos_formulario)
        
        nuevo_id = modelo.guardar()
        if nuevo_id:
            return {'success': True, 'id': nuevo_id, 'message': 'Solicitud registrada correctamente.'}
        return {'success': False, 'message': 'Error en la base de datos al guardar.'}
    except ValueError as e:
        return {'success': False, 'message': str(e)}
    except Exception as e:
        print(f"Error en crear_solicitud controlador: {e}")
        return {'success': False, 'message': 'Error interno del servidor.'}

def obtener_solicitud_por_id(id_solicitud) -> dict | None:
    """Retorna los datos de una solicitud específica."""
    if not id_solicitud:
        return None
    return SolicitudModel.buscar_por_id(id_solicitud)

def actualizar_solicitud(id_solicitud, datos_formulario: dict) -> dict:
    """Actualiza el estatus y problemática de una solicitud."""
    try:
        modelo = SolicitudModel(id_solicitudes=id_solicitud)
        modelo.set_estatus_solicitud(datos_formulario.get('estatus', datos_formulario.get('estatus_solicitud')))
        modelo.set_problematica(datos_formulario.get('problematica'))
        
        exito = modelo.actualizar()
        if exito:
            return {'success': True, 'message': 'Solicitud actualizada correctamente.'}
        return {'success': False, 'message': 'No se pudo actualizar la solicitud (posible ID no encontrado).'}
    except ValueError as e:
        return {'success': False, 'message': str(e)}

def eliminar_solicitud(id_solicitud) -> dict:
    """Elimina una solicitud por su ID."""
    modelo = SolicitudModel(id_solicitudes=id_solicitud)
    exito = modelo.eliminar()
    if exito:
        return {'success': True, 'message': 'Solicitud eliminada correctamente.'}
    return {'success': False, 'message': 'No se pudo eliminar la solicitud.'}

def obtener_estadisticas_solicitudes() -> dict:
    """Retorna estadísticas agrupadas por estatus."""
    return SolicitudModel.obtener_estadisticas()