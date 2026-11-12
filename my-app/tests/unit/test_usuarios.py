from unittest.mock import MagicMock, call, patch

import pytest

from models.model_usuarios import DEFAULT_AVATAR, UsuarioModel


def test_listar_usuarios_asigna_avatar_por_defecto():
    usuario = UsuarioModel()
    conexion = MagicMock()
    conexion.cursor.return_value.fetchall.return_value = [
        {'id_usuarios': 1, 'avatar': None},
        {'id_usuarios': 2, 'avatar': 'assets/avatar.png'},
    ]

    with patch.object(usuario, 'obtener_conexion_seguridad', return_value=conexion):
        usuarios = usuario.listar_todos()

    assert usuarios[0]['avatar'] == DEFAULT_AVATAR
    assert usuarios[1]['avatar'] == 'assets/avatar.png'


def _mock_database():
    cursor = MagicMock()
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def _model_without_constructor(**kwargs):
    model = UsuarioModel.__new__(UsuarioModel)
    UsuarioModel.__init__(model, **kwargs)
    return model


def test_constructor_getters_y_setters():
    usuario = UsuarioModel(3, 'Ana', 'ana@example.test', 'hash', '123', 'Admin', 'foto.png')
    assert (usuario.get_id(), usuario.get_nombre(), usuario.get_correo()) == (
        3, 'Ana', 'ana@example.test',
    )
    assert (usuario.get_contrasena(), usuario.get_cedula(), usuario.get_rol(), usuario.get_avatar()) == (
        'hash', '123', 'Admin', 'foto.png',
    )

    usuario.set_nombre('Eva')
    usuario.set_correo('eva@example.test')
    usuario.set_contrasena('nuevo-hash')
    usuario.set_cedula('456')
    usuario.set_rol('Usuario')
    usuario.set_avatar('nuevo.png')
    assert (usuario.get_nombre(), usuario.get_correo(), usuario.get_contrasena()) == (
        'Eva', 'eva@example.test', 'nuevo-hash',
    )
    assert (usuario.get_cedula(), usuario.get_rol(), usuario.get_avatar()) == (
        '456', 'Usuario', 'nuevo.png',
    )


@pytest.mark.parametrize(
    ('method', 'query', 'parameter'),
    [
        ('buscar_por_nombre', 'SELECT * FROM usuarios WHERE nombre = %s', 'Ana'),
        ('buscar_por_email', 'SELECT * FROM usuarios WHERE correo = %s', 'ana@example.test'),
    ],
)
def test_busquedas_por_nombre_y_correo_consultan_y_cierran(
    monkeypatch, method, query, parameter
):
    connection, cursor = _mock_database()
    row = {'id_usuarios': 8, 'nombre': 'Ana'}
    cursor.fetchone.return_value = row
    usuario = _model_without_constructor()
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    assert getattr(usuario, method)(parameter) == row

    assert cursor.execute.call_args.args == (query, (parameter,))
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(
    ('row', 'expected'),
    [({'id_usuarios': 1}, True), (None, False)],
)
def test_validar_duplicados_busca_correo_o_cedula(monkeypatch, row, expected):
    connection, cursor = _mock_database()
    cursor.fetchone.return_value = row
    usuario = _model_without_constructor()
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    assert usuario.validar_duplicados('a@b.test', '99') is expected
    assert cursor.execute.call_args.args == (
        'SELECT id_usuarios FROM usuarios WHERE correo = %s OR cedula_usuario = %s',
        ('a@b.test', '99'),
    )
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


@pytest.mark.parametrize(
    ('method', 'row', 'expected_avatar'),
    [
        ('buscar_por_id', {'id_usuarios': 2, 'avatar': None}, DEFAULT_AVATAR),
        ('buscar_por_id', {'id_usuarios': 2, 'avatar': 'custom.png'}, 'custom.png'),
        ('buscar_por_id_con_contrasena', {'id_usuarios': 2, 'avatar': None, 'contrasena': 'hash'}, DEFAULT_AVATAR),
    ],
)
def test_buscar_por_id_aplica_avatar_sin_quitar_campos(
    monkeypatch, method, row, expected_avatar
):
    connection, cursor = _mock_database()
    cursor.fetchone.return_value = row.copy()
    usuario = _model_without_constructor()
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    result = getattr(usuario, method)(2)

    assert result['avatar'] == expected_avatar
    assert result['id_usuarios'] == 2
    if 'contrasena' in row:
        assert result['contrasena'] == 'hash'
    assert cursor.execute.call_args.args[1] == (2,)
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_busquedas_de_usuario_devuelven_none_sin_conexion_y_si_no_hay_fila(monkeypatch):
    usuario = _model_without_constructor()
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: None)
    assert usuario.buscar_por_nombre('Ana') is None
    assert usuario.buscar_por_email('ana@example.test') is None
    assert usuario.validar_duplicados('a@b.test', '1') is False
    assert usuario.listar_todos() == []
    assert usuario.buscar_por_id(1) is None
    assert usuario.buscar_por_id_con_contrasena(1) is None

    connection, cursor = _mock_database()
    cursor.fetchone.return_value = None
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)
    assert usuario.buscar_por_id(1) is None
    assert usuario.buscar_por_id_con_contrasena(1) is None


def test_incluir_guarda_datos_con_hash_y_usa_rol_por_defecto(monkeypatch):
    usuario = _model_without_constructor()
    with patch('models.model_usuarios.generate_password_hash', return_value='hashed') as hash_password, \
            patch.object(usuario, '_UsuarioModel__registrar_db', return_value=True) as registrar:
        assert usuario.incluir({
            'nombre': 'Ana', 'correo': 'ana@example.test', 'cedula_usuario': '10',
            'pass_user': 'secreto',
        }) is True

    hash_password.assert_called_once_with('secreto')
    registrar.assert_called_once_with()
    assert (usuario.get_nombre(), usuario.get_correo(), usuario.get_cedula(), usuario.get_rol()) == (
        'Ana', 'ana@example.test', '10', 'Usuario',
    )
    assert usuario.get_contrasena() == 'hashed'

    usuario = _model_without_constructor()
    with patch.object(usuario, '_UsuarioModel__registrar_db', return_value=False) as registrar:
        assert usuario.incluir({'nombre': 'Beto', 'rol': None}) is False
    registrar.assert_called_once_with()
    assert usuario.get_contrasena() is None
    assert usuario.get_rol() is None


def test_actualizar_hashes_password_opcional_y_actualiza_campos(monkeypatch):
    usuario = _model_without_constructor()
    with patch('models.model_usuarios.generate_password_hash', return_value='hashed') as hash_password, \
            patch.object(usuario, '_UsuarioModel__actualizar_db', return_value=True) as actualizar_db:
        assert usuario.actualizar(4, 'Ana', 'ana@example.test', '11', 'Admin', password='plain') is True

    hash_password.assert_called_once_with('plain')
    actualizar_db.assert_called_once_with()
    assert usuario.get_id() == 4
    assert (usuario.get_nombre(), usuario.get_correo(), usuario.get_cedula(), usuario.get_rol()) == (
        'Ana', 'ana@example.test', '11', 'Admin',
    )
    assert usuario.get_contrasena() == 'hashed'

    with patch.object(usuario, '_UsuarioModel__actualizar_db', return_value=False):
        assert usuario.actualizar(5, 'Eva', 'e@example.test', '12', 'Usuario') is False
    assert usuario.get_contrasena() is None


@pytest.mark.parametrize(
    ('method', 'sql_part', 'values', 'rowcount', 'expected'),
    [
        ('_UsuarioModel__registrar_db', 'INSERT INTO usuarios', ('Ana', 'a@b.test', 'hash', '9', 'Admin'), 1, True),
        ('_UsuarioModel__actualizar_db', 'UPDATE usuarios SET', ('Ana', 'a@b.test', '9', 'Admin', 'hash', 6), 1, True),
    ],
)
def test_db_insert_y_update_ejecutan_sql_commit_y_limpieza(
    monkeypatch, method, sql_part, values, rowcount, expected
):
    connection, cursor = _mock_database()
    cursor.rowcount = rowcount
    usuario = _model_without_constructor(
        id_usuarios=6 if method == '_UsuarioModel__actualizar_db' else None,
        nombre='Ana', correo='a@b.test',
        contrasena='hash', cedula='9', rol='Admin',
    )
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    assert getattr(usuario, method)() is expected

    sql, params = cursor.execute.call_args.args
    assert sql_part in sql
    assert params == values
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_update_sin_password_omite_columna_y_devuelve_false_si_no_hay_cambios(monkeypatch):
    connection, cursor = _mock_database()
    cursor.rowcount = 0
    usuario = _model_without_constructor(
        id_usuarios=6, nombre='Ana', correo='a@b.test',
        cedula='9', rol='Admin',
    )
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    assert usuario._UsuarioModel__actualizar_db() is False
    sql, params = cursor.execute.call_args.args
    assert 'contrasena' not in sql
    assert params == ('Ana', 'a@b.test', '9', 'Admin', 6)
    connection.commit.assert_called_once_with()


def test_operaciones_db_devuelven_false_sin_conexion(monkeypatch):
    usuario = _model_without_constructor()
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: None)
    assert usuario._UsuarioModel__registrar_db() is False
    assert usuario._UsuarioModel__actualizar_db() is False
    assert usuario._UsuarioModel__eliminar_fisico_db() is False
    assert usuario.guardar() is False


def test_eliminar_fisico_db_ejecuta_delete_y_guardar_selecciona_accion(monkeypatch):
    connection, cursor = _mock_database()
    usuario = _model_without_constructor(id_usuarios=2)
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    assert usuario._UsuarioModel__eliminar_fisico_db() is True
    assert cursor.execute.call_args.args == (
        'DELETE FROM usuarios WHERE id_usuarios = %s', (2,),
    )
    connection.commit.assert_called_once_with()

    with patch.object(usuario, '_UsuarioModel__actualizar_db', return_value='updated') as update:
        assert usuario.guardar() == 'updated'
    update.assert_called_once_with()
    usuario = _model_without_constructor()
    with patch.object(usuario, '_UsuarioModel__registrar_db', return_value='inserted') as register:
        assert usuario.guardar() == 'inserted'
    register.assert_called_once_with()


def test_eliminar_usa_id_suministrado_y_rechaza_usuario_sin_id():
    usuario = _model_without_constructor()
    with patch.object(usuario, '_UsuarioModel__eliminar_fisico_db', return_value=True) as delete:
        assert usuario.eliminar() is False
        assert usuario.eliminar(9) is True
    delete.assert_called_once_with()
    assert usuario.get_id() == 9


def test_existe_y_activo_consulta_y_cierra_recursos(monkeypatch):
    connection, cursor = _mock_database()
    cursor.fetchone.side_effect = [{'id_usuarios': 3}, None]
    usuario = _model_without_constructor()
    monkeypatch.setattr(usuario, 'obtener_conexion_seguridad', lambda: connection)

    assert usuario.existe_y_activo(3) is True
    assert usuario.existe_y_activo(4) is False

    assert cursor.execute.call_args_list == [
        call(
            'SELECT id_usuarios FROM usuarios WHERE id_usuarios = %s',
            (3,),
        ),
        call(
            'SELECT id_usuarios FROM usuarios WHERE id_usuarios = %s',
            (4,),
        ),
    ]
    assert cursor.close.call_count == 2
    assert connection.close.call_count == 2
