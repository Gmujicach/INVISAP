"""
funciones_solicitud.py — Controlador de Solicitudes.
Coordina entre router y modelo, manejando los ValueErrors.
"""
from models.model_solicitudes import SolicitudModel
from services.bitacora_service import BitacoraService
<<<<<<< Updated upstream
from flask import session
=======


def _registrar_bitacora(session: dict, accion: str, id_solicitud: int | None, descripcion: str) -> None:
    """Registra una acción de solicitudes en la bitácora si el usuario tiene sesión activa."""
    if not session:
        return
    BitacoraService.registrar_accion(
        session=session,
        modulo='Solicitudes',
        accion=accion,
        descripcion=f'{descripcion} (Solicitud #{id_solicitud})' if id_solicitud else descripcion,
    )

>>>>>>> Stashed changes

def obtener_solicitudes() -> list:
    """Retorna todas las solicitudes registradas."""
    return SolicitudModel.obtener_todas()

def obtener_solicitudes_pendientes() -> list:
    """Retorna solo las solicitudes con estatus 'Pendiente'."""
    return SolicitudModel.obtener_solicitudes_pendientes()

def crear_solicitud(datos_formulario: dict, session: dict | None = None) -> dict:
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
<<<<<<< Updated upstream
            BitacoraService.registrar_accion(
                session, 'Solicitudes', 'CREAR',
                f'Registró una nueva solicitud con ID: {nuevo_id}'
            )
=======
            if session:
                _registrar_bitacora(
                    session,
                    'CREAR',
                    nuevo_id,
                    'Solicitud creada desde el sistema'
                )
>>>>>>> Stashed changes
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

def actualizar_solicitud(id_solicitud, datos_formulario: dict, session: dict | None = None) -> dict:
    """Actualiza el estatus y problemática de una solicitud."""
    try:
        modelo = SolicitudModel(id_solicitudes=id_solicitud)
        modelo.set_estatus_solicitud(datos_formulario.get('estatus', datos_formulario.get('estatus_solicitud')))
        modelo.set_problematica(datos_formulario.get('problematica'))
        
        exito = modelo.actualizar()
        if exito:
<<<<<<< Updated upstream
            BitacoraService.registrar_accion(
                session, 'Solicitudes', 'EDITAR',
                f'Modificó la solicitud con ID: {id_solicitud}'
            )
=======
            if session:
                _registrar_bitacora(
                    session,
                    'EDITAR',
                    id_solicitud,
                    'Solicitud actualizada'
                )
>>>>>>> Stashed changes
            return {'success': True, 'message': 'Solicitud actualizada correctamente.'}
        return {'success': False, 'message': 'No se pudo actualizar la solicitud (posible ID no encontrado).'}
    except ValueError as e:
        return {'success': False, 'message': str(e)}

def eliminar_solicitud(id_solicitud, session: dict | None = None) -> dict:
    """Elimina una solicitud por su ID."""
    modelo = SolicitudModel(id_solicitudes=id_solicitud)
    exito = modelo.eliminar()
    if exito:
<<<<<<< Updated upstream
        BitacoraService.registrar_accion(
            session, 'Solicitudes', 'ELIMINAR',
            f'Eliminó la solicitud con ID: {id_solicitud}'
        )
=======
        if session:
            _registrar_bitacora(
                session,
                'ELIMINAR',
                id_solicitud,
                'Solicitud eliminada'
            )
>>>>>>> Stashed changes
        return {'success': True, 'message': 'Solicitud eliminada correctamente.'}
    return {'success': False, 'message': 'No se pudo eliminar la solicitud.'}

def obtener_estadisticas_solicitudes() -> dict:
    """Retorna estadísticas agrupadas por estatus con total."""
    stats = SolicitudModel.obtener_estadisticas()
    stats['total_solicitudes'] = sum(stats.values()) if stats else 0
    return stats

def obtener_dashboard_datos() -> dict:
    stats = obtener_estadisticas_solicitudes()
    stats['por_tipo'] = SolicitudModel.obtener_estadisticas_por_tipo()
    stats['por_parroquia'] = SolicitudModel.obtener_estadisticas_por_parroquia()
    stats['pendientes_priorizadas'] = SolicitudModel.obtener_solicitudes_priorizadas(8)
    return stats