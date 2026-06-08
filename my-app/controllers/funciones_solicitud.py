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
