from models.model_publicaciones import PublicacionModel

def listar_publicaciones_controller():
    modelo = PublicacionModel()
    return modelo.obtener_todas_las_publicaciones()

def registrar_publicacion_controller(data):
    modelo = PublicacionModel()
    # Aquí podrías agregar validaciones de datos antes de enviar al modelo
    return modelo.registrar_publicacion(data)

def eliminar_publicacion_controller(id_publicacion):
    modelo = PublicacionModel()
    return modelo.eliminar_publicacion(id_publicacion)

def obtener_publicacion_por_id_controller(id_publicacion):
    modelo = PublicacionModel()
    return modelo.obtener_publicacion_por_id(id_publicacion)