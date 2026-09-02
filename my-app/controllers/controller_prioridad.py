from models.model_prioridad import PrioridadModel
from services.ia_prioridad_service import clasificar_solicitud_ia, calcular_prioridad_con_ia
from services.bitacora_service import BitacoraService
from flask import session
from mysql.connector import Error


def calcular_prioridad_controller(solicitud_id, gravedad_id=None):
    try:
        datos = PrioridadModel.obtener_datos_solicitud(solicitud_id)
        if not datos:
            return {"success": False, "message": "Solicitud no encontrada."}

        gravedad_nivel = datos.get('nivel_gravedad')
        if gravedad_id:
            gravedad_registro = PrioridadModel.obtener_gravedad_obra(gravedad_id)
            if gravedad_registro:
                gravedad_nivel = gravedad_registro.get('nivel_gravedad')

        resultado_ia = clasificar_solicitud_ia(
            datos.get('descripcion') or '',
            gravedad_nivel,
            datos.get('color_semaforo'),
            datos.get('tipo_solicitante')
        )

        calculo = PrioridadModel._calcular_puntaje_ponderado(
            datos.get('tipo_solicitante'),
            resultado_ia.get('gravedad_sugerida'),
            resultado_ia.get('tipo_obra')
        )

        return {
            "success": True,
            "data": {
                "tipo_obra": resultado_ia.get('tipo_obra'),
                "gravedad_sugerida": resultado_ia.get('gravedad_sugerida'),
                "justificacion": resultado_ia.get('justificacion'),
                "origen": resultado_ia.get('origen'),
                "calculo": calculo,
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error al calcular prioridad: {str(e)}"}


def guardar_prioridad_controller(solicitud_id, prioridad, justificacion, usuario):
    try:
        modelo = PrioridadModel(
            solicitud_id=solicitud_id,
            rango_prioridad=prioridad,
            justificacion=justificacion,
            responsable=usuario
        )
        resultado = modelo.registrar()
        if resultado:
            BitacoraService.registrar_accion(
                session, 'Prioridad', 'REGISTRAR',
                f'Asignó prioridad "{prioridad}" a la solicitud ID: {solicitud_id}'
            )
            return {"success": True, "id": resultado}
        return {"success": False, "message": "No se pudo registrar la prioridad."}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        return {"success": False, "message": f"Error inesperado: {str(e)}"}


def clasificar_nueva_solicitud_controller(id_solicitud):
    try:
        responsable = session.get('name_surname', 'Sistema')
        resultado = PrioridadModel.clasificar_nueva_solicitud(id_solicitud, responsable)
        if resultado.get('success'):
            BitacoraService.registrar_accion(
                session, 'Prioridad', 'CLASIFICAR_IA',
                f'IA clasificó solicitud ID {id_solicitud} → prioridad {resultado["data"]["rango"]} '
                f'({resultado["data"]["tipo_obra"]}, {resultado["data"]["gravedad_sugerida"]})'
            )
        return resultado
    except Exception as e:
        return {"success": False, "message": f"Error al clasificar: {str(e)}"}


def procesar_pendientes_batch_controller():
    try:
        responsable = session.get('name_surname', 'Sistema')
        resultado = PrioridadModel.procesar_solicitudes_pendientes_batch(responsable)
        if resultado.get('success'):
            BitacoraService.registrar_accion(
                session, 'Prioridad', 'CLASIFICAR_BATCH',
                f'Procesamiento masivo: {resultado["procesadas"]} solicitudes clasificadas, '
                f'{resultado["errores"]} errores.'
            )
        return resultado
    except Exception as e:
        return {"success": False, "message": f"Error en procesamiento batch: {str(e)}"}


def listar_prioridades_controller(page=1, per_page=10):
    try:
        filas, total = PrioridadModel.listar_priorizadas(page=page, per_page=per_page)
        return {
            "success": True,
            "data": filas,
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        return {"success": False, "message": f"Error al listar: {str(e)}"}


def obtener_prioridad_controller(id_prioridad):
    try:
        registro = PrioridadModel.obtener_por_id(id_prioridad)
        if registro:
            return {"success": True, "data": registro}
        return {"success": False, "message": "Prioridad no encontrada."}
    except Exception as e:
        return {"success": False, "message": f"Error al obtener: {str(e)}"}


def actualizar_prioridad_controller(id_prioridad, rango, justificacion, estado):
    try:
        modelo = PrioridadModel(
            id_prioridad=id_prioridad,
            rango_prioridad=rango,
            justificacion=justificacion,
            estado=estado
        )
        if modelo.actualizar():
            BitacoraService.registrar_accion(
                session, 'Prioridad', 'EDITAR',
                f'Actualizó prioridad ID: {id_prioridad} a rango {rango}'
            )
            return {"success": True, "message": "Prioridad actualizada."}
        return {"success": False, "message": "No se realizaron cambios."}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        return {"success": False, "message": f"Error al actualizar: {str(e)}"}


def eliminar_prioridad_controller(id_prioridad):
    try:
        modelo = PrioridadModel(id_prioridad=id_prioridad)
        if modelo.eliminar_logico():
            BitacoraService.registrar_accion(
                session, 'Prioridad', 'ELIMINAR',
                f'Desactivó (borrado lógico) prioridad ID: {id_prioridad}'
            )
            return {"success": True, "message": "Prioridad desactivada."}
        return {"success": False, "message": "No se pudo desactivar."}
    except Exception as e:
        return {"success": False, "message": f"Error al eliminar: {str(e)}"}
