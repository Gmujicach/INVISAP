import pytest
from unittest.mock import patch

from models.model_inspeccion import InspeccionModel


def test_validadores_de_inspeccion_aceptan_datos_correctos():
    inspeccion = InspeccionModel.__new__(InspeccionModel)

    assert inspeccion._validar_inspector('12') is True
    assert inspeccion._validar_fecha('2025-03-18') is True
    assert inspeccion._validar_observaciones('Inspección en buen estado') is True


def test_validadores_de_inspeccion_rechazan_datos_invalidos():
    inspeccion = InspeccionModel.__new__(InspeccionModel)

    assert inspeccion._validar_inspector('cero') is False
    assert inspeccion._validar_fecha('18/03/2025') is False
    assert inspeccion._validar_observaciones('no') is False


def test_tipo_de_inspeccion_rechaza_valores_no_catalogados():
    inspeccion = InspeccionModel.__new__(InspeccionModel)

    with pytest.raises(ValueError):
        inspeccion.set_tipo_inspeccion('Preventiva')


def _inspeccion():
    i = InspeccionModel.__new__(InspeccionModel)
    i._InspeccionModel__id_inspeccion = None
    i._InspeccionModel__inspector = None
    i._InspeccionModel__fecha_inspeccion = None
    i._InspeccionModel__tipo_inspeccion = None
    i._InspeccionModel__observaciones = None
    i._InspeccionModel__obra_id_obra = None
    i._InspeccionModel__evidencia_id_evidencia = None
    i._InspeccionModel__evidencias_adicionales = None
    i._InspeccionModel__estado = 1
    return i


class _Cursor:
    def __init__(self, one=None, many=None, rowcount=1):
        self.one, self.many, self.rowcount = one, many or [], rowcount
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
        self.commits = self.closed = 0

    def cursor(self, **kwargs):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def close(self):
        self.closed += 1


def test_inspeccion_accesores_validaciones_y_mapeo_de_etapas():
    i = _inspeccion()
    i.set_id_inspeccion(3)
    i.set_inspector('12')
    i.set_fecha_inspeccion('2025-03-18')
    i.set_tipo_inspeccion(' Final ')
    i.set_observaciones('Inspección normal')
    i.set_obra_id_obra(5)
    i.set_evidencia_id_evidencia(8)
    i.set_evidencias_adicionales(4)
    i.set_estado(0)
    assert (i.get_id_inspeccion(), i.get_inspector(), i.get_fecha_inspeccion()) == (3, 12, '2025-03-18')
    assert i.get_tipo_inspeccion() == 'Final'
    assert i.get_observaciones() == 'Inspección normal'
    assert i.get_obra_id_obra() == 5 and i.get_evidencia_id_evidencia() == 8
    assert i.get_evidencias_adicionales() == '4' and i.get_estado() == 0
    for method, value in [('set_id_inspeccion', 0), ('set_inspector', '0'),
                          ('set_fecha_inspeccion', 'bad'), ('set_observaciones', 'no'),
                          ('set_obra_id_obra', 0), ('set_evidencia_id_evidencia', 0),
                          ('set_estado', 2)]:
        with pytest.raises(ValueError):
            getattr(i, method)(value)
    assert i._InspeccionModel__mapear_tipo_a_etapa('Inicial') == 'antes'
    assert i._InspeccionModel__mapear_tipo_a_etapa('Intermedia') == 'durante'
    assert i._InspeccionModel__mapear_tipo_a_etapa('Final') == 'despues'
    assert i._InspeccionModel__mapear_tipo_a_etapa('Extraordinaria') == 'durante'
    assert i._InspeccionModel__mapear_tipo_a_etapa('otro') == 'antes'


def test_helpers_de_configuracion_y_carga_de_evidencias_adicionales():
    class SchemaCursor:
        def __init__(self, result):
            self.result, self.calls = result, []

        def execute(self, sql, params=None):
            self.calls.append((sql, params))

        def fetchone(self):
            return self.result

        def fetchall(self):
            return [{'id_evidencia': 2}]

    c = SchemaCursor({'Field': 'obra_semaforo_id_semaforo'})
    assert InspeccionModel._InspeccionModel__get_obra_fk_config(c) == {
        'semaforo_col': 'obra_semaforo_id_semaforo',
        'semaforo1_col': 'obra_semaforo_id_semaforo1',
        'obra_select': 'semaforo_id_semaforo',
    }
    c = SchemaCursor(None)
    assert InspeccionModel._InspeccionModel__get_obra_fk_config(c)['obra_select'] == 'estado'
    row = {'evidencias_adicionales': '2, bad, 4'}
    InspeccionModel._InspeccionModel__cargar_evidencias_adicionales(row, c)
    assert row['evidencias_adicionales_list'] == [{'id_evidencia': 2}]
    assert c.calls[-1][1] == [2, 4]
    row = {'evidencias_adicionales': 'bad'}
    InspeccionModel._InspeccionModel__cargar_evidencias_adicionales(row, c)
    assert row['evidencias_adicionales_list'] == []


def test_conectar_prueba_conexion_secundaria_y_no_disponible():
    i = _inspeccion()
    with patch.object(i, 'obtener_conexion', side_effect=RuntimeError('down')), \
            patch.object(i, 'obtener_conexion_seguridad_segura', return_value='secure'):
        assert i._conectar() == 'secure'
    with patch.object(i, 'obtener_conexion', return_value=None), \
            patch.object(i, 'obtener_conexion_seguridad_segura', return_value=None):
        assert i._conectar() is None


def test_interfaces_publicas_de_inspeccion_validan_delegan_y_retorna_catalogo():
    i = _inspeccion()
    with patch.object(i, '_InspeccionModel__guardar_inspeccion_db', return_value=19) as save:
        assert i.registrar_inspeccion({
            'inspector': '12', 'fecha_inspeccion': '2025-01-03',
            'tipo_inspeccion': 'Inicial', 'observaciones': 'Inspección válida',
            'obra_id_obra': '2', 'evidencia_id_evidencia': '6',
            'evidencias_adicionales': '3,4',
        }) == 19
    save.assert_called_once_with()
    with pytest.raises(ValueError):
        i.registrar_inspeccion({'inspector': '0'})
    with patch.object(i, '_InspeccionModel__validar_inspeccion_activa_db', return_value=True), \
            patch.object(i, '_InspeccionModel__actualizar_inspeccion_db', return_value=True), \
            patch.object(i, '_InspeccionModel__eliminar_logico_db', return_value=True):
        data = {'id_inspeccion': '3', 'inspector': '12', 'fecha_inspeccion': '2025-01-03',
                'tipo_inspeccion': 'Final', 'observaciones': 'Inspección válida',
                'obra_id_obra': '2', 'evidencia_id_evidencia': '6'}
        assert i.actualizar_inspeccion(data) is True
        assert i.eliminar_inspeccion(3) is True
    with patch.object(i, '_InspeccionModel__validar_inspeccion_activa_db', return_value=False):
        with pytest.raises(ValueError):
            i.eliminar_inspeccion(3)
    assert i.obtener_catalogo_tipos_inspeccion() == [
        'Extraordinaria', 'Final', 'Inicial', 'Intermedia'
    ]


def test_operaciones_publicas_de_lectura_y_existencia_delegan():
    i = _inspeccion()
    with patch.object(i, '_InspeccionModel__obtener_inspeccion_por_id_db', return_value={'id': 5}), \
            patch.object(i, '_InspeccionModel__obtener_todas_inspecciones_db', return_value=[5]), \
            patch.object(i, '_InspeccionModel__validar_inspeccion_activa_db', return_value=True), \
            patch.object(i, '_InspeccionModel__validar_obra_existe_db', return_value=True) as obra, \
            patch.object(i, '_InspeccionModel__validar_evidencia_existe_db', return_value=False) as evidencia, \
            patch.object(i, '_InspeccionModel__obtener_obras_db', return_value=[1]), \
            patch.object(i, '_InspeccionModel__obtener_evidencias_db', return_value=[2]), \
            patch.object(i, '_InspeccionModel__obtener_inspectores_db', return_value=[3]):
        assert i.obtener_inspeccion_por_id(5) == {'id': 5}
        assert i.obtener_inspeccion_por_id('bad') is None
        assert i.obtener_todas_inspecciones() == [5]
        assert i.validar_inspeccion_activa(5)
        assert not i.validar_inspeccion_activa(0)
        assert i.obra_existe(2) and not i.evidencia_existe(3)
        assert i.obtener_obras() == [1]
        assert i.obtener_evidencias() == [2]
        assert i.obtener_inspectores() == [3]
    obra.assert_called_once_with(2)
    evidencia.assert_called_once_with(3)


def test_helpers_db_inspeccion_consultan_ids_columnas_obras_y_evidencias():
    i = _inspeccion()
    cursor = _Cursor(one={'id_obra': 2}, many=[{'id_obra': 2}])
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn):
        assert i._InspeccionModel__columna_existe('obra', 'estado') is True
    assert cursor.calls[0][1] == ('estado',) and conn.closed == 1
    with pytest.raises(ValueError):
        i._InspeccionModel__columna_existe('usuarios', 'id')

    cursor = _Cursor(one={'id_obra': 2}, many=[{'id_obra': 2}])
    result_rows = iter([None, {'id_obra': 2}])
    cursor.fetchone = lambda: next(result_rows, None)
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn):
        assert i._InspeccionModel__buscar_obra_por_id_db(2) == {'id_obra': 2}
        assert cursor.calls[-1][1] == (2,)
    assert conn.closed == 1 and cursor.closed

    cursor = _Cursor(one={'id_evidencia': 8})
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn):
        assert i._InspeccionModel__buscar_evidencia_por_id_db(8) == {'id_evidencia': 8}
    assert cursor.calls[0][1] == (8,)
    assert 'estado = 1' in cursor.calls[0][0]


def test_siguiente_id_y_limpieza_de_cedula_son_deterministas():
    class IdCursor:
        def __init__(self):
            self.closed = False

        def execute(self, sql, params=None):
            self.sql = sql

        def fetchone(self):
            return {'siguiente': 13}

        def close(self):
            self.closed = True

    cursor_id = IdCursor()
    conn_id = _Connection(cursor_id)
    assert InspeccionModel._InspeccionModel__obtener_siguiente_id_inspeccion(conn_id) == 13
    assert cursor_id.closed

    class CleanupCursor:
        def __init__(self):
            self.calls = []
            self.closed = False

        def execute(self, sql, params=None):
            self.calls.append((sql, params))
            self.sql = sql

        def fetchall(self):
            return [{'TRIGGER_NAME': 'safe_trigger'}]

        def fetchone(self):
            return {'exists': 1}

        def close(self):
            self.closed = True

    cleanup = CleanupCursor()
    conn = _Connection(cleanup)
    i = _inspeccion()
    i._InspeccionModel__limpiar_cedula_inspeccion(cleanup, conn)
    sqls = [sql for sql, _ in cleanup.calls]
    assert 'DROP TRIGGER IF EXISTS `safe_trigger`' in sqls
    assert 'ALTER TABLE inspeccion DROP INDEX cedula_UNIQUE' in sqls
    assert 'ALTER TABLE inspeccion DROP COLUMN cedula' in sqls
    assert conn.commits == 1


def test_guardar_inspeccion_construye_insert_con_relaciones_y_cierra():
    i = _inspeccion()
    i.set_inspector(2)
    i.set_fecha_inspeccion('2025-01-03')
    i.set_tipo_inspeccion('Final')
    i.set_observaciones('Inspección válida')
    i.set_obra_id_obra(5)
    i.set_evidencia_id_evidencia(8)
    i.set_evidencias_adicionales('9,10')
    cursor = _Cursor()
    cursor.lastrowid = 33
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__limpiar_cedula_inspeccion'), \
            patch.object(i, '_InspeccionModel__columna_existe',
                         side_effect=lambda table, column: column == 'estado'), \
            patch.object(i, '_InspeccionModel__buscar_obra_por_id_db',
                         return_value={'estado': 2, 'contratacion_id_contratacion': 4,
                                       'gestionar_proyectos_codigo_proyecto': 'FRE-005'}), \
            patch.object(i, '_InspeccionModel__buscar_evidencia_por_id_db',
                         return_value={'id_evidencia': 8}), \
            patch.object(i, '_InspeccionModel__get_obra_fk_config',
                         return_value={'semaforo_col': 'obra_estado',
                                       'semaforo1_col': 'obra_estado1'}), \
            patch.object(i, '_InspeccionModel__obtener_siguiente_id_inspeccion', return_value=12):
        assert i._InspeccionModel__guardar_inspeccion_db() == 33
    insert_sql, params = cursor.calls[-1]
    assert insert_sql.startswith('INSERT INTO inspeccion')
    assert 'obra_estado' in insert_sql and params[0:5] == (12, 2, '2025-01-03', 'Final', 'Inspección válida')
    assert params[-3:] == (8, '9,10', 1)
    assert conn.commits == 1 and conn.closed == 1 and cursor.closed


def test_db_de_listas_y_validaciones_activos_parametriza_consultas():
    i = _inspeccion()
    cursor = _Cursor(one=(1,), many=[{'id': 1}])
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__columna_existe', return_value=True):
        assert i._InspeccionModel__validar_inspeccion_activa_db() is True
    assert cursor.calls[0][1] == (None,)
    cursor = _Cursor(one=(5,))
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__columna_existe', return_value=True):
        assert i._InspeccionModel__validar_obra_existe_db(5)
    assert cursor.calls[0][1] == (5,)
    cursor = _Cursor(one=None)
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn):
        assert not i._InspeccionModel__validar_evidencia_existe_db(6)
    assert cursor.calls[0][1] == (6,)


def test_constructor_y_schema_helpers_de_inspeccion_quedan_aislados():
    with patch.object(InspeccionModel, '_InspeccionModel__asegurar_tabla_inspeccion') as asegurar:
        i = InspeccionModel()
    asegurar.assert_called_once_with()
    assert i.get_id_inspeccion() is None
    assert i.get_estado() == 1

    cursor = _Cursor()
    i._InspeccionModel__asegurar_columnas_obra_inspeccion(cursor)
    alter_sql = [sql for sql, _ in cursor.calls if sql.startswith('ALTER TABLE')]
    for column in ('obra_estado', 'obra_contratacion_id_contratacion',
                   'obra_gestionar_proyectos_codigo_proyecto', 'obra_estado1',
                   'obra_contratacion_id_contratacion1',
                   'obra_gestionar_proyectos_codigo_proyecto1', 'evidencias_adicionales'):
        assert any(f'ADD COLUMN {column} ' in sql for sql in alter_sql)


def test_asegurar_tabla_inspeccion_aplica_migraciones_con_falsa_conexion():
    i = _inspeccion()
    cursor = _Cursor()
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn):
        i._InspeccionModel__asegurar_tabla_inspeccion()
    assert any('ADD COLUMN estado' in sql for sql, _ in cursor.calls)
    assert any('ADD COLUMN evidencias_adicionales' in sql for sql, _ in cursor.calls)
    assert conn.commits >= 2 and conn.closed == 1 and cursor.closed


def test_selectores_de_listas_de_inspeccion_devuelven_filas_y_cierran():
    i = _inspeccion()
    rows = [{'id_inspeccion': 4}]
    cursor = _Cursor(many=rows)
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__columna_existe', return_value=True):
        assert i._InspeccionModel__obtener_todas_inspecciones_db() == rows
    assert 'WHERE i.estado = 1' in cursor.calls[0][0]
    assert conn.closed == 1 and cursor.closed

    cursor = _Cursor(one={'id_inspeccion': 4, 'evidencias_adicionales': ''})
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__columna_existe', return_value=True), \
            patch.object(i, '_InspeccionModel__cargar_evidencias_adicionales') as cargar:
        assert i._InspeccionModel__obtener_inspeccion_por_id_db() == {
            'id_inspeccion': 4, 'evidencias_adicionales': ''
        }
    cargar.assert_called_once()
    assert conn.closed == 1 and cursor.closed


def test_consultas_catalogo_de_inspeccion_separan_obras_evidencias_e_inspectores():
    i = _inspeccion()
    rows = [{'id': 1}]
    cursor = _Cursor(many=rows)
    schema = iter([None])
    cursor.fetchone = lambda: next(schema, None)
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn):
        assert i._InspeccionModel__obtener_obras_db() == rows
    assert 'estado AS estado' in cursor.calls[-1][0]
    assert conn.closed == 1

    for method, expected in [
        ('_InspeccionModel__obtener_evidencias_db', 'FROM evidencia WHERE estado = 1'),
        ('_InspeccionModel__obtener_inspectores_db', "TRIM(cargo) = 'Inspector'"),
    ]:
        cursor = _Cursor(many=rows)
        conn = _Connection(cursor)
        with patch.object(i, '_conectar', return_value=conn):
            assert getattr(i, method)() == rows
        assert expected in cursor.calls[0][0]
        assert conn.closed == 1 and cursor.closed


def test_actualizar_inspeccion_actualiza_relaciones_y_etapa_de_evidencia():
    i = _inspeccion()
    i.set_id_inspeccion(14)
    i.set_inspector(2)
    i.set_fecha_inspeccion('2025-01-03')
    i.set_tipo_inspeccion('Final')
    i.set_observaciones('Inspección válida')
    i.set_obra_id_obra(5)
    i.set_evidencia_id_evidencia(8)
    i.set_evidencias_adicionales('9')
    cursor = _Cursor()
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__limpiar_cedula_inspeccion'), \
            patch.object(i, '_InspeccionModel__buscar_obra_por_id_db',
                         return_value={'estado': 1, 'contratacion_id_contratacion': 4,
                                       'gestionar_proyectos_codigo_proyecto': 'FRE-005'}), \
            patch.object(i, '_InspeccionModel__buscar_evidencia_por_id_db', return_value={'id': 8}), \
            patch.object(i, '_InspeccionModel__get_obra_fk_config',
                         return_value={'semaforo_col': 'obra_estado',
                                       'semaforo1_col': 'obra_estado1'}), \
            patch.object(i, '_InspeccionModel__columna_existe', return_value=True):
        assert i._InspeccionModel__actualizar_inspeccion_db() is True
    update_sql, update_params = cursor.calls[0]
    assert update_sql.lstrip().startswith('UPDATE inspeccion')
    assert update_params[-3:] == (8, '9', 14)
    assert cursor.calls[1] == (
        'UPDATE evidencia SET etapa = %s, fecha_registro = NOW() WHERE id_evidencia = %s AND estado = 1',
        ('despues', 8),
    )
    assert conn.commits == 1 and conn.closed == 1 and cursor.closed


def test_borrado_logico_de_inspeccion_commit_y_cierra_recursos():
    i = _inspeccion()
    i.set_id_inspeccion(6)
    cursor = _Cursor(rowcount=1)
    conn = _Connection(cursor)
    with patch.object(i, '_conectar', return_value=conn), \
            patch.object(i, '_InspeccionModel__columna_existe', return_value=True):
        assert i._InspeccionModel__eliminar_logico_db() is True
    assert cursor.calls[0][1] == (6,)
    assert 'SET estado = 0' in cursor.calls[0][0]
    assert conn.commits == 1 and conn.closed == 1 and cursor.closed
