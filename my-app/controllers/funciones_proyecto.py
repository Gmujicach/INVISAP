from models.model_proyecto import ProyectoModel
from services.bitacora_service import BitacoraService

def registrar_proyecto_controller(datos):
    modelo = ProyectoModel()
    return modelo.registrar_proyecto(datos)

def listar_proyectos_controller():
    modelo = ProyectoModel()
    
    # 1. Obtenemos la lista de proyectos como ya lo hacías
    proyectos = modelo.obtener_proyectos()
    
    # 2. Obtenemos el diccionario con todos los contadores calculados
    contadores = modelo.obtener_contadores_proyectos()
    
    # 3. Retornamos ambos valores separados por una coma (una tupla)
    return proyectos, contadores