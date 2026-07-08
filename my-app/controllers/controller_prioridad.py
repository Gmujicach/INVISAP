from models.model_prioridad import PrioridadModel
from services.ia_prioridad_service import calcular_prioridad_con_ia
from services.bitacora_service import BitacoraService
from flask import session
from mysql.connector import Error

def calcular_prioridad_controller(solicitud_id, gravedad_id=None):
    # Obtener descripción de la solicitud (conexión a BD)
    # ... (código de consulta)
    descripcion = obtener_descripcion_solicitud(solicitud_id)
    gravedad_nivel = obtener_nivel_gravedad(gravedad_id) if gravedad_id else None

    resultado_ia = calcular_prioridad_con_ia(descripcion, gravedad_nivel)
    return resultado_ia

def guardar_prioridad_controller(solicitud_id, prioridad, justificacion, usuario):
    modelo = PrioridadModel(
        solicitud_id=solicitud_id,
        rango_prioridad=prioridad,
        justificacion=justificacion,
        responsable=usuario
    )
    # Conexión dinámica y guardado
    resultado = modelo.guardar()
    if resultado:
        BitacoraService.registrar_accion(
            session, 'Prioridad', 'EDITAR',
            f'Asignó prioridad "{prioridad}" a la solicitud ID: {solicitud_id}'
        )
    return resultado