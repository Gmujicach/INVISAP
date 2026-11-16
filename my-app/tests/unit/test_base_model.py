from unittest.mock import MagicMock

import pytest

from models.base_model import BaseModel


@pytest.mark.parametrize(
    ('value', 'max_len', 'expected'),
    [
        ('  <texto>;  ', 20, 'texto'),
        (123, 2, '12'),
        ('abcdef', 3, 'abc'),
    ],
)
def test_limpiar_texto_normaliza_y_limita_entrada(value, max_len, expected):
    assert BaseModel._limpiar_texto(value, max_len=max_len) == expected


def test_ejecutar_sql_retorna_cursor_y_conexion_en_exito(monkeypatch):
    connection = MagicMock()
    cursor = connection.cursor.return_value
    monkeypatch.setattr(BaseModel, 'obtener_conexion', staticmethod(lambda: connection))

    resultado = BaseModel._ejecutar_sql('SELECT %s', (7,))

    assert resultado == (cursor, connection, None)
    cursor.execute.assert_called_once_with('SELECT %s', (7,))
    cursor.close.assert_not_called()
    connection.close.assert_not_called()


def test_ejecutar_sql_devuelve_sin_resultados_si_no_hay_conexion(monkeypatch):
    monkeypatch.setattr(BaseModel, 'obtener_conexion', staticmethod(lambda: None))

    assert BaseModel._ejecutar_sql('SELECT 1') == (None, None, None)


def test_ejecutar_sql_revierte_y_cierra_recursos_si_falla(monkeypatch):
    connection = MagicMock()
    cursor = connection.cursor.return_value
    error = RuntimeError('fallo SQL')
    cursor.execute.side_effect = error
    monkeypatch.setattr(BaseModel, 'obtener_conexion', staticmethod(lambda: connection))

    cursor_resultado, conexion_resultado, error_resultado = BaseModel._ejecutar_sql(
        'UPDATE tabla SET valor = %s',
        (1,),
    )

    assert (cursor_resultado, conexion_resultado, error_resultado) == (None, None, error)
    connection.rollback.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_cerrar_recursos_cierra_cursor_y_conexion():
    cursor = MagicMock()
    connection = MagicMock()

    BaseModel._cerrar_recursos(cursor, connection)

    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_cerrar_recursos_ignora_recursos_ausentes_o_cierre_fallido():
    cursor = MagicMock()
    cursor.close.side_effect = RuntimeError('cursor cerrado')
    connection = MagicMock()
    connection.close.side_effect = RuntimeError('conexion cerrada')

    BaseModel._cerrar_recursos(cursor, connection)
    BaseModel._cerrar_recursos(None, None)

    cursor.close.assert_called_once()
    connection.close.assert_called_once()
