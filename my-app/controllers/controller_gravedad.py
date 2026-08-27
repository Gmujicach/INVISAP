from models.model_gravedad import GravedadObraModel
from services.bitacora_service import BitacoraService
from flask import session


def _calcular_nivel_gravedad(criticidad):
    try:
        v = int(float(criticidad))
    except (TypeError, ValueError):
        return None
    if v <= 50:
        return "Bajo"
    return "Alto"


def registrar_gravedad_controller(datos):
    """
    Recibe los datos del frontend (vía Fetch).
    Instancia el modelo POO, el cual ejecutará las validaciones automáticamente en sus setters.
    El nivel de gravedad se calcula automáticamente según la criticidad:
      - 0 a 50 => Bajo
      - 51 a 100 => Alto
    """
    try:
        nivel_gravedad = _calcular_nivel_gravedad(datos.get('criticidad'))
        if not nivel_gravedad:
            return {"success": False, "message": "Debe ingresar una criticidad válida (0 a 100)."}

        modelo = GravedadObraModel(
            nivel_gravedad=nivel_gravedad,
            criticidad=datos.get('criticidad'),
            estado=int(datos.get('estado', 1))
        )

        resultado = modelo.registrar_gravedad()

        if resultado:
            BitacoraService.registrar_accion(
                session, 'Gravedad', 'CREAR',
                f'Registró nivel de gravedad {nivel_gravedad} (criticidad {datos.get("criticidad")})'
            )
            return {"success": True, "message": "Nivel de gravedad registrado exitosamente."}
        else:
            return {"success": False, "message": "No se pudo registrar la gravedad en la base de datos."}

    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        print(f"Error crítico en registrar_gravedad_controller: {e}")
        return {"success": False, "message": "Error interno del servidor al procesar la solicitud."}

def listar_gravedades_controller():
    """
    Trae únicamente los registros activos, cumpliendo con la regla de 
    trazabilidad y omitiendo los eliminados lógicamente (estado = 0).
    """
    modelo = GravedadObraModel()
    return modelo.consultar_activos()

def obtener_gravedad_controller(id_gravedad):
    """
    Trae los datos de una gravedad específica para llenar el modal de edición.
    """
    modelo = GravedadObraModel()
    return modelo.obtener_gravedad_por_id(id_gravedad)

def actualizar_gravedad_controller(id_gravedad, datos):
    """
    Actualiza los datos pasando nuevamente por la validación POO.
    El nivel de gravedad se calcula automáticamente según la criticidad.
    """
    try:
        nivel_gravedad = _calcular_nivel_gravedad(datos.get('criticidad'))
        if not nivel_gravedad:
            return {"success": False, "message": "Debe ingresar una criticidad válida (0 a 100)."}

        modelo = GravedadObraModel(
            id_gravedad=id_gravedad,
            nivel_gravedad=nivel_gravedad,
            criticidad=datos.get('criticidad'),
            estado=int(datos.get('estado', 1))
        )
        resultado = modelo.actualizar_gravedad()

        if resultado:
            BitacoraService.registrar_accion(
                session, 'Gravedad', 'EDITAR',
                f'Actualizó el nivel de gravedad ID: {id_gravedad} a {nivel_gravedad}'
            )
            return {"success": True, "message": "Registro actualizado correctamente."}
        else:
            return {"success": False, "message": "No se realizaron cambios."}

    except ValueError as ve:
        return {"success": False, "message": str(ve)}

def eliminar_gravedad_controller(id_gravedad):
    """
    Ejecuta el BORRADO LÓGICO exigido por el Prof. Escalona y Cadenas.
    """
    try:
        modelo = GravedadObraModel(id_gravedad=id_gravedad)
        resultado = modelo.eliminar_gravedad() # Este método hace un UPDATE estado = 0
        
        if resultado:
            BitacoraService.registrar_accion(
                session, 'Gravedad', 'ELIMINAR',
                f'Eliminó el nivel de gravedad ID: {id_gravedad}'
            )
            return {"success": True, "message": "Registro eliminado lógicamente del sistema."}
        else:
            return {"success": False, "message": "Error al intentar eliminar el registro."}
    except Exception as e:
        print(f"Error en eliminar_gravedad_controller: {e}")
        return {"success": False, "message": "Error interno del servidor."}

def validar_existencia_controller(id_gravedad):
    """
    Validación de existencia en tiempo real.
    Llamado vía AJAX (change) para verificar si un registro sigue activo.
    """
    modelo = GravedadObraModel()
    existe = modelo.validar_existencia(id_gravedad)
    return {"activo": existe}
