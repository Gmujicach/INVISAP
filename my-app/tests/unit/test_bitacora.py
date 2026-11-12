from models.model_bitacora import BitacoraModel
from unittest.mock import patch


class _Cursor:
    def __init__(self, one=None, many=None):
        self.one = one
        self.many = many or []
        self.calls = []
        self.closed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.many

    def close(self):
        self.closed = True


class _Connection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self, **kwargs):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def test_bitacora_acepta_texto_y_usuario_validos():
    assert BitacoraModel._es_texto_valido('Solicitud registrada') is True
    assert BitacoraModel._es_usuario_valido('Ana Pérez') is True


def test_bitacora_rechaza_caracteres_no_permitidos():
    assert BitacoraModel._es_texto_valido('<script>') is False
    assert BitacoraModel._es_usuario_valido('usuario@ejemplo.com') is False


def test_validadores_aceptan_limites_y_rechazan_entrada_vacia():
    assert BitacoraModel._es_texto_valido('x' * 100)
    assert not BitacoraModel._es_texto_valido('x' * 101)
    assert BitacoraModel._es_usuario_valido('á' * 15)
    assert not BitacoraModel._es_usuario_valido('')


def test_registrar_normaliza_entradas_antes_de_insertar():
    modelo = BitacoraModel()
    with patch.object(modelo, '_sql_insertar', return_value=True) as insertar:
        assert modelo.registrar('  Ana  ', '23', ' Obras ', 'crear', 'hecho')
    insertar.assert_called_once_with('Ana', 23, 'Obras', 'CREAR', 'hecho')
    with patch.object(modelo, '_sql_insertar', return_value=True) as insertar:
        modelo.registrar('', 'no-id', '', '', '')
    insertar.assert_called_once_with('Sistema', 1, 'General', 'VER', '')


def test_facadas_de_filtrado_validan_y_sanitizan_criterios():
    modelo = BitacoraModel()
    with patch.object(modelo, '_sql_filtrar_por_usuario', return_value=['u']) as fn:
        assert modelo.filtrar_por_usuario('A;na') == ['u']
        fn.assert_called_once_with('Ana')
        assert modelo.filtrar_por_usuario('a') == []
        fn.assert_called_once()
    with patch.object(modelo, '_sql_filtrar_por_modulo', return_value=['m']) as fn:
        assert modelo.filtrar_por_modulo('Ob<ras') == ['m']
        fn.assert_called_once_with('Obras')
        assert modelo.filtrar_por_modulo('') == []
    with patch.object(modelo, '_sql_filtrar_por_accion', return_value=['a']) as fn:
        assert modelo.filtrar_por_accion(' login ') == ['a']
        assert modelo.filtrar_por_accion('DROP') == []
        fn.assert_called_once_with('LOGIN')


def test_filtro_compuesto_calcula_offset_y_omite_accion_desconocida():
    modelo = BitacoraModel()
    with patch.object(modelo, '_sql_filtrar_por_criterios', return_value=[1]) as fn:
        assert modelo.filtrar_por_criterios('Ana', 'Obras', 'incorrecta', page=3, per_page=7) == [1]
    assert fn.call_args.kwargs == {
        'usuario': 'Ana', 'modulo': 'Obras', 'accion': None, 'limit': 7, 'offset': 14
    }
    with patch.object(modelo, 'obtener_todos', return_value=['all']) as todos:
        assert modelo.filtrar_por_criterios('x', None, '???') == ['all']
        todos.assert_called_once_with()
    with patch.object(modelo, '_sql_contar_filtrados', return_value=6) as contar:
        assert modelo.contar_filtrados('Ana;', 'Ob<ras', 'ver') == 6
    contar.assert_called_once_with(usuario='Ana', modulo='Obras', accion='VER')


def test_metodos_sql_consultan_parametrizado_y_cierra_recursos():
    rows = [{'id_bitacora': 1}]
    cursor = _Cursor(one=(4,), many=rows)
    conn = _Connection(cursor)
    modelo = BitacoraModel()
    with patch.object(modelo, '_con', return_value=conn):
        assert modelo._sql_obtener_todos(5) == rows
        assert cursor.calls[-1][1] == (5,)
        assert modelo._sql_filtrar_por_usuario('Ana') == rows
        assert cursor.calls[-1][1] == ('%Ana%',)
        assert modelo._sql_filtrar_por_modulo('Obras') == rows
        assert cursor.calls[-1][1] == ('Obras',)
        assert modelo._sql_filtrar_por_accion('VER') == rows
        assert cursor.calls[-1][1] == ('VER',)
        assert modelo._sql_contar_filtrados(usuario='Ana', modulo='Obras', accion='VER') == 4
        assert cursor.calls[-1][1] == ('%Ana%', 'Obras', 'VER')
    assert conn.closed and cursor.closed


def test_metodos_sql_criterios_estadisticas_y_registro():
    modelo = BitacoraModel()
    rows = [{'accion': 'VER', 'total': 3}]
    cursor = _Cursor(one=(3,), many=rows)
    conn = _Connection(cursor)
    with patch.object(modelo, '_con', return_value=conn):
        assert modelo._sql_filtrar_por_criterios('Ana', 'Obras', 'VER', 8, 16) == rows
        assert cursor.calls[-1][1] == ('%Ana%', 'Obras', 'VER', 8, 16)
        assert modelo._sql_contar_por_accion() == {'VER': 3}
        assert modelo._sql_contar_filtrados() == 3
    assert conn.closed and cursor.closed
    with patch.object(modelo, '_sql_contar_por_accion', return_value={'VER': 3}) as stats:
        assert modelo.estadisticas_por_accion() == {'VER': 3}
    stats.assert_called_once_with()
    with patch.object(modelo, '_sql_obtener_todos', return_value=rows) as todos:
        assert modelo.obtener_todos(9) == rows
    todos.assert_called_once_with(limit=9)


def test_insertar_confirma_y_reintenta_id_duplicado_con_limpieza():
    class Duplicate(Exception):
        errno = 1062

    class RetryCursor(_Cursor):
        def __init__(self):
            super().__init__()
            self.sequence = iter([(1,), (2,)])

        def fetchone(self):
            return next(self.sequence)

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT') and params[0] == 1:
                raise Duplicate()

    modelo = BitacoraModel()
    cursor = RetryCursor()
    conn = _Connection(cursor)
    with patch.object(modelo, '_con', return_value=conn):
        assert modelo._sql_insertar('Ana', 3, 'Obras', 'VER', '')
    inserts = [args for sql, args in cursor.calls if sql.lstrip().startswith('INSERT')]
    assert [values[0] for values in inserts] == [1, 2]
    assert conn.rollbacks == 1 and conn.commits == 1
    assert conn.closed and cursor.closed


def test_bitacora_sql_degrada_con_seguridad_si_no_hay_conexion():
    modelo = BitacoraModel()
    with patch.object(modelo, '_con', return_value=None):
        assert modelo._sql_obtener_todos() == []
        assert modelo._sql_filtrar_por_usuario('Ana') == []
        assert modelo._sql_filtrar_por_modulo('Obras') == []
        assert modelo._sql_filtrar_por_accion('VER') == []
        assert modelo._sql_filtrar_por_criterios('Ana') == []
        assert modelo._sql_contar_por_accion() == {}
        assert modelo._sql_contar_filtrados() == 0
        assert modelo._sql_insertar('Ana', 1, 'Obras', 'VER', '') is False


def test_conexion_estatica_delega_y_criterios_vacios_reutilizan_listado():
    with patch.object(BitacoraModel, 'obtener_conexion_seguridad', return_value='fake-connection') as conectar:
        assert BitacoraModel._con() == 'fake-connection'
    conectar.assert_called_once_with()
    modelo = BitacoraModel()
    cursor = _Cursor()
    conn = _Connection(cursor)
    with patch.object(modelo, '_con', return_value=conn), \
            patch.object(modelo, '_sql_obtener_todos', return_value=['all']) as listar:
        assert modelo._sql_filtrar_por_criterios(limit=4) == ['all']
    listar.assert_called_once_with(limit=4)
    assert conn.closed and cursor.closed
