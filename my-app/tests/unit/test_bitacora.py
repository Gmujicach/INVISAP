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
    # INICIO DE ASERCIÓN: Verificar validadores de texto y usuario
    assert BitacoraModel._BitacoraModel__es_texto_valido('Solicitud registrada') is True
    assert BitacoraModel._BitacoraModel__es_usuario_valido('Ana Pérez') is True
    # FIN DE ASERCIÓN


def test_bitacora_rechaza_caracteres_no_permitidos():
    # INICIO DE ASERCIÓN: Verificar rechazo de caracteres no permitidos
    assert BitacoraModel._BitacoraModel__es_texto_valido('<script>') is False
    assert BitacoraModel._BitacoraModel__es_usuario_valido('usuario@ejemplo.com') is False
    # FIN DE ASERCIÓN


def test_validadores_aceptan_limites_y_rechazan_entrada_vacia():
    # INICIO DE ASERCIÓN: Verificar límites y entrada vacía
    assert BitacoraModel._BitacoraModel__es_texto_valido('x' * 100)
    assert not BitacoraModel._BitacoraModel__es_texto_valido('x' * 101)
    assert BitacoraModel._BitacoraModel__es_usuario_valido('á' * 15)
    assert not BitacoraModel._BitacoraModel__es_usuario_valido('')
    # FIN DE ASERCIÓN


def test_registrar_normaliza_entradas_antes_de_insertar():
    modelo = BitacoraModel()
    # INICIO DE MOCK: Parchear _sql_insertar para primera llamada
    with patch.object(modelo, '_BitacoraModel__sql_insertar', return_value=True) as insertar:
        # INICIO DE MOCK: Llamar registrar con entradas
        assert modelo.registrar('  Ana  ', '23', ' Obras ', 'crear', 'hecho')
    # INICIO DE ASERCIÓN: Verificar llamada con valores normalizados
    insertar.assert_called_once_with('Ana', 23, 'Obras', 'CREAR', 'hecho')
    # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear _sql_insertar para segunda llamada
    with patch.object(modelo, '_BitacoraModel__sql_insertar', return_value=True) as insertar:
        # INICIO DE MOCK: Llamar registrar con entradas vacías
        modelo.registrar('', 'no-id', '', '', '')
    # INICIO DE ASERCIÓN: Verificar valores por defecto
    insertar.assert_called_once_with('Sistema', 1, 'General', 'VER', '')
    # FIN DE ASERCIÓN


def test_facadas_de_filtrado_validan_y_sanitizan_criterios():
    modelo = BitacoraModel()
    # INICIO DE MOCK: Parchear _sql_filtrar_por_usuario
    with patch.object(modelo, '_BitacoraModel__sql_filtrar_por_usuario', return_value=['u']) as fn:
        # INICIO DE MOCK: Llamar filtrar_por_usuario
        assert modelo.filtrar_por_usuario('A;na') == ['u']
        # INICIO DE ASERCIÓN: Verificar llamada y validación
        fn.assert_called_once_with('Ana')
        assert modelo.filtrar_por_usuario('a') == []
        fn.assert_called_once()
        # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear _sql_filtrar_por_modulo
    with patch.object(modelo, '_BitacoraModel__sql_filtrar_por_modulo', return_value=['m']) as fn:
        # INICIO DE MOCK: Llamar filtrar_por_modulo
        assert modelo.filtrar_por_modulo('Ob<ras') == ['m']
        # INICIO DE ASERCIÓN: Verificar llamada y validación
        fn.assert_called_once_with('Obras')
        assert modelo.filtrar_por_modulo('') == []
        # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear _sql_filtrar_por_accion
    with patch.object(modelo, '_BitacoraModel__sql_filtrar_por_accion', return_value=['a']) as fn:
        # INICIO DE MOCK: Llamar filtrar_por_accion
        assert modelo.filtrar_por_accion(' login ') == ['a']
        assert modelo.filtrar_por_accion('DROP') == []
        # INICIO DE ASERCIÓN: Verificar llamada y validación
        fn.assert_called_once_with('LOGIN')
        # FIN DE ASERCIÓN


def test_filtro_compuesto_calcula_offset_y_omite_accion_desconocida():
    modelo = BitacoraModel()
    # INICIO DE MOCK: Parchear _sql_filtrar_por_criterios
    with patch.object(modelo, '_BitacoraModel__sql_filtrar_por_criterios', return_value=[1]) as fn:
        # INICIO DE MOCK: Llamar filtrar_por_criterios
        assert modelo.filtrar_por_criterios('Ana', 'Obras', 'incorrecta', page=3, per_page=7) == [1]
    # INICIO DE ASERCIÓN: Verificar argumentos de llamada
    assert fn.call_args.kwargs == {
        'usuario': 'Ana', 'modulo': 'Obras', 'accion': None, 'limit': 7, 'offset': 14
    }
    # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear obtener_todos
    with patch.object(modelo, '_BitacoraModel__sql_obtener_todos', return_value=['all']) as todos:
        # INICIO DE MOCK: Llamar filtrar_por_criterios con accion desconocida
        assert modelo.filtrar_por_criterios('x', None, '???') == ['all']
        # INICIO DE ASERCIÓN: Verificar llamada a obtener_todos
        todos.assert_called_once_with()
        # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear _sql_contar_filtrados
    with patch.object(modelo, '_BitacoraModel__sql_contar_filtrados', return_value=6) as contar:
        # INICIO DE MOCK: Llamar contar_filtrados
        assert modelo.contar_filtrados('Ana;', 'Ob<ras', 'ver') == 6
    # INICIO DE ASERCIÓN: Verificar llamada con valores sanitizados
    contar.assert_called_once_with(usuario='Ana', modulo='Obras', accion='VER')
    # FIN DE ASERCIÓN


def test_metodos_sql_consultan_parametrizado_y_cierra_recursos():
    rows = [{'id_bitacora': 1}]
    cursor = _Cursor(one=(4,), many=rows)
    conn = _Connection(cursor)
    modelo = BitacoraModel()
    # INICIO DE MOCK: Parchear _con para devolver conexión simulada
    with patch.object(modelo, '_BitacoraModel__con', return_value=conn):
        # INICIO DE MOCK: Llamar métodos SQL
        assert modelo._BitacoraModel__sql_obtener_todos(5) == rows
        # INICIO DE ASERCIÓN: Verificar parámetros de consulta
        assert cursor.calls[-1][1] == (5,)
        assert modelo._BitacoraModel__sql_filtrar_por_usuario('Ana') == rows
        assert cursor.calls[-1][1] == ('%Ana%',)
        assert modelo._BitacoraModel__sql_filtrar_por_modulo('Obras') == rows
        assert cursor.calls[-1][1] == ('Obras',)
        assert modelo._BitacoraModel__sql_filtrar_por_accion('VER') == rows
        assert cursor.calls[-1][1] == ('VER',)
        assert modelo._BitacoraModel__sql_contar_filtrados(usuario='Ana', modulo='Obras', accion='VER') == 4
        assert cursor.calls[-1][1] == ('%Ana%', 'Obras', 'VER')
        # FIN DE ASERCIÓN
    # INICIO DE ASERCIÓN: Verificar que recursos se cierran
    assert conn.closed and cursor.closed
    # FIN DE ASERCIÓN


def test_metodos_sql_criterios_estadisticas_y_registro():
    modelo = BitacoraModel()
    rows = [{'accion': 'VER', 'total': 3}]
    cursor = _Cursor(one=(3,), many=rows)
    conn = _Connection(cursor)
    # INICIO DE MOCK: Parchear _con para devolver conexión simulada
    with patch.object(modelo, '_BitacoraModel__con', return_value=conn):
        # INICIO DE MOCK: Llamar métodos SQL
        assert modelo._BitacoraModel__sql_filtrar_por_criterios('Ana', 'Obras', 'VER', 8, 16) == rows
        # INICIO DE ASERCIÓN: Verificar parámetros
        assert cursor.calls[-1][1] == ('%Ana%', 'Obras', 'VER', 8, 16)
        assert modelo._BitacoraModel__sql_contar_por_accion() == {'VER': 3}
        assert modelo._BitacoraModel__sql_contar_filtrados() == 3
        # FIN DE ASERCIÓN
    # INICIO DE ASERCIÓN: Verificar que recursos se cierran
    assert conn.closed and cursor.closed
    # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear _sql_contar_por_accion
    with patch.object(modelo, '_BitacoraModel__sql_contar_por_accion', return_value={'VER': 3}) as stats:
        # INICIO DE MOCK: Llamar estadisticas_por_accion
        assert modelo.estadisticas_por_accion() == {'VER': 3}
        # INICIO DE ASERCIÓN: Verificar llamada
        stats.assert_called_once_with()
        # FIN DE ASERCIÓN
    # INICIO DE MOCK: Parchear _sql_obtener_todos
    with patch.object(modelo, '_BitacoraModel__sql_obtener_todos', return_value=rows) as todos:
        # INICIO DE MOCK: Llamar obtener_todos
        assert modelo.obtener_todos(9) == rows
    # INICIO DE ASERCIÓN: Verificar llamada
    todos.assert_called_once_with(limit=9)
    # FIN DE ASERCIÓN


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
    # INICIO DE MOCK: Parchear _con para devolver conexión simulada
    with patch.object(modelo, '_BitacoraModel__con', return_value=conn):
        # INICIO DE MOCK: Llamar _sql_insertar
        assert modelo._BitacoraModel__sql_insertar('Ana', 3, 'Obras', 'VER', '')
    # INICIO DE ASERCIÓN: Verificar reintentos y rollback/commit
    inserts = [args for sql, args in cursor.calls if sql.lstrip().startswith('INSERT')]
    assert [values[0] for values in inserts] == [1, 2]
    assert conn.rollbacks == 1 and conn.commits == 1
    assert conn.closed and cursor.closed
    # FIN DE ASERCIÓN


def test_bitacora_sql_degrada_con_seguridad_si_no_hay_conexion():
    modelo = BitacoraModel()
    # INICIO DE MOCK: Parchear _con para devolver None
    with patch.object(modelo, '_BitacoraModel__con', return_value=None):
        # INICIO DE MOCK: Llamar métodos SQL sin conexión
        assert modelo._BitacoraModel__sql_obtener_todos() == []
        assert modelo._BitacoraModel__sql_filtrar_por_usuario('Ana') == []
        assert modelo._BitacoraModel__sql_filtrar_por_modulo('Obras') == []
        assert modelo._BitacoraModel__sql_filtrar_por_accion('VER') == []
        assert modelo._BitacoraModel__sql_filtrar_por_criterios('Ana') == []
        assert modelo._BitacoraModel__sql_contar_por_accion() == {}
        assert modelo._BitacoraModel__sql_contar_filtrados() == 0
        assert modelo._BitacoraModel__sql_insertar('Ana', 1, 'Obras', 'VER', '') is False
        # INICIO DE ASERCIÓN: Verificar degradación segura (implícita en asserts)
        # FIN DE ASERCIÓN


def test_conexion_estatica_delega_y_criterios_vacios_reutilizan_listado():
    # INICIO DE MOCK: Parchear obtener_conexion_seguridad
    with patch.object(BitacoraModel, 'obtener_conexion_seguridad', return_value='fake-connection') as conectar:
        # INICIO DE MOCK: Llamar _con
        assert BitacoraModel._BitacoraModel__con() == 'fake-connection'
    # INICIO DE ASERCIÓN: Verificar llamada
    conectar.assert_called_once_with()
    # FIN DE ASERCIÓN
    modelo = BitacoraModel()
    cursor = _Cursor()
    conn = _Connection(cursor)
    # INICIO DE MOCK: Parchear _con y _sql_obtener_todos
    with patch.object(modelo, '_BitacoraModel__con', return_value=conn), \
            patch.object(modelo, '_BitacoraModel__sql_obtener_todos', return_value=['all']) as listar:
        # INICIO DE MOCK: Llamar _sql_filtrar_por_criterios con criterios vacíos
        assert modelo._BitacoraModel__sql_filtrar_por_criterios(limit=4) == ['all']
    # INICIO DE ASERCIÓN: Verificar delegación y cierre
    listar.assert_called_once_with(limit=4)
    assert conn.closed and cursor.closed
    # FIN DE ASERCIÓN
