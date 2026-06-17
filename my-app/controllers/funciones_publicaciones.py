from models.model_publicaciones import PublicacionModel

def listar_publicaciones_controller():
    modelo = PublicacionModel()
    return modelo.obtener_todas_las_publicaciones()

def registrar_publicacion_controller(data):
    # Convertimos ImmutableMultiDict a dict para manejar el valor de evidencias
    data_form = data.to_dict()
    # Si el valor viene vacío (opción por defecto del select), lo guardamos como None
    if not data_form.get('evidencias'):
        data_form['evidencias'] = None
        
    modelo = PublicacionModel()
    return modelo.registrar_publicacion(data_form)

def eliminar_publicacion_controller(id_publicacion):
    modelo = PublicacionModel()
    return modelo.eliminar_publicacion(id_publicacion)

def obtener_publicacion_por_id_controller(id_publicacion):
    modelo = PublicacionModel()
    return modelo.obtener_publicacion_por_id(id_publicacion)

def actualizar_publicacion_controller(id_publicacion, data):
    data_form = data.to_dict()
    if not data_form.get('evidencias'):
        data_form['evidencias'] = None
        
    modelo = PublicacionModel()
    return modelo.actualizar_publicacion(id_publicacion, data_form)