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
    ACCIONES_VALIDAS = {'CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'LOGIN', 'LOGOUT', 'ACCESO_DENEGADO'}

    # Módulos válidos del sistema
    MODULOS_VALIDOS = {
        'Solicitudes', 'Usuarios', 'Empleados', 'Proyectos',
        'Contrataciones', 'Empresas', 'Obras', 'Publicaciones', 'Maquinaria',
        'Inspecciones', 'Gerencias', 'Respaldos', 'Bitacora', 'Login'
    }

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
            return modelo.registrar(
                usuario=nombre_usuario,
                id_usuario=id_usuario,
                modulo=modulo,
                accion=accion,
                descripcion=descripcion
            )

        except Exception as e:
            # Silenciosamente registrar el error sin lanzarlo al caller
            print(f"[BitacoraService] Error al registrar accion: {e}")
            return False
