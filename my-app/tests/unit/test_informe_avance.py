from datetime import datetime
from unittest.mock import patch

import pytest
from PIL import Image

from models.model_informe_avance import InformeAvanceModel


def informe_sin_conexion():
    informe = InformeAvanceModel.__new__(InformeAvanceModel)
    informe._InformeAvanceModel__id_informe = None
    informe._InformeAvanceModel__fecha = None
    informe._InformeAvanceModel__estado = None
    informe._InformeAvanceModel__poblacion_beneficiada = None
    informe._InformeAvanceModel__tipo_informe = None
    informe._InformeAvanceModel__observaciones = None
    informe._InformeAvanceModel__avance_id = None
    informe._InformeAvanceModel__porcentaje_avance = 0
    informe._InformeAvanceModel__gerente = None
    informe._InformeAvanceModel__evidencias_antes = []
    informe._InformeAvanceModel__evidencias_durante = []
    informe._InformeAvanceModel__evidencias_despues = []
    informe._InformeAvanceModel__estado_registro = 1
    return informe


def test_porcentaje_de_avance_se_limita_a_rango_valido():
    informe = informe_sin_conexion()

    informe.set_porcentaje_avance(120)

    assert informe.get_porcentaje_avance() == 100


def test_estado_de_informe_normaliza_opcion_valida():
    informe = informe_sin_conexion()

    informe.set_estado('En Ejecución')

    assert informe.get_estado() == 'En Ejecucion'


def test_rechaza_estado_de_informe_desconocido():
    with pytest.raises(ValueError):
        informe_sin_conexion().set_estado('Desconocido')


class _Cursor:
    def __init__(self, rows=None, rowcount=1):
        self.rows = iter(rows or [])
        self.calls = []
        self.rowcount = rowcount
        self.lastrowid = 22
        self.closed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return next(self.rows, None)

    def fetchall(self):
        return []

    def close(self):
        self.closed = True


class _Connection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = self.rollbacks = 0
        self.closed = False

    def cursor(self, **kwargs):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def test_setters_de_informe_cubren_catalogos_fechas_textos_y_evidencias():
    i = informe_sin_conexion()
    i.set_id_informe('14')
    i.set_fecha('2025-01-02 03:04:05')
    assert i.get_id_informe() == 14
    assert i.get_fecha() == datetime(2025, 1, 2, 3, 4, 5)
    i.set_fecha('fecha inválida')
    assert isinstance(i.get_fecha(), datetime)
    i.set_estado('Aprobado')
    i.set_poblacion_beneficiada('  Barquisimeto  ')
    i.set_tipo_informe('Mayor')
    i.set_observaciones(None)
    i.set_evidencias_antes([1, 2])
    i.set_evidencias_durante([3])
    i.set_evidencias_despues([4])
    i.set_avance_id(99)
    i.set_gerente(5)
    assert i.get_estado() == 'Aprobado'
    assert i.get_poblacion_beneficiada() == 'Barquisimeto'
    assert i.get_tipo_informe() == 'Mayor'
    assert i.get_observaciones() == 'Sin observaciones'
    assert i.get_avance_id() == '99' and i.get_gerente() == '5'
    i.set_gerente('')
    assert i.get_gerente() == '5'
    i.set_avance_id(None)
    assert i.get_avance_id() is None
    for method in ('set_evidencias_antes', 'set_evidencias_durante', 'set_evidencias_despues'):
        with pytest.raises(ValueError):
            getattr(i, method)([1, 2, 3, 4, 5, 6])
    with pytest.raises(ValueError):
        i.set_poblacion_beneficiada('x')
    with pytest.raises(ValueError):
        i.set_tipo_informe('invalido')
    with pytest.raises(ValueError):
        i.set_observaciones('x' * 2001)
    for value, expected in [(None, 0), ('bad', 0), (-4, 0), (45, 45), (111, 100)]:
        i.set_porcentaje_avance(value)
        assert i.get_porcentaje_avance() == expected


def test_constructor_informe_inicializa_campos_sin_acceder_a_bd():
    with patch.object(InformeAvanceModel, '_InformeAvanceModel__asegurar_tabla_informe') as tabla, \
            patch.object(InformeAvanceModel, '_InformeAvanceModel__asegurar_tabla_avance') as avance:
        i = InformeAvanceModel()
    tabla.assert_called_once_with()
    avance.assert_called_once_with()
    assert i.get_id_informe() is None
    assert i.get_fecha() is None
    assert i.get_porcentaje_avance() == 0
    assert i.get_gerente() is None


def test_helpers_de_schema_migran_columna_y_amplian_evidencias():
    i = informe_sin_conexion()

    class Cursor:
        def __init__(self, rows):
            self.rows = iter(rows)
            self.calls = []

        def execute(self, sql, params=None):
            self.calls.append((sql, params))

        def fetchone(self):
            return next(self.rows, None)

    cursor = Cursor([None, {'Field': 'poblacion_benefiada'}])
    i._InformeAvanceModel__asegurar_columna_poblacion(cursor)
    assert any('CHANGE COLUMN poblacion_benefiada' in sql for sql, _ in cursor.calls)
    cursor = Cursor([('evidencia_antes', 'varchar(45)'), None, None])
    i._InformeAvanceModel__asegurar_columnas_evidencia(cursor)
    assert 'MODIFY COLUMN evidencia_antes VARCHAR(255)' in cursor.calls[1][0]
    assert cursor.calls[0][1] == ('evidencia_antes',)


def test_crear_avance_usa_claves_de_obra_y_cierra_transaccion():
    i = informe_sin_conexion()
    cursor = _Cursor([None, (7, 2, 3, 'FRE-007'), None])
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        advance_id = i._InformeAvanceModel__crear_avance_db(5, 130, '  revisión de obra  ')
    assert len(advance_id) == 12
    insert = [call for call in cursor.calls if call[0].lstrip().startswith('INSERT INTO avance')][0]
    assert insert[1][0] == advance_id
    assert insert[1][1:4] == ('revisión de obra', 100, '5')
    assert insert[1][5:] == (7, 2, 3, 'FRE-007')
    assert conn.commits == 1 and conn.closed and cursor.closed


def test_registrar_y_actualizar_informe_db_persisten_evidencias_parametrizadas():
    i = informe_sin_conexion()
    i.set_estado('Aprobado')
    i.set_poblacion_beneficiada('Comunidad')
    i.set_tipo_informe('Mayor')
    i.set_evidencias_antes([1, 2])
    i.set_evidencias_durante([3])
    i.set_evidencias_despues([4])
    i.set_avance_id('avance-1')
    i.set_observaciones('Trabajo ejecutado')
    i.set_porcentaje_avance(75)
    cursor = _Cursor([(12,)])
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn), \
            patch.object(i, '_InformeAvanceModel__asegurar_columna_poblacion'):
        assert i._InformeAvanceModel__registrar_informe_db() == 12
    params = [p for sql, p in cursor.calls if sql.lstrip().startswith('INSERT')][0]
    assert params[5:8] == ('1,2', '3', '4')
    assert any(p == ('Trabajo ejecutado', 75, 'avance-1') for _, p in cursor.calls)
    assert conn.commits == 2 and conn.closed

    i._InformeAvanceModel__id_informe = 12
    cursor = _Cursor([('avance-1',)])
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        assert i._InformeAvanceModel__actualizar_informe_db() is True
    assert cursor.calls[0][1] == ('Aprobado', 'Comunidad', 'Mayor', '1,2', '3', '4', 12)
    assert cursor.calls[2][1] == ('Trabajo ejecutado', 75, 'avance-1')
    assert conn.commits == 1 and conn.closed


def test_consultas_validaciones_y_borrado_logico_de_informe_cubren_recurso():
    i = informe_sin_conexion()
    i.set_id_informe(6)
    rows = [{'id_informe': 6}]
    cursor = _Cursor([{'id_informe': 6}])
    cursor.fetchall = lambda: rows
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        assert i._InformeAvanceModel__obtener_todos_informes_db() == rows
    assert 'estado_registro = 1' in cursor.calls[0][0]
    assert conn.closed and cursor.closed
    cursor = _Cursor([{'id_informe': 6}])
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn), \
            patch.object(i, '_InformeAvanceModel__obtener_evidencias_por_informe', return_value=[]):
        assert i._InformeAvanceModel__obtener_informe_por_id_db(6) == {
            'id_informe': 6, 'evidencias': []
        }
    assert cursor.calls[0][1] == (6,)
    assert conn.closed and cursor.closed

    cursor = _Cursor([(6,), (6,)])
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        assert i._InformeAvanceModel__validar_informe_activo_db(6)
        assert i._InformeAvanceModel__validar_gerente_activo_db('8')
    assert cursor.calls[-1][1] == (8, 'Gerente', 'Inspector')
    assert conn.closed

    cursor = _Cursor(rowcount=1)
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        assert i._InformeAvanceModel__eliminar_logico_db()
    assert 'estado_registro = 0' in cursor.calls[0][0]
    assert conn.commits == 1


def test_interfaces_publicas_de_informe_validan_y_delegan():
    i = informe_sin_conexion()
    valid = {'gerente_responsable_id': '4', 'estado': 'Aprobado',
             'poblacion_beneficiada': 'Comunidad', 'tipo_informe': 'Mayor',
             'observaciones': 'Avance satisfactorio', 'porcentaje_avance': 20,
             'avance_id_avance': 'a-1', 'evidencias_antes': '1,2'}
    with patch.object(i, '_InformeAvanceModel__validar_gerente_activo_db', return_value=True), \
            patch.object(i, '_InformeAvanceModel__registrar_informe_db', return_value=9) as save:
        assert i.registrar_informe(valid) == 9
    save.assert_called_once_with()
    assert i.get_avance_id() == 'a-1'
    with patch.object(i, '_InformeAvanceModel__validar_informe_activo_db', return_value=True), \
            patch.object(i, '_InformeAvanceModel__validar_gerente_activo_db', return_value=True), \
            patch.object(i, '_InformeAvanceModel__actualizar_informe_db', return_value=True):
        assert i.actualizar_informe(dict(valid, id_informe='9')) is True
        assert i.get_id_informe() == 9
    with patch.object(i, '_InformeAvanceModel__validar_informe_activo_db', return_value=False):
        with pytest.raises(ValueError):
            i.eliminar_informe_logico(9)
    with patch.object(i, '_InformeAvanceModel__validar_informe_activo_db', return_value=True), \
            patch.object(i, '_InformeAvanceModel__eliminar_logico_db', return_value=True):
        assert i.eliminar_informe_logico(9) is True
    with patch.object(i, '_InformeAvanceModel__obtener_todos_informes_db', return_value=[1]), \
            patch.object(i, '_InformeAvanceModel__obtener_informe_por_id_db', return_value={'id': 9}), \
            patch.object(i, '_InformeAvanceModel__obtener_gerentes_activos_db', return_value=[4]), \
            patch.object(i, '_InformeAvanceModel__validar_informe_activo_db', return_value=True), \
            patch.object(i, '_InformeAvanceModel__validar_gerente_activo_db', return_value=True):
        assert i.obtener_todos_informes() == [1]
        assert i.obtener_informe_por_id('9') == {'id': 9}
        assert i.obtener_informe_por_id('bad') is None
        assert i.obtener_gerentes_activos() == [4]
        assert i.validar_informe_activo('9')
        assert not i.validar_informe_activo('bad')
        assert i.validar_gerente_activo(4)


def test_comprimir_imagen_normaliza_rgb_y_rechaza_ruta_invalida(tmp_path):
    ruta = tmp_path / 'foto.png'
    Image.new('RGBA', (4, 3), (10, 20, 30, 50)).save(ruta, format='PNG')
    assert InformeAvanceModel.comprimir_imagen(str(ruta), calidad=70) is True
    with Image.open(ruta) as result:
        assert result.format == 'JPEG'
        assert result.mode == 'RGB'
    assert InformeAvanceModel.comprimir_imagen(str(tmp_path / 'missing.jpg')) is False


def test_obtener_informes_por_ids_compone_evidencias_y_parametriza_consultas():
    i = informe_sin_conexion()
    informes = [{
        'id_informe': 1, 'evidencia_antes': '10', 'evidencia_durante': '20',
        'evidencia_despues': '',
    }]
    evidencias = [
        {'id_evidencia': 10, 'etapa': 'antes'},
        {'id_evidencia': 20, 'etapa': 'durante'},
        {'id_evidencia': 30, 'etapa': 'antes'},
    ]
    cursor = _Cursor()
    results = iter([informes, evidencias])
    cursor.fetchall = lambda: next(results, [])
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        resultado = i.obtener_informes_por_ids([1, 2])
    assert resultado[0]['evidencias'] == evidencias[:2]
    assert cursor.calls[0][1] == (1, 2)
    assert set(cursor.calls[1][1]) == {'10', '20'}
    assert conn.closed and cursor.closed
    assert i.obtener_informes_por_ids([]) == []


def test_validar_gerente_activo_conexion_fallida_o_identificador_invalido():
    i = informe_sin_conexion()
    with patch.object(i, 'obtener_conexion', return_value=None):
        assert not i._InformeAvanceModel__validar_gerente_activo_db(3)
        assert not i._InformeAvanceModel__validar_gerente_activo_db('no-id')
        assert not i._InformeAvanceModel__validar_informe_activo_db(1)


def test_helper_de_evidencias_y_lectores_de_catalogo():
    i = informe_sin_conexion()
    cursor = _Cursor()
    cursor.fetchall = lambda: [{'id_evidencia': 10}]
    assert i._InformeAvanceModel__obtener_evidencias_por_informe(cursor, 4) == [
        {'id_evidencia': 10}
    ]
    assert cursor.calls[0][1] == (4,)
    with patch.object(i, '_InformeAvanceModel__obtener_gerentes_activos_db', return_value=[8]) as gerentes:
        assert i.obtener_gerentes_activos() == [8]
    gerentes.assert_called_once_with()


@pytest.mark.parametrize(('rows', 'expected_sql'), [
    ([{'Field': 'ok'}, {'Field': 'typo'}], 'DROP COLUMN poblacion_benefiada'),
    ([None, {'Field': 'typo'}], 'CHANGE COLUMN poblacion_benefiada'),
    ([None, None], 'ADD COLUMN poblacion_beneficiada'),
    ([{'Field': 'ok'}, None], 'MODIFY COLUMN poblacion_beneficiada'),
])
def test_migracion_de_poblacion_cubre_cuatro_esquemas_legacy(rows, expected_sql):
    i = informe_sin_conexion()

    class Cursor:
        def __init__(self):
            self.results = iter(rows)
            self.calls = []

        def execute(self, sql, params=None):
            self.calls.append((sql, params))

        def fetchone(self):
            return next(self.results, None)

    cursor = Cursor()
    i._InformeAvanceModel__asegurar_columna_poblacion(cursor)
    assert any(expected_sql in sql for sql, _ in cursor.calls)


def test_asegurar_tablas_de_informe_y_avance_aplica_migraciones_con_mock_db():
    i = informe_sin_conexion()
    cursor = _Cursor()
    schema_rows = iter([
        None, ('evidencia_antes', 'varchar(45)'),
        ('evidencia_durante', 'varchar(255)'), ('evidencia_despues', 'text'),
    ])
    cursor.fetchone = lambda: next(schema_rows, None)
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn), \
            patch.object(i, '_InformeAvanceModel__asegurar_columna_poblacion'):
        i._InformeAvanceModel__asegurar_tabla_informe()
    assert any('ADD COLUMN estado_registro' in sql for sql, _ in cursor.calls)
    assert any('MODIFY COLUMN evidencia_antes VARCHAR(255)' in sql for sql, _ in cursor.calls)
    assert conn.commits == 3 and conn.closed and cursor.closed

    cursor = _Cursor()
    schema_rows = iter([
        ('descripcion', 'varchar(45)'), None, None, None, None, None, None,
    ])
    cursor.fetchone = lambda: next(schema_rows, None)
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        i._InformeAvanceModel__asegurar_tabla_avance()
    assert any('MODIFY COLUMN descripcion TEXT' in sql for sql, _ in cursor.calls)
    assert sum('ADD COLUMN' in sql for sql, _ in cursor.calls) == 3
    assert conn.commits == 2 and conn.closed and cursor.closed


def test_registrar_informe_db_reintenta_colision_y_persiste_el_siguiente_id():
    class Duplicate(Exception):
        errno = 1062

    class RetryCursor(_Cursor):
        def __init__(self):
            super().__init__([(1,), (2,)])
            self.insert_count = 0

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT'):
                self.insert_count += 1
                if self.insert_count == 1:
                    raise Duplicate()

    i = informe_sin_conexion()
    i.set_estado('Aprobado')
    i.set_poblacion_beneficiada('Comunidad')
    i.set_tipo_informe('Mayor')
    cursor = RetryCursor()
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn), \
            patch.object(i, '_InformeAvanceModel__asegurar_columna_poblacion'):
        assert i._InformeAvanceModel__registrar_informe_db() == 2
    inserts = [params for sql, params in cursor.calls if sql.lstrip().startswith('INSERT')]
    assert [params[0] for params in inserts] == [1, 2]
    assert conn.rollbacks == 1 and conn.commits == 2
    assert conn.closed and cursor.closed


def test_borrado_informe_usa_delete_como_fallback_si_estado_no_actualiza():
    class FallbackCursor(_Cursor):
        def execute(self, sql, params=None):
            super().execute(sql, params)
            self.rowcount = 0 if sql.startswith('UPDATE') else 1

    i = informe_sin_conexion()
    i.set_id_informe(3)
    cursor = FallbackCursor()
    conn = _Connection(cursor)
    with patch.object(i, 'obtener_conexion', return_value=conn):
        assert i._InformeAvanceModel__eliminar_logico_db() is True
    assert len(cursor.calls) == 2
    assert cursor.calls[0][1] == (3,) and cursor.calls[1][1] == (3,)
    assert cursor.calls[1][0].startswith('DELETE')
    assert conn.commits == 1 and conn.closed and cursor.closed
