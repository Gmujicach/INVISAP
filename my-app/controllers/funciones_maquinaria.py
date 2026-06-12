from models.model_maquinaria import MaquinariaModel

def registrar_maquinaria_controller(datos):
    modelo = MaquinariaModel()
    return modelo.registrar_maquinaria(datos.get('nombre_maquinaria'))

def listar_maquinarias_controller():
    modelo = MaquinariaModel()
    return modelo.obtener_maquinarias()