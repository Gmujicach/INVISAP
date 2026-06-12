from models.model_proyecto import ProyectoModel

def registrar_proyecto_controller(datos):
    modelo = ProyectoModel()
    return modelo.registrar_proyecto(datos)

def listar_proyectos_controller():
    modelo = ProyectoModel()
    return modelo.obtener_proyectos()