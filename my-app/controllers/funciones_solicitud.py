# my-app/controllers/funciones_solicitud.py
from models.model_solicitudes import SolicitudModel


def obtener_solicitantes():
    """
    Devuelve todas las solicitudes registradas en la base de datos invilara.
    """
    modelo = SolicitudModel()
    return modelo.obtener_todas_las_solicitudes()


def crear_solicitante(datos_formulario):
    """
    Crea el solicitante o lo recupera y registra la solicitud en invilara.
    """
    if not datos_formulario.get('tipo_solicitud') or not datos_formulario.get('problematica'):
        return False

    modelo = SolicitudModel()
    return modelo.crear_nueva_solicitud(datos_formulario)


def obtener_solicitante_por_id(id_solicitud):
    """
    Recupera los datos de una solicitud por su identificador.
    """
    modelo = SolicitudModel()
    return modelo.obtener_solicitud_por_id(id_solicitud)


def eliminar_solicitud_por_id(id_solicitud):
    """
    Solicita al modelo que elimine un registro por su ID.
    """
    modelo = SolicitudModel()
    return modelo.eliminar_solicitud(id_solicitud)

def actualizar_datos_solicitud(id_solicitud, datos_formulario):
    """
    Solicita al modelo la actualización de los datos de la solicitud.
    """
    if not id_solicitud or not datos_formulario:
        return False
    
    modelo = SolicitudModel()
    return modelo.actualizar_solicitud(id_solicitud, datos_formulario)