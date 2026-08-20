"""
controller_seguridad.py — Controladores para el módulo
"Permisos por Rol" (gestión dinámica de roles y permisos).
Sigue el patrón de controller_gravedad: validación POO + bitácora.
Cada acción audita en la bitácora con módulo 'Roles y Permisos'.
"""
from models.model_seguridad import ModuloModel, RolModel, RolPermisoModel
from services.bitacora_service import BitacoraService
from flask import session

MODULO_BITACORA = 'Roles y Permisos'


# ===================== MÓDULOS =====================
def registrar_modulo_controller(datos):
    try:
        modelo = ModuloModel(
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            url=datos.get('url'),
            tipo=datos.get('tipo', 'CRUD'),
            icono=datos.get('icono'),
            orden=int(datos.get('orden') or 0),
            estado=int(datos.get('estado', 1))
        )
        if modelo.validar_nombre_existente():
            return {"success": False, "message": "Ya existe un módulo con esa clave (nombre)."}
        resultado = modelo.registrar()
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'CREAR',
                f'Registró el módulo: {datos.get("nombre")}')
            return {"success": True, "message": "Módulo registrado exitosamente."}
        return {"success": False, "message": "No se pudo registrar el módulo."}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        print(f"Error en registrar_modulo_controller: {e}")
        return {"success": False, "message": "Error interno del servidor."}


def listar_modulos_controller():
    return ModuloModel().consultar_activos()


def obtener_modulo_controller(id_modulo):
    return ModuloModel(id_modulo=id_modulo).obtener_por_id(id_modulo)


def actualizar_modulo_controller(id_modulo, datos):
    try:
        modelo = ModuloModel(
            id_modulo=id_modulo,
            nombre=datos.get('nombre'),
            descripcion=datos.get('descripcion'),
            url=datos.get('url'),
            tipo=datos.get('tipo', 'CRUD'),
            icono=datos.get('icono'),
            orden=int(datos.get('orden') or 0),
            estado=int(datos.get('estado', 1))
        )
        if modelo.validar_nombre_existente(excluir_id=id_modulo):
            return {"success": False, "message": "Ya existe otro módulo con esa clave (nombre)."}
        resultado = modelo.actualizar()
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'EDITAR',
                f'Actualizó el módulo ID: {id_modulo}')
            return {"success": True, "message": "Módulo actualizado correctamente."}
        return {"success": False, "message": "No se realizaron cambios."}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}


def eliminar_modulo_controller(id_modulo):
    try:
        resultado = ModuloModel(id_modulo=id_modulo).eliminar()
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'ELIMINAR',
                f'Eliminó (lógicamente) el módulo ID: {id_modulo}')
            return {"success": True, "message": "Módulo desactivado del sistema."}
        return {"success": False, "message": "Error al desactivar el módulo."}
    except Exception as e:
        print(f"Error en eliminar_modulo_controller: {e}")
        return {"success": False, "message": "Error interno del servidor."}


# ===================== ROLES =====================
def registrar_rol_controller(datos):
    try:
        nombre = (datos.get('nombre') or '').strip()
        modelo = RolModel(
            nombre=nombre,
            descripcion=datos.get('descripcion'),
            estado=int(datos.get('estado', 1))
        )
        if modelo.validar_nombre_existente():
            return {"success": False, "message": "Ya existe un rol con ese nombre."}
        if nombre.lower() == "super usuario" and modelo.existe_super_usuario_activo():
            return {"success": False, "message": "Ya existe un Super Usuario activo. No se permite crear otro."}
        resultado = modelo.registrar()
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'CREAR',
                f'Registró el rol: {nombre}')
            return {"success": True, "message": "Rol registrado exitosamente."}
        return {"success": False, "message": "No se pudo registrar el rol."}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        print(f"Error en registrar_rol_controller: {e}")
        return {"success": False, "message": "Error interno del servidor."}


def listar_roles_controller():
    return RolModel().consultar_activos()


def obtener_rol_controller(id_rol):
    return RolModel(id_rol=id_rol).obtener_por_id(id_rol)


def actualizar_rol_controller(id_rol, datos):
    try:
        nombre = (datos.get('nombre') or '').strip()
        modelo = RolModel(
            id_rol=id_rol,
            nombre=nombre,
            descripcion=datos.get('descripcion'),
            estado=int(datos.get('estado', 1))
        )
        if modelo.validar_nombre_existente(excluir_id=id_rol):
            return {"success": False, "message": "Ya existe otro rol con ese nombre."}
        if nombre.lower() == "super usuario" and modelo.existe_super_usuario_activo(excluir_id=id_rol):
            return {"success": False, "message": "Ya existe un Super Usuario activo. No se permite asignar este rol a otro."}
        resultado = modelo.actualizar()
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'EDITAR',
                f'Actualizó el rol ID: {id_rol}')
            return {"success": True, "message": "Rol actualizado correctamente."}
        return {"success": False, "message": "No se realizaron cambios."}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}


def eliminar_rol_controller(id_rol):
    try:
        resultado = RolModel(id_rol=id_rol).eliminar()
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'ELIMINAR',
                f'Eliminó (lógicamente) el rol ID: {id_rol}')
            return {"success": True, "message": "Rol desactivado del sistema."}
        return {"success": False, "message": "Error al desactivar el rol."}
    except Exception as e:
        print(f"Error en eliminar_rol_controller: {e}")
        return {"success": False, "message": "Error interno del servidor."}


# ===================== PERMISOS POR ROL =====================
def obtener_permisos_rol_controller(id_rol):
    return RolPermisoModel().obtener_por_rol(id_rol)


def guardar_permisos_controller(id_rol, permisos):
    try:
        id_rol = int(id_rol)
        if not permisos or not isinstance(permisos, list):
            return {"success": False, "message": "No se recibieron permisos."}
        resultado = RolPermisoModel().guardar_permisos(id_rol, permisos)
        if resultado:
            BitacoraService.registrar_accion(
                session, MODULO_BITACORA, 'EDITAR',
                f'Actualizó permisos del rol ID: {id_rol}')
            return {"success": True, "message": "Permisos guardados correctamente."}
        return {"success": False, "message": "Error al guardar los permisos."}
    except Exception as e:
        print(f"Error en guardar_permisos_controller: {e}")
        return {"success": False, "message": "Error interno del servidor."}


def obtener_usuarios_por_rol_controller(id_rol):
    try:
        rol = RolModel(id_rol=id_rol).obtener_por_id(id_rol)
        if not rol:
            return {"success": False, "message": "Rol no encontrado.", "usuarios": []}
        return {
            "success": True,
            "rol": rol.get('nombre'),
            "usuarios": RolModel(nombre=rol.get('nombre')).obtener_usuarios_por_rol()
        }
    except Exception as e:
        print(f"Error en obtener_usuarios_por_rol_controller: {e}")
        return {"success": False, "message": "Error interno del servidor.", "usuarios": []}
