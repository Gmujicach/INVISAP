from models.model_proyecto import ProyectoModel
from services.bitacora_service import BitacoraService
from flask import request

def registrar_proyecto_controller(datos, session_flask):
    modelo = ProyectoModel()
    resultado = modelo.registrar_proyecto(datos)
    
    if resultado:
        codigo_proy = datos.get('Codigo_p', 'Desconocido')
        BitacoraService.registrar_accion(
            session_flask, 'Proyectos', 'CREAR',
            f'Registró un nuevo proyecto con código: {codigo_proy}'
        )
    return resultado

def listar_proyectos_controller(session_flask):
    modelo = ProyectoModel()
    proyectos = modelo.obtener_proyectos()
    contadores = modelo.obtener_contadores_proyectos()
    
    # 🚨 VERIFICACIÓN DE LA BANDERA DE SESIÓN
    # Si la marca existe en la sesión, significa que el usuario viene de actualizar 
    # un proyecto y Flask lo redireccionó aquí. ¡Omitimos el VER!
    if session_flask.get('ignorar_proximo_ver'):
        # Borramos la marca inmediatamente para que la próxima vez que entre normalmente sí registre el VER
        session_flask.pop('ignorar_proximo_ver', None)
        return proyectos, contadores

    # Si entra de manera normal (desde el menú, etc.), registramos el VER sin problemas
    BitacoraService.registrar_accion(
        session_flask, 'Proyectos', 'VER',
        'Accedió al módulo de Gestión de Proyectos'
    )
    
    return proyectos, contadores
def actualizar_proyecto_controller(codigo_proyecto_actual, datos, session_flask):
    """
    Actualiza los datos del proyecto y asegura el registro 'MODIFICAR' en la bitácora
    """
    if not codigo_proyecto_actual:
        codigo_proyecto_actual = datos.get('Codigo_p')
        
    modelo = ProyectoModel()
    resultado = modelo.actualizar_proyecto(codigo_proyecto_actual, datos)
    
    # Si el modelo retorna True (operación exitosa en BD)
    if resultado:
        codigo_nuevo = datos.get('Codigo_p', codigo_proyecto_actual)
        BitacoraService.registrar_accion(
            session_flask, 'Proyectos', 'MODIFICAR',
            f'Modificó el proyecto. Código anterior: {codigo_proyecto_actual} -> Nuevo: {codigo_nuevo}'
        )
        return True
        
    return False

def eliminar_proyecto_controller(codigo_proyecto, session_flask):
    modelo = ProyectoModel()
    resultado = modelo.eliminar_proyecto(codigo_proyecto)
    
    if resultado:
        BitacoraService.registrar_accion(
            session_flask, 'Proyectos', 'ELIMINAR',
            f'Eliminó permanentemente el proyecto con código: {codigo_proyecto}'
        )
    return resultado