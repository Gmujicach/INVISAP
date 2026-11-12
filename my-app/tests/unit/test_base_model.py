from unittest.mock import Mock, patch

from models.base_model import BaseModel


def test_limpia_texto_no_confiable_y_respeta_limite():
    assert BaseModel._limpiar_texto('  <b>O\'Brien</b>  ') == 'bOBrien/b'
    assert BaseModel._limpiar_texto('abcdef', max_len=3) == 'abc'
    assert BaseModel._limpiar_texto(None) == ''


def test_ejecuta_sql_y_devuelve_recursos_abiertos():
    conexion = Mock()
    cursor = conexion.cursor.return_value

    with patch.object(BaseModel, 'obtener_conexion', return_value=conexion):
        resultado_cursor, resultado_conexion, error = BaseModel._ejecutar_sql(
            'SELECT 1',
            (1,),
        )

    assert resultado_cursor is cursor
    assert resultado_conexion is conexion
    assert error is None
    cursor.execute.assert_called_once_with('SELECT 1', (1,))


def test_ejecutar_sql_retorna_error_y_revierte_transaccion():
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.execute.side_effect = RuntimeError('fallo controlado')

    with patch.object(BaseModel, 'obtener_conexion', return_value=conexion):
        resultado_cursor, resultado_conexion, error = BaseModel._ejecutar_sql(
            'UPDATE registro',
        )

    assert resultado_cursor is None
    assert resultado_conexion is None
    assert isinstance(error, RuntimeError)
    conexion.rollback.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_cerrar_recursos_cierra_cursor_y_conexion():
    cursor = Mock()
    conexion = Mock()

    BaseModel._cerrar_recursos(cursor, conexion)

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_ejecutar_sql_sin_conexion_devuelve_resultado_vacio():
    with patch.object(BaseModel, 'obtener_conexion', return_value=None):
        resultado = BaseModel._ejecutar_sql('SELECT 1')

    assert resultado == (None, None, None)
