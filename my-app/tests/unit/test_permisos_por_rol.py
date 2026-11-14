import pytest
from unittest.mock import MagicMock, patch

from models.model_seguridad import (
    ModuloModel,
    RolModel,
    RolPermisoModel,
    asegurar_tabla_permisos_usuario,
)


def _mock_database():
    cursor = MagicMock()
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def _connect(monkeypatch, model, connection):
    monkeypatch.setattr(model, 'obtener_conexion_seguridad', lambda: connection)


def test_modulo_rechaza_url_que_no_empieza_con_barra():
    modulo = ModuloModel(nombre='obras', url='obras', tipo='CRUD')

    with pytest.raises(ValueError):
        modulo._validar()


def test_rol_rechaza_nombre_con_caracteres_no_permitidos():
    rol = RolModel(nombre='Admin123')

    with pytest.raises(ValueError):
        rol._validar()


def test_asegurar_tabla_permisos_usuario_confirma_y_limpia_recursos(monkeypatch):
    connection, cursor = _mock_database()
    monkeypatch.setattr(
        'models.model_seguridad._SeguridadDatabase.obtener_conexion_seguridad',
        lambda: connection,
    )

    asegurar_tabla_permisos_usuario()

    statements = [item.args[0] for item in cursor.execute.call_args_list]
    assert len(statements) == 3
    assert 'CREATE TABLE IF NOT EXISTS usuarios_permisos' in statements[0]
    assert 'INSERT INTO modulos' in statements[1]
    assert 'INSERT IGNORE INTO roles_permisos' in statements[2]
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_asegurar_tabla_permisos_usuario_tolera_fallo_de_conexion(monkeypatch):
    monkeypatch.setattr(
        'models.model_seguridad._SeguridadDatabase.obtener_conexion_seguridad',
        lambda: None,
    )
    asegurar_tabla_permisos_usuario()

    connection, cursor = _mock_database()
    cursor.execute.side_effect = RuntimeError('DDL failed')
    monkeypatch.setattr(
        'models.model_seguridad._SeguridadDatabase.obtener_conexion_seguridad',
        lambda: connection,
    )
    asegurar_tabla_permisos_usuario()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()
    connection.commit.assert_not_called()


@pytest.mark.parametrize(
    'kwargs',
    [
        {'nombre': 'A', 'url': '/a'},
        {'nombre': 'Nombre-Mayus', 'url': '/a'},
        {'nombre': 'obras', 'url': 'obras'},
        {'nombre': 'obras', 'url': '/obras', 'tipo': 'Otro'},
        {'nombre': 'obras', 'url': '/obras', 'descripcion': '<script>'},
    ],
)
def test_modulo_rechaza_datos_invalidos(kwargs):
    with pytest.raises(ValueError):
        ModuloModel(**kwargs)._validar()


def test_modulo_registrar_valida_guarda_y_cierra(monkeypatch):
    connection, cursor = _mock_database()
    cursor.lastrowid = 12
    model = ModuloModel('obras', 'Gestión de obras', '/obras', 'CRUD', 'bi-hammer', 3, 1)
    _connect(monkeypatch, model, connection)

    assert model.registrar() == 12

    assert cursor.execute.call_args.args[1] == (
        'obras', 'Gestión de obras', '/obras', 'CRUD', 'bi-hammer', 3, 1,
    )
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(
    ('method', 'args', 'fetch_method', 'expected'),
    [
        ('consultar_activos', (), 'fetchall', [{'id_modulo': 2}]),
        ('obtener_por_id', (2,), 'fetchone', {'id_modulo': 2}),
    ],
)
def test_modulo_consultas_retorna_filas_y_parametriza_id(monkeypatch, method, args, fetch_method, expected):
    connection, cursor = _mock_database()
    getattr(cursor, fetch_method).return_value = expected
    model = ModuloModel('obras', url='/obras')
    _connect(monkeypatch, model, connection)

    assert getattr(model, method)(*args) == expected

    assert cursor.execute.called
    if args:
        assert cursor.execute.call_args.args[1] == args
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(('rowcount', 'expected'), [(1, True), (0, False)])
def test_modulo_actualizar_y_eliminar_devuelven_estado_de_filas(monkeypatch, rowcount, expected):
    connection, cursor = _mock_database()
    cursor.rowcount = rowcount
    model = ModuloModel('obras', 'Obras', '/obras', 'CRUD', id_modulo=6)
    _connect(monkeypatch, model, connection)

    assert model.actualizar() is expected
    assert cursor.execute.call_args.args[1] == ('obras', 'Obras', '/obras', 'CRUD', None, 0, 1, 6)
    connection.commit.assert_called_once_with()

    cursor.reset_mock()
    connection.reset_mock()
    _connect(monkeypatch, model, connection)
    assert model.eliminar() is expected
    assert cursor.execute.call_args.args == (
        'UPDATE modulos SET estado = 0 WHERE id_modulo = %s', (6,),
    )
    connection.commit.assert_called_once_with()


@pytest.mark.parametrize(
    ('excluding', 'row', 'expected', 'sql_tail', 'params'),
    [
        (None, {'exists': 1}, True, 'estado = 1 LIMIT 1', ('obras',)),
        (None, None, False, 'estado = 1 LIMIT 1', ('obras',)),
        (8, {'exists': 1}, True, 'id_modulo <> %s AND estado = 1 LIMIT 1', ('obras', 8)),
    ],
)
def test_modulo_validar_nombre_existente_condiciona_exclusion(
    monkeypatch, excluding, row, expected, sql_tail, params
):
    connection, cursor = _mock_database()
    cursor.fetchone.return_value = row
    model = ModuloModel('obras', url='/obras')
    _connect(monkeypatch, model, connection)

    assert model.validar_nombre_existente(excluding) is expected
    sql, actual_params = cursor.execute.call_args.args
    assert sql.endswith(sql_tail)
    assert actual_params == params


def test_rol_valida_y_registra_nombre_recortado(monkeypatch):
    with pytest.raises(ValueError):
        RolModel(nombre='A1')._validar()
    model = RolModel('  Administrador  ', 'Admin', id_rol=5)
    model._validar()
    connection, cursor = _mock_database()
    cursor.lastrowid = 4
    _connect(monkeypatch, model, connection)

    assert model.registrar() == 4
    assert cursor.execute.call_args.args[1] == ('Administrador', 'Admin', 1)
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(
    ('method', 'args', 'fetch_method', 'expected'),
    [
        ('consultar_activos', (), 'fetchall', [{'id_rol': 1}]),
        ('obtener_por_id', (1,), 'fetchone', {'id_rol': 1}),
        ('obtener_usuarios_por_rol', (), 'fetchall', [{'id_usuarios': 9}]),
    ],
)
def test_rol_consultas_retorna_datos_y_usa_rol_actual(
    monkeypatch, method, args, fetch_method, expected
):
    connection, cursor = _mock_database()
    getattr(cursor, fetch_method).return_value = expected
    model = RolModel(' Usuario ')
    _connect(monkeypatch, model, connection)

    assert getattr(model, method)(*args) == expected

    if method == 'obtener_por_id':
        assert cursor.execute.call_args.args[1] == (1,)
    elif method == 'obtener_usuarios_por_rol':
        assert cursor.execute.call_args.args[1] == ('Usuario',)
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(('rowcount', 'expected'), [(1, True), (0, False)])
def test_rol_actualizar_y_eliminar_reportan_si_hubo_cambios(monkeypatch, rowcount, expected):
    connection, cursor = _mock_database()
    cursor.rowcount = rowcount
    model = RolModel(' Admin ', 'desc', estado=0, id_rol=7)
    _connect(monkeypatch, model, connection)

    assert model.actualizar() is expected
    assert cursor.execute.call_args.args[1] == ('Admin', 'desc', 0, 7)
    connection.commit.assert_called_once_with()

    cursor.reset_mock()
    connection.reset_mock()
    _connect(monkeypatch, model, connection)
    assert model.eliminar() is expected
    assert cursor.execute.call_args.args == ('UPDATE roles SET estado = 0 WHERE id_rol = %s', (7,))


def test_rol_eliminar_rechaza_super_usuario(monkeypatch):
    connection, cursor = _mock_database()
    cursor.fetchone.return_value = {'nombre': 'Super Usuario'}
    model = RolModel(id_rol=1)
    _connect(monkeypatch, model, connection)

    assert model.eliminar() is False

    assert cursor.execute.call_count == 1
    assert cursor.execute.call_args.args == (
        'SELECT nombre FROM roles WHERE id_rol = %s', (1,),
    )
    connection.commit.assert_not_called()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(
    ('method', 'exclude_id', 'row', 'expected', 'params'),
    [
        ('validar_nombre_existente', None, {'id': 1}, True, ('Admin',)),
        ('validar_nombre_existente', 3, None, False, ('Admin', 3)),
        ('existe_super_usuario_activo', None, {'id_rol': 1}, True, ('Super Usuario',)),
        ('existe_super_usuario_activo', 3, None, False, ('Super Usuario', 3)),
    ],
)
def test_rol_existence_checks_handle_exclusions(monkeypatch, method, exclude_id, row, expected, params):
    connection, cursor = _mock_database()
    cursor.fetchone.return_value = row
    model = RolModel(' Admin ')
    _connect(monkeypatch, model, connection)

    assert getattr(model, method)(exclude_id) is expected
    assert cursor.execute.call_args.args[1] == params


@pytest.mark.parametrize(('row', 'expected'), [({'id_rol': 8}, 8), (None, None)])
def test_rol_obtener_super_usuario_id(row, expected, monkeypatch):
    connection, cursor = _mock_database()
    cursor.fetchone.return_value = row
    model = RolModel()
    _connect(monkeypatch, model, connection)

    assert model.obtener_super_usuario_id() == expected
    assert cursor.execute.call_args.args[1] == ('Super Usuario',)
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_rol_permiso_consultas_retorna_datos_y_aplica_override_usuario(monkeypatch):
    connection, cursor = _mock_database()
    rows = [{'id_modulo': 1, 'nombre': 'obras'}]
    cursor.fetchall.return_value = rows
    model = RolPermisoModel()
    _connect(monkeypatch, model, connection)

    assert model.obtener_por_rol(4) == rows
    assert cursor.execute.call_args.args[1] == (4,)
    cursor.fetchall.return_value = [{'nombre': 'obras'}, {'nombre': 'usuarios'}]
    assert model.obtener_nombres_modulos_por_rol('Admin') == ['obras', 'usuarios']
    assert cursor.execute.call_args.args[1] == ('Admin',)
    cursor.fetchone.return_value = {
        'puede_ver': 1, 'puede_crear': 0, 'puede_editar': 1, 'puede_eliminar': 0,
        'usuario_puede_ver': 0, 'usuario_puede_crear': None,
        'usuario_puede_editar': 1, 'usuario_puede_eliminar': None,
    }
    assert model.obtener_permiso('Admin', 5, 'obras') == {
        'puede_ver': 0, 'puede_crear': 0, 'puede_editar': 1, 'puede_eliminar': 0,
    }
    assert cursor.execute.call_args.args[1] == ('Admin', 5, 'obras')
    assert cursor.close.call_count == 3
    assert connection.close.call_count == 3


def test_rol_permiso_sin_fila_y_permisos_directos(monkeypatch):
    connection, cursor = _mock_database()
    model = RolPermisoModel()
    _connect(monkeypatch, model, connection)
    cursor.fetchone.return_value = None
    assert model.obtener_permiso('Admin', 5, 'obras') is None

    rows = [{'nombre': 'obras', 'id_modulo': 2, 'puede_ver': 1}]
    cursor.fetchall.return_value = rows
    assert model.obtener_permisos_usuario(5) == rows
    assert cursor.execute.call_args.args[1] == (5,)


@pytest.mark.parametrize('method', ['guardar_permisos_usuario', 'guardar_permisos'])
def test_guardar_permisos_reemplaza_registros_y_confirma_transaccion(monkeypatch, method):
    connection, cursor = _mock_database()
    model = RolPermisoModel()
    _connect(monkeypatch, model, connection)
    permission = {
        'id_modulo': 3, 'puede_ver': True, 'puede_crear': False,
        'puede_editar': 1, 'puede_eliminar': 0,
    }

    assert getattr(model, method)(11, [permission]) is True

    calls = cursor.execute.call_args_list
    assert len(calls) == 2
    assert calls[0].args[1] == (11,)
    assert 'UPDATE usuarios_permisos' in calls[0].args[0] if method == 'guardar_permisos_usuario' else 'UPDATE roles_permisos' in calls[0].args[0]
    assert calls[1].args[1] == (11, 3, 1, 0, 1, 0)
    assert 'ON DUPLICATE KEY UPDATE' in calls[1].args[0]
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize('method', ['guardar_permisos_usuario', 'guardar_permisos'])
def test_guardar_permisos_vacia_lista_y_revierte_si_falla(monkeypatch, method):
    connection, cursor = _mock_database()
    model = RolPermisoModel()
    _connect(monkeypatch, model, connection)
    assert getattr(model, method)(12, []) is True
    assert cursor.execute.call_count == 1
    connection.commit.assert_called_once_with()

    connection, cursor = _mock_database()
    cursor.execute.side_effect = RuntimeError('write failed')
    _connect(monkeypatch, model, connection)
    assert getattr(model, method)(12, [{'id_modulo': 3}]) is False
    connection.rollback.assert_called_once_with()
    connection.commit.assert_not_called()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()
