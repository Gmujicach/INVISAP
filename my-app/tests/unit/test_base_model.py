from unittest.mock import Mock, patch

from models.base_model import BaseModel


def test_limpia_texto_no_confiable_y_respeta_limite():
    # INICIO DE ASERCIÓN: Verificar limpieza de texto y límite de longitud
    assert BaseModel._limpiar_texto('  <b>O\'Brien</b>  ') == 'bOBrien/b'
    assert BaseModel._limpiar_texto('abcdef', max_len=3) == 'abc'
    assert BaseModel._limpiar_texto(None) == ''
    # FIN DE ASERCIÓN


def test_ejecuta_sql_y_devuelve_recursos_abiertos():
    # INICIO DE MOCK: Crear conexión y cursor simulados
    conexion = Mock()
    cursor = conexion.cursor.return_value

    # INICIO DE MOCK: Parchear obtener_conexion para devolver conexión simulada
    with patch.object(BaseModel, 'obtener_conexion', return_value=conexion):
        # INICIO DE MOCK: Llamar _ejecutar_sql con conexión parcheada
        resultado_cursor, resultado_conexion, error = BaseModel._ejecutar_sql(
            'SELECT 1',
            (1,),
        )

    # INICIO DE ASERCIÓN: Verificar resultados y llamada execute
    assert resultado_cursor is cursor
    assert resultado_conexion is conexion
    assert error is None
    cursor.execute.assert_called_once_with('SELECT 1', (1,))
    # FIN DE ASERCIÓN


def test_ejecutar_sql_retorna_error_y_revierte_transaccion():
    # INICIO DE MOCK: Crear conexión y cursor simulados con error
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.execute.side_effect = RuntimeError('fallo controlado')

    # INICIO DE MOCK: Parchear obtener_conexion para devolver conexión simulada
    with patch.object(BaseModel, 'obtener_conexion', return_value=conexion):
        # INICIO DE MOCK: Llamar _ejecutar_sql con conexión parcheada
        resultado_cursor, resultado_conexion, error = BaseModel._ejecutar_sql(
            'UPDATE registro',
        )

    # INICIO DE ASERCIÓN: Verificar error y rollback/close llamados
    assert resultado_cursor is None
    assert resultado_conexion is None
    assert isinstance(error, RuntimeError)
    conexion.rollback.assert_called_once()
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()
    # FIN DE ASERCIÓN


def test_cerrar_recursos_cierra_cursor_y_conexion():
    # INICIO DE MOCK: Crear cursor y conexión simulados
    cursor = Mock()
    conexion = Mock()

    # INICIO DE MOCK: Llamar _cerrar_recursos con mocks
    BaseModel._cerrar_recursos(cursor, conexion)

    # INICIO DE ASERCIÓN: Verificar que métodos close se llaman una vez
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()
    # FIN DE ASERCIÓN


def test_ejecutar_sql_sin_conexion_devuelve_resultado_vacio():
    # INICIO DE MOCK: Parchear obtener_conexion para devolver None
    with patch.object(BaseModel, 'obtener_conexion', return_value=None):
        # INICIO DE MOCK: Llamar _ejecutar_sql sin conexión
        resultado = BaseModel._ejecutar_sql('SELECT 1')

    # INICIO DE ASERCIÓN: Verificar resultado vacío
    assert resultado == (None, None, None)
    # FIN DE ASERCIÓN
