# my-app/controllers/funciones_solicitud.py
from models.model_gerencias import GerenciaModel


def obtener_gerencias():
    """
    Devuelve todas las solicitudes registradas en la base de datos invilara.
    """
    modelo = GerenciaModel()
    return modelo.obtener_todas_las_Gerencias()


def crear_gerencia(datos_formulario):
    """
    Crea el solicitante o lo recupera y registra la solicitud en invilara.
    """
    if not datos_formulario.get('tipo_gerencia') or not datos_formulario.get('problematica'):
        return False

    modelo = GerenciaModel()
    return modelo.crear_nueva_gerencia(datos_formulario)


def obtener_gerencia_por_id(id_gerencia):
    """
    Recupera los datos de una solicitud por su identificador.
    """
    modelo = GerenciaModel()
    return modelo.obtener_gerencia_por_id(id_gerencia)