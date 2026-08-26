"""
BitacoraService — Servicio centralizado de auditoría.

Puede ser importado y usado desde cualquier módulo del sistema:
    from services.bitacora_service import BitacoraService
    BitacoraService.registrar_accion(session, 'Solicitudes', 'CREAR', 'Detalle...')
"""
import re
from datetime import datetime


class BitacoraService:
    """
    Servicio estático de auditoría. Registra acciones de usuarios en la bitácora.
    No lanza excepciones hacia arriba; captura y loggea silenciosamente para no
    interrumpir el flujo principal de la aplicación.
    """

    # Acciones válidas del sistema
    ACCIONES_VALIDAS = {'CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'LOGIN', 'LOGOUT', 'ACCESO_DENEGADO', 'GENERAR_REPORTE'}

    # Módulos válidos del sistema
    MODULOS_VALIDOS = {
        'Solicitudes', 'Usuarios', 'Empleados', 'Proyectos',
        'Contrataciones', 'Empresas', 'Obras', 'Publicaciones', 'Maquinaria',
        'Inspecciones', 'Gerencias', 'Respaldos', 'Bitacora', 'Login',
        'Reportes', 'Gravedad', 'Prioridad', 'Evidencias', 'Solicitantes',
        'Informes de Avance', 'Roles y Permisos'
    }

    # Mapeo de blueprints a nombre legible de módulo
    _BLUEPRINT_A_MODULO = {
        'login_bp': 'Login',
        'respaldo_bp': 'Respaldos',
        'user_bp': 'Usuarios',
        'empleado_bp': 'Empleados',
        'empresa_bp': 'Empresas',
        'evidencia_bp': 'Evidencias',
        'reporte_excel_bp': 'Reportes',
        'reporte_pdf_bp': 'Reportes',
        'reporte_estadistico_bp': 'Reportes',
        'informe_avance_bp': 'Informes de Avance',
        'obra_bp': 'Obras',
        'contrataciones_bp': 'Contrataciones',
        'inspeccion_bp': 'Inspecciones',
        'notificacion_bp': 'Notificaciones',
    }

    # Reglas de ruta -> módulo (home_bp agrupa varios módulos)
    _RUTA_A_MODULO = [
        ('informe', 'Informes de Avance'),
        ('inf_avance', 'Informes de Avance'),
        ('reporte', 'Reportes'),
        ('evidencia', 'Evidencias'),
        ('inspeccion', 'Inspecciones'),
        ('solicitud', 'Solicitudes'),
        ('proyecto', 'Proyectos'),
        ('publicacion', 'Publicaciones'),
        ('contratacion', 'Contrataciones'),
        ('obra', 'Obras'),
        ('empleado', 'Empleados'),
        ('empresa', 'Empresas'),
        ('maquinaria', 'Maquinaria'),
        ('gravedad', 'Gravedad'),
        ('prioridad', 'Prioridad'),
        ('permiso', 'Roles y Permisos'),
        ('seguridad', 'Roles y Permisos'),
        ('rol', 'Roles y Permisos'),
        ('bitacora', 'Bitacora'),
        ('respaldo', 'Respaldos'),
        ('usuario', 'Usuarios'),
        ('/users', 'Usuarios'),
        ('perfil', 'Login'),
        ('manual', 'Principal'),
    ]

    @staticmethod
    def mapear_modulo(endpoint: str, path: str) -> str:
        """
        Convierte un endpoint/ruta en el nombre legible del módulo correspondiente.
        Se usa en la auditoría global para que el campo 'modulo' de la bitácora
        muestre el nombre del módulo y no el identificador interno del blueprint.
        """
        ep = (endpoint or '').lower()
        ruta = (path or '').lower()

        bp = ep.split('.')[0] if '.' in ep else ''
        if bp in BitacoraService._BLUEPRINT_A_MODULO:
            return BitacoraService._BLUEPRINT_A_MODULO[bp]

        for clave, nombre in BitacoraService._RUTA_A_MODULO:
            if clave in ruta:
                return nombre

        if bp == 'home_bp':
            return 'Principal'
        return (ep.split('.')[-1] if ep else ruta) or 'General'

    @staticmethod
    def _validar_texto(texto: str, max_len: int = 100) -> str:
        """Sanitiza un texto eliminando caracteres peligrosos."""
        if not isinstance(texto, str):
            texto = str(texto)
        # Eliminar caracteres peligrosos, dejar solo alfanum, espacios y puntuación básica
        texto = re.sub(r'[<>\'";\\]', '', texto)
        return texto[:max_len].strip()

    @staticmethod
    def registrar_accion(session: dict, modulo: str, accion: str, descripcion: str = '') -> bool:
        """
        Registra una acción de usuario en la bitácora.

        Args:
            session:     Diccionario de sesión Flask con 'nombre' e 'id'.
            modulo:      Nombre del módulo donde ocurrió la acción.
            accion:      Tipo de acción (CREAR, EDITAR, ELIMINAR, VER, LOGIN, LOGOUT).
            descripcion: Detalle adicional opcional (ej. 'Solicitud #12').

        Returns:
            bool: True si se registró correctamente, False en caso de error.
        """
        try:
            from models.model_bitacora import BitacoraModel

            # Extraer datos del usuario de la sesión
            nombre_usuario = BitacoraService._validar_texto(
                session.get('name_surname') or session.get('nombre') or session.get('email_user') or 'Sistema',
                max_len=15
            )
            id_usuario = int(session.get('id', 0)) if session.get('id') else 1

            # Normalizar y validar modulo y accion
            modulo = BitacoraService._validar_texto(modulo, max_len=20)
            accion = accion.upper().strip()

            if accion not in BitacoraService.ACCIONES_VALIDAS:
                accion = 'VER'

            # Si el modulo no está en los válidos, lo truncamos igualmente
            if modulo not in BitacoraService.MODULOS_VALIDOS:
                modulo = BitacoraService._validar_texto(modulo, max_len=20)

            descripcion = BitacoraService._validar_texto(descripcion, max_len=100)

            # Llamar al modelo para insertar el registro
            modelo = BitacoraModel()
            resultado = modelo.registrar(
                usuario=nombre_usuario,
                id_usuario=id_usuario,
                modulo=modulo,
                accion=accion,
                descripcion=descripcion
            )

            # Conectar la bitácora con el sistema de notificaciones:
            # las acciones relevantes (no solo lectura) generan una
            # notificación para los administradores.
            if resultado and accion != 'VER':
                try:
                    from models.model_notificacion import notificar_a_roles
                    accion_amigable = {
                        'CREAR': 'Nuevo registro en',
                        'EDITAR': 'Actualización en',
                        'ELIMINAR': 'Eliminación en',
                        'LOGIN': 'Inicio de sesión en',
                        'LOGOUT': 'Cierre de sesión en',
                        'ACCESO_DENEGADO': 'Acceso denegado en',
                        'GENERAR_REPORTE': 'Reporte generado en'
                    }.get(accion, 'Cambio en')
                    notificar_a_roles(
                        ['Super Usuario', 'Administrador'],
                        modulo,
                        f'{accion_amigable} {modulo}',
                        descripcion or f'Se registró una actividad en {modulo}',
                        creado_por=nombre_usuario,
                        creado_por_id=id_usuario
                    )
                except Exception as e:
                    print(f"[BitacoraService] Error al crear notificación: {e}")

            # Marcar que esta petición ya quedó registrada en la bitácora,
            # para que el hook global de auditoría no la duplique.
            try:
                from flask import g
                g.bitacora_logged = True
            except Exception:
                pass

            return resultado

        except Exception as e:
            # Silenciosamente registrar el error sin lanzarlo al caller
            print(f"[BitacoraService] Error al registrar accion: {e}")
            return False
