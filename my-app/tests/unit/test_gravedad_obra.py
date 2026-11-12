import pytest
from unittest.mock import patch

from controllers.controller_gravedad import _calcular_nivel_gravedad
from models.model_gravedad import GravedadObraModel


@pytest.mark.parametrize(('criticidad', 'nivel'), [(0, 'Bajo'), (50, 'Bajo'), (51, 'Alto'), (100, 'Alto')])
def test_calcula_nivel_de_gravedad(criticidad, nivel):
    assert _calcular_nivel_gravedad(criticidad) == nivel


def test_criticidad_rechaza_valores_fuera_de_rango():
    with pytest.raises(ValueError):
        GravedadObraModel().set_criticidad(101)


def test_criticidad_acepta_y_normaliza_valor_numerico():
    gravedad = GravedadObraModel()

    gravedad.set_criticidad('75.0')

    assert gravedad.get_criticidad() == 75


class _Cursor:
    def __init__(self, rows=None, rowcount=1):
        self.rows = iter(rows or [])
        self.calls = []
        self.rowcount = rowcount
        self.closed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return next(self.rows, None)

    def fetchall(self):
        return list(self.rows)

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


def test_model_gravedad_getters_setters_y_validaciones():
    g = GravedadObraModel(id_gravedad=4, nivel_gravedad='Bajo', criticidad=10)
    assert (g.get_id(), g.get_nivel_gravedad(), g.get_criticidad()) == (4, 'Bajo', 10)
    g.set_nivel_gravedad('  Media  ')
    g.set_criticidad('50.8')
    assert g.get_nivel_gravedad() == 'Media'
    assert g.get_criticidad() == 50
    for method, val in [('set_nivel_gravedad', 'X'), ('set_criticidad', 'abc'),
                        ('set_criticidad', -1), ('set_criticidad', 101)]:
        with pytest.raises(ValueError):
            getattr(g, method)(val)


def test_registrar_gravedad_reintenta_id_duplicado_y_confirma():
    class Duplicate(Exception):
        errno = 1062

    class CursorRetry(_Cursor):
        def __init__(self):
            super().__init__([(1,), (2,)])

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT') and params[0] == 1:
                raise Duplicate()

    g = GravedadObraModel('Bajo', 20)
    cursor = CursorRetry()
    conn = _Connection(cursor)
    with patch.object(g, 'obtener_conexion_estricta', return_value=conn):
        assert g.registrar_gravedad() == 2
    assert conn.rollbacks == 1 and conn.commits == 1 and conn.closed and cursor.closed
    assert [params[0] for sql, params in cursor.calls if sql.lstrip().startswith('INSERT')] == [1, 2]


def test_lecturas_normalizan_criticidad_y_nivel_y_cierra_recursos():
    g = GravedadObraModel()
    rows = [
        {'id_gravedad': 1, 'nivel_gravedad': 'baja', 'criticidad': 0.75},
        {'id_gravedad': 2, 'nivel_gravedad': 'media', 'criticidad': 'bad'},
    ]
    cursor = _Cursor([{'id_gravedad': 1, 'nivel_gravedad': 'bajo', 'criticidad': 0.4}])
    cursor.fetchall = lambda: rows
    conn = _Connection(cursor)
    with patch.object(g, 'obtener_conexion_estricta', return_value=conn):
        assert g.consultar_activos() == [
            {'id_gravedad': 1, 'nivel_gravedad': 'Bajo', 'criticidad': 75},
            {'id_gravedad': 2, 'nivel_gravedad': 'Alto', 'criticidad': 0},
        ]
    assert conn.closed and cursor.closed

    cursor = _Cursor([{'id_gravedad': 1, 'nivel_gravedad': 'alto', 'criticidad': 0.4}])
    conn = _Connection(cursor)
    with patch.object(g, 'obtener_conexion_estricta', return_value=conn):
        assert g.obtener_gravedad_por_id(1) == {
            'id_gravedad': 1, 'nivel_gravedad': 'Alto', 'criticidad': 40
        }
    assert cursor.calls[0][1] == (1,)


def test_actualizar_eliminar_y_validar_existencia_usan_sql_y_commit():
    g = GravedadObraModel('Alto', 75, id_gravedad=9)
    cursor = _Cursor([(1,), None], rowcount=1)
    conn = _Connection(cursor)
    with patch.object(g, 'obtener_conexion_estricta', return_value=conn):
        assert g.actualizar_gravedad() is True
        assert g.eliminar_gravedad() is True
        assert g.validar_nivel_existente() is True
    assert cursor.calls[0][1] == ('Alto', 75, 1, 9)
    assert cursor.calls[1][1] == (9,)
    assert 'estado = 0' in cursor.calls[1][0]
    assert cursor.calls[2][1] == ('Alto',)
    assert conn.commits == 2 and conn.closed and cursor.closed

    cursor = _Cursor([None])
    conn = _Connection(cursor)
    with patch.object(g, 'obtener_conexion_estricta', return_value=conn):
        assert g.validar_nivel_existente(excluir_id=7) is False
    assert cursor.calls[0][1] == ('Alto', 7)


def test_registrar_gravedad_aborta_despues_de_tres_colisiones_y_limpia():
    class Duplicate(Exception):
        errno = 1062

    class AlwaysDuplicate(_Cursor):
        def __init__(self):
            super().__init__([(1,), (1,), (1,)])

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT'):
                raise Duplicate()

    gravedad = GravedadObraModel('Bajo', 15)
    cursor = AlwaysDuplicate()
    conn = _Connection(cursor)
    with patch.object(gravedad, 'obtener_conexion_estricta', return_value=conn):
        with pytest.raises(ValueError, match='tras 3 intentos'):
            gravedad.registrar_gravedad()
    assert conn.rollbacks == 3 and conn.commits == 0
    assert conn.closed and cursor.closed
