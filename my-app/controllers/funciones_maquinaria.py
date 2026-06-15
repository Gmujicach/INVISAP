from models.model_maquinaria import MaquinariaModel

def registrar_maquinaria_controller(datos):
    modelo = MaquinariaModel()
    return modelo.registrar_maquinaria(
        datos.get('nombre_maquinaria'),
        datos.get('tipo_maquinaria')
    )

def listar_maquinarias_controller():
    modelo = MaquinariaModel()
    return modelo.obtener_maquinarias()

def obtener_maquinaria_controller(id_maquinaria):
    modelo = MaquinariaModel()
    return modelo.obtener_maquinaria_por_id(id_maquinaria) # Ahora el método existe en el modelo

def actualizar_maquinaria_controller(id_maquinaria, datos):
    modelo = MaquinariaModel()
    return modelo.actualizar_maquinaria(
        id_maquinaria,
        datos.get('nombre_maquinaria'),
        datos.get('tipo_maquinaria')
    )

def eliminar_maquinaria_controller(id_maquinaria):
    modelo = MaquinariaModel()
    return modelo.eliminar_maquinaria(id_maquinaria)