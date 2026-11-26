"""Pruebas unitarias del modulo de Notificaciones.

Cubre el modelo NotificacionModel y las funciones auxiliares de notificacion,
validando SQL parametrizado, validacion de entrada y comportamiento sin BD.
"""
from unittest.mock import Mock, patch

from models.model_notificacion import NotificacionModel, notificar, notificar_a_rol, notificar_a_roles


def test_crear_rechaza_titulo_vacio():
    # INICIO DE MOCK: Parchear _sql_crear para rastrear llamadas
    with patch.object(NotificacionModel, '_sql_crear') as sql_crear:
        # INICIO DE ASERCIÓN: crear con titulo vacio retorna False sin SQL
        assert NotificacionModel().crear(1, 'General', '   ', 'mensaje') is False
        sql_crear.assert_not_called()
    # FIN DE ASERCIÓN


def test_crear_trunca_campos_y_llama_sql():
    # INICIO DE MOCK: Parchear _sql_crear para devolver True
    with patch.object(NotificacionModel, '_sql_crear', return_value=True) as sql_crear:
        # INICIO DE ASERCIÓN: crear con datos validos trunca y delega
        ok = NotificacionModel().crear(5, 'ModuloLargo' * 10, 'T' * 200, 'M' * 300, enlace='E' * 300, creado_por='P' * 100)
        assert ok is True
        args = sql_crear.call_args.args
        assert args[1] == ('ModuloLargo' * 10)[:30]
        assert args[2] == ('T' * 200)[:120]
        assert args[3] == ('M' * 300)[:255]
    # FIN DE ASERCIÓN


def test_listar_delega_a_sql_listar():
    # INICIO DE MOCK: Parchear _sql_listar
    with patch.object(NotificacionModel, '_sql_listar', return_value=[{'id_notificacion': 1}]) as sql_listar:
        # INICIO DE ASERCIÓN: listar retorna resultado de _sql_listar
        resultado = NotificacionModel().listar(7, limit=5)
        assert resultado == [{'id_notificacion': 1}]
        sql_listar.assert_called_once_with(7, 5)
    # FIN DE ASERCIÓN


def test_contar_no_leidas_maneja_error_de_tipo():
    # INICIO DE ASERCIÓN: contar_no_leidas con valor invalido retorna 0
    assert NotificacionModel().contar_no_leidas('abc') == 0
    # FIN DE ASERCIÓN


def test_marcar_leida_delega():
    # INICIO DE MOCK: Parchear _sql_marcar_leida
    with patch.object(NotificacionModel, '_sql_marcar_leida', return_value=True) as sql:
        # INICIO DE ASERCIÓN: marcar_leida delega y retorna True
        assert NotificacionModel().marcar_leida(3, 9) is True
        sql.assert_called_once_with(3, 9)
    # FIN DE ASERCIÓN


def test_eliminar_delega():
    # INICIO DE MOCK: Parchear _sql_eliminar
    with patch.object(NotificacionModel, '_sql_eliminar', return_value=False) as sql:
        # INICIO DE ASERCIÓN: eliminar delega y retorna False
        assert NotificacionModel().eliminar(3, 9) is False
        sql.assert_called_once_with(3, 9)
    # FIN DE ASERCIÓN


def test_notificar_funcion_auxiliar():
    # INICIO DE MOCK: Parchear crear del modelo
    with patch.object(NotificacionModel, 'crear', return_value=True) as crear:
        # INICIO DE ASERCIÓN: notificar instancia modelo y llama crear
        assert notificar(1, 'Mod', 'Tit', 'Msg') is True
        crear.assert_called_once()
    # FIN DE ASERCIÓN


def test_notificar_a_rol_itera_ids():
    # INICIO DE MOCK: Parchear ids_por_rol y crear
    with patch.object(NotificacionModel, 'ids_por_rol', return_value=[1, 2]) as ids:
        with patch.object(NotificacionModel, 'crear', return_value=True) as crear:
            # INICIO DE ASERCIÓN: notificar_a_rol crea por cada id
            notificar_a_rol('admin', 'Mod', 'Tit', 'Msg')
            assert crear.call_count == 2
            ids.assert_called_once_with('admin')
    # FIN DE ASERCIÓN


def test_notificar_a_roles_excluye_autor():
    # INICIO DE MOCK: Parchear ids_por_rol y crear
    with patch.object(NotificacionModel, 'ids_por_rol', return_value=[1, 2, 3]) as ids:
        with patch.object(NotificacionModel, 'crear', return_value=True) as crear:
            # INICIO DE ASERCIÓN: excluir_id omite al usuario indicado
            notificar_a_roles(['admin'], 'Mod', 'Tit', 'Msg', excluir_id=2)
            assert crear.call_count == 2
    # FIN DE ASERCIÓN


def test_sql_listar_retorna_vacio_sin_conexion():
    # INICIO DE MOCK: Parchear obtener_conexion para devolver None
    with patch.object(NotificacionModel, 'obtener_conexion_seguridad', return_value=None):
        # INICIO DE ASERCIÓN: _sql_listar retorna lista vacia sin conexion
        assert NotificacionModel()._sql_listar(1) == []
    # FIN DE ASERCIÓN


def test_sql_contar_retorna_cero_sin_conexion():
    # INICIO DE MOCK: Parchear obtener_conexion para devolver None
    with patch.object(NotificacionModel, 'obtener_conexion_seguridad', return_value=None):
        # INICIO DE ASERCIÓN: _sql_contar retorna 0 sin conexion
        assert NotificacionModel()._sql_contar_no_leidas(1) == 0
    # FIN DE ASERCIÓN


def test_sql_crear_retorna_false_sin_conexion():
    # INICIO DE MOCK: Parchear obtener_conexion para devolver None
    with patch.object(NotificacionModel, 'obtener_conexion_seguridad', return_value=None):
        # INICIO DE ASERCIÓN: _sql_crear retorna False sin conexion
        assert NotificacionModel()._sql_crear(1, 'M', 'T', 'Msg', None, None) is False
    # FIN DE ASERCIÓN
