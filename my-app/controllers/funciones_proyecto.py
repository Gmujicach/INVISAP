from models.model_proyecto import ProyectoModel
from services.bitacora_service import BitacoraService
from flask import request

# --- Validación interna avanzada ---
def _validar_input(datos, es_actualizacion=False):
   
    if not isinstance(datos, dict):
        return False
    
    # Validar campo obligatorio (Codigo_p)
    codigo = datos.get('Codigo_p')
    if not codigo or not str(codigo).strip():
        return False
        
   
    if len(str(codigo).strip()) < 3 or len(str(codigo).strip()) > 20:
        return False
        
    return True



def registrar_proyecto_controller(datos, session_flask):
  
    if not _validar_input(datos):
        return False

    modelo = ProyectoModel()
    resultado = modelo.registrar_proyecto(datos)
    
    if resultado:
        codigo_proy = datos.get('Codigo_p')
        BitacoraService.registrar_accion(
            session_flask, 'Proyectos', 'CREAR',
            f'Registró un nuevo proyecto con código: {codigo_proy}'
        )
    return resultado

def listar_proyectos_controller(session_flask):
    modelo = ProyectoModel()
    proyectos = modelo.obtener_proyectos()
    contadores = modelo.obtener_contadores_proyectos()
    
    if session_flask.get('ignorar_proximo_ver'):
        session_flask.pop('ignorar_proximo_ver', None)
        return proyectos, contadores

    BitacoraService.registrar_accion(
        session_flask, 'Proyectos', 'VER',
        'Accedió al módulo de Gestión de Proyectos'
    )
    
    return proyectos, contadores

def actualizar_proyecto_controller(codigo_proyecto_actual, datos, session_flask):
    # Validación de entrada antes de proceder
    if not codigo_proyecto_actual or not _validar_input(datos, es_actualizacion=True):
        return False
        
    modelo = ProyectoModel()
    resultado = modelo.actualizar_proyecto(codigo_proyecto_actual, datos)
    
    if resultado:
        codigo_nuevo = datos.get('Codigo_p', codigo_proyecto_actual)
        BitacoraService.registrar_accion(
            session_flask, 'Proyectos', 'EDITAR',
            f'Modificó el proyecto. Código anterior: {codigo_proyecto_actual} -> Nuevo: {codigo_nuevo}'
        )
        return True
        
    return False

def eliminar_proyecto_controller(codigo_proyecto, session_flask):

    if not codigo_proyecto or not str(codigo_proyecto).strip():
        return False
        
    modelo = ProyectoModel()
    resultado = modelo.eliminar_proyecto(codigo_proyecto)
    
    if resultado:
        BitacoraService.registrar_accion(
            session_flask, 'Proyectos', 'ELIMINAR',
            f'Eliminó permanentemente el proyecto con código: {codigo_proyecto}'
        )
    return resultado