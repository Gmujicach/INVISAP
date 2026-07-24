"""
notificacion_vencimiento_service — Verifica obras cuya fecha de culminación
(fecha_fin) está próxima y genera notificaciones de alerta para los roles
responsables.

La cercanía se evalúa respecto a la fecha actual (ventana configurable en días).
Se usa típicamente en una tarea programada (cron) o al iniciar la app.
"""
from datetime import date, datetime

from models.model_obra import ObraModel
from models.model_notificacion import notificar_a_roles

ROLES_OBRA = ['Super Usuario', 'Administrador', 'Gerente', 'Inspector', 'Proyectista']


def _a_fecha(valor):
    """Convierte date/datetime/str a datetime.date o None."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor)[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def obras_por_vencer(dias_ventana: int = 7) -> list:
    """
    Devuelve las obras activas cuya fecha_fin está entre hoy y hoy+dias_ventana.
    """
    try:
        obras = ObraModel().obtener_todas()
    except Exception as e:
        print(f"[vencimiento] Error al obtener obras: {e}")
        return []

    hoy = date.today()
    resultado = []
    for obra in obras or []:
        if int(obra.get('estado', 1)) != 1:
            continue
        ffin = _a_fecha(obra.get('fecha_fin'))
        if ffin is None:
            continue
        delta = (ffin - hoy).days
        if 0 <= delta <= dias_ventana:
            resultado.append({'obra': obra, 'dias': delta, 'fecha_fin': ffin})
    return resultado


def notificar_obras_por_vencer(dias_ventana: int = 7, roles=None) -> int:
    """
    Genera una notificación de cercanía para cada obra próxima a culminar.
    Devuelve la cantidad de notificaciones creadas.
    """
    roles = roles or ROLES_OBRA
    creadas = 0
    for item in obras_por_vencer(dias_ventana):
        obra = item['obra']
        dias = item['dias']
        titulo = obra.get('titulo_obra') or f"Obra #{obra.get('id_obra')}"
        if dias == 0:
            mensaje = f"¡La obra '{titulo}' culmina hoy ({item['fecha_fin']})!"
        else:
            mensaje = f"La obra '{titulo}' culmina en {dias} día(s) ({item['fecha_fin']})."
        try:
            ok = notificar_a_roles(
                roles, 'Obras',
                'Fecha de culminación próxima',
                mensaje,
                enlace='/gestionar-obras',
                creado_por='Sistema'
            )
            if ok is not False:
                creadas += 1
        except Exception as e:
            print(f"[vencimiento] Error al notificar obra: {e}")
    return creadas
