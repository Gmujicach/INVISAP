from models.model_publicacion import PublicacionModel

def listar_publicaciones_controller():
    modelo = PublicacionModel()
    return modelo.obtener_todas_las_publicaciones()

def registrar_publicacion_controller(data):
    data_form = data.to_dict()
    modelo = PublicacionModel()
    return modelo.registrar_publicacion(data_form)

def eliminar_publicacion_controller(id_publicacion):
    modelo = PublicacionModel(id_publicacion=id_publicacion)
    return modelo.eliminar()

def obtener_publicacion_por_id_controller(id_publicacion):
    modelo = PublicacionModel()
    return modelo.obtener_publicacion_por_id(id_publicacion)

def actualizar_publicacion_controller(id_publicacion, data):
    data_form = data.to_dict()
    modelo = PublicacionModel()
    return modelo.actualizar_publicacion(id_publicacion, data_form)