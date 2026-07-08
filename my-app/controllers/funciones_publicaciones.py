from models.model_publicacion import PublicacionModel
from services.bitacora_service import BitacoraService
from flask import session

def listar_publicaciones_controller():
    modelo = PublicacionModel()
    return modelo.obtener_todas_las_publicaciones()

def registrar_publicacion_controller(data):
    data_form = data.to_dict()
    modelo = PublicacionModel()
    resultado = modelo.registrar_publicacion(data_form)
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Publicaciones', 'CREAR',
            f'Publicó: {data_form.get("titulo_publicacion")}'
        )
    return resultado

def eliminar_publicacion_controller(id_publicacion):
    modelo = PublicacionModel(id_publicacion=id_publicacion)
    resultado = modelo.eliminar()
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Publicaciones', 'ELIMINAR',
            f'Eliminó la publicación ID: {id_publicacion}'
        )
    return resultado

def obtener_publicacion_por_id_controller(id_publicacion):
    modelo = PublicacionModel()
    return modelo.obtener_publicacion_por_id(id_publicacion)

def actualizar_publicacion_controller(id_publicacion, data):
    data_form = data.to_dict()
    modelo = PublicacionModel()
    resultado = modelo.actualizar_publicacion(id_publicacion, data_form)
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Publicaciones', 'EDITAR',
            f'Modificó la publicación ID: {id_publicacion}'
        )
    return resultado