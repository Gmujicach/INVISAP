from models.model_maquinaria import MaquinariaModel
from services.bitacora_service import BitacoraService
from flask import session

def registrar_maquinaria_controller(datos):
    modelo = MaquinariaModel()
    resultado = modelo.registrar(
        datos.get('nombre_maquinaria'),
        datos.get('tipo_maquinaria')
    )
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Maquinaria', 'CREAR',
            f'Registró la maquinaria: {datos.get("nombre_maquinaria")}'
        )
    return resultado

def listar_maquinarias_controller(page=1, per_page=10):
    modelo = MaquinariaModel()
    return modelo.obtener_todos(page, per_page)

def contar_maquinarias_controller():
    modelo = MaquinariaModel()
    return modelo.contar()

def obtener_maquinaria_controller(id_maquinaria):
    modelo = MaquinariaModel()
    return modelo.obtener_por_id(id_maquinaria)

def listar_maquinarias_eliminadas_controller():
    modelo = MaquinariaModel()
    return modelo.obtener_eliminadas()

def restaurar_maquinaria_controller(id_maquinaria):
    modelo = MaquinariaModel()
    return modelo.restaurar(id_maquinaria)

def actualizar_maquinaria_controller(id_maquinaria, datos):
    modelo = MaquinariaModel()
    resultado = modelo.actualizar(
        id_maquinaria,
        datos.get('nombre_maquinaria'),
        datos.get('tipo_maquinaria')
    )
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Maquinaria', 'EDITAR',
            f'Modificó la maquinaria ID: {id_maquinaria}'
        )
    return resultado

def eliminar_maquinaria_controller(id_maquinaria):
    modelo = MaquinariaModel()
    resultado = modelo.eliminar(id_maquinaria)
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Maquinaria', 'ELIMINAR',
            f'Eliminó la maquinaria ID: {id_maquinaria}'
        )
    return resultado