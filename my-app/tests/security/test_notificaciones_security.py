"""Pruebas de seguridad del modulo de Notificaciones.

Valida que las operaciones esten filtradas por usuario y que no se inyecten
SQL ni se expongan datos de otros usuarios.
"""
from unittest.mock import Mock, patch

from controllers.controller_notificacion import _id_usuario_actual


def test_id_usuario_actual_retorna_cero_sin_sesion():
    # INICIO DE MOCK: Parchear session vacia
    with patch('controllers.controller_notificacion.session', {}):
        # INICIO DE ASERCIÓN: sin id en session retorna 0
        assert _id_usuario_actual() == 0
    # FIN DE ASERCIÓN


def test_id_usuario_actual_convierte_a_entero():
    # INICIO DE MOCK: Parchear session con id string
    with patch('controllers.controller_notificacion.session', {'id': '42'}):
        # INICIO DE ASERCIÓN: convierte id string a int
        assert _id_usuario_actual() == 42
    # FIN DE ASERCIÓN


def test_marcar_leida_filtra_por_usuario_en_sql():
    # INICIO DE MOCK: Crear conexion y cursor simulados
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.rowcount = 1
    # INICIO DE MOCK: Parchear obtener_conexion_seguridad
    with patch('models.model_notificacion.NotificacionModel.obtener_conexion_seguridad', return_value=conexion):
        # INICIO DE ASERCIÓN: marcar_leida ejecuta WHERE con id_usuario
        modelo = __import__('models.model_notificacion', fromlist=['NotificacionModel']).NotificacionModel()
        ok = modelo.marcar_leida(10, 7)
        assert ok is True
        sql = cursor.execute.call_args.args[0]
        assert 'usuarios_id_usuarios = %s' in sql
    # FIN DE ASERCIÓN
