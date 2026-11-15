import pytest
from unittest.mock import patch

from models.model_empleados import EmpleadoModel


def test_valida_y_limpia_nombre_y_cargo():
    empleado = EmpleadoModel()

    empleado.set_nombre_empleado(' Ana Pérez ')
    empleado.set_cargo('Inspector')

    assert empleado.get_nombre_empleado() == 'Ana Pérez'
    assert empleado.get_cargo() == 'Inspector'


@pytest.mark.parametrize(('setter', 'valor'), [
    ('set_nombre_empleado', 'A'),
    ('set_cargo', 'Cargo inventado'),
    ('set_cedula_persona', '123'),
])
def test_rechaza_datos_de_empleado_invalidos(setter, valor):
    with pytest.raises(ValueError):
        getattr(EmpleadoModel(), setter)(valor)


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


def test_getters_setters_validadores_y_normalizacion_de_empleado():
    e = EmpleadoModel()
    e.set_id_empleado(7)
    e.set_nombre_empleado(' Ana Pérez ')
    e.set_cargo(' Inspector ')
    e.set_fecha_ingreso('2025-03-18')
    e.set_gerencia_asignada(' Obras Viales ')
    e.set_cedula_persona('01234567')
    e.set_estado(0)
    assert (e.get_id_empleado(), e.get_nombre_empleado(), e.get_cargo()) == (7, 'Ana Pérez', 'Inspector')
    assert e.get_fecha_ingreso() == '2025-03-18'
    assert e.get_gerencia_asignada() == 'Obras Viales'
    assert e.get_cedula_persona() == 1234567
    assert e.get_estado() == 0
    assert e._validar_telefono('04141234567') and not e._validar_telefono('123')
    assert e._validar_correo('ana@example.org') and not e._validar_correo('ana@')
    assert e._validar_nombre('Ana') and not e._validar_nombre('A1')
    assert e._validar_gerencia('Obras') and not e._validar_gerencia('abc')
    assert e._validar_fecha('2024-12-01') and not e._validar_fecha('01/12/2024')
    assert e._validar_cedula('1234567') and not e._validar_cedula('123')


@pytest.mark.parametrize(('setter', 'value'), [
    ('set_id_empleado', 0), ('set_fecha_ingreso', '01/02/2024'),
    ('set_gerencia_asignada', 'Ops'), ('set_estado', 3),
])
def test_setters_rechazan_valores_fuera_de_regla(setter, value):
    with pytest.raises(ValueError):
        getattr(EmpleadoModel(), setter)(value)


def test_buscar_o_crear_persona_reutiliza_o_inserta_fk_parametrizado():
    e = EmpleadoModel()
    e.set_cedula_persona('12345678')
    existing = _Cursor(one={'id_persona': 12})
    assert e._EmpleadoModel__buscar_o_crear_persona(existing) == 12
    assert existing.calls[0][1] == (12345678,)
    e._EmpleadoModel__direccion = 'Centro'
    inserted = _Cursor(one=None)
    inserted.lastrowid = 15
    # La fila del máximo se sirve en la segunda lectura.
    inserted.fetchone = lambda: next(iter([None]))  # replace below with a sequenced reader
    values = iter([None, {'siguiente_id': 3}])
    inserted.fetchone = lambda: next(values)
    assert e._EmpleadoModel__buscar_o_crear_persona(inserted) == 15
    assert inserted.calls[-1][1] == (3, 12345678, 'Centro', 'No especificado',
                                     'No especificado', '0000000000', 'sin_correo@invilara.gob.ve')


def test_metodos_db_de_empleados_verifican_sql_parametros_y_cierre():
    e = EmpleadoModel()
    rows = [{'id_empleados': 3}]
    cursor = _Cursor(many=rows)
    resultados = iter([(4,), {'id_empleados': 3}, (3,)])
    cursor.fetchone = lambda: next(resultados, None)
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn):
        assert e._EmpleadoModel__obtener_todos_empleados_db(5, 10) == rows
        assert cursor.calls[-1][1] == [5, 10]
        assert e.contar_empleados() == 4
        e.set_id_empleado(3)
        assert e._EmpleadoModel__actualizar_empleado_db() is True
        assert cursor.calls[-1][1][-1] == 3
        assert e._EmpleadoModel__eliminar_logico_db() is True
        assert cursor.calls[-1][1] == (3,)
        assert e._EmpleadoModel__obtener_empleado_por_id_db(3) == {'id_empleados': 3}
        assert cursor.calls[-1][1] == (3,)
        assert e._EmpleadoModel__obtener_empleados_por_cargo_db('Inspector') == rows
        assert cursor.calls[-1][1] == ('Inspector',)
        assert e._EmpleadoModel__validar_empleado_activo_db(3)
    assert conn.closed and cursor.closed and conn.commits == 2


def test_registrar_validacion_publica_y_paginacion_y_catalogo():
    e = EmpleadoModel()
    invalid = {'nombre_empleado': 'AB', 'cargo': 'Inspector', 'fecha_ingreso': '2024-01-01',
               'gerencia_asignada': 'Obras', 'cedula_empleado': '1234567'}
    with pytest.raises(ValueError):
        e.registrar_empleado(invalid)
    valid = dict(invalid, nombre_empleado='Ana Pérez', gerencia_asignada='Obras Viales')
    with patch.object(e, '_EmpleadoModel__guardar_empleado_db', return_value=42) as save:
        assert e.registrar_empleado(valid) == 42
    save.assert_called_once_with()
    with patch.object(e, '_EmpleadoModel__obtener_todos_empleados_db', return_value=[]) as all_db:
        assert e.obtener_empleados_paginados(0, 8) == []
        all_db.assert_called_once_with(limite=8, offset=0)
    assert e.obtener_catalogo_cargos() == list(e.CARGOS_VALIDOS)
    with patch.object(e, '_EmpleadoModel__obtener_empleados_por_cargo_db', return_value=[1]) as cargos:
        assert e.obtener_empleados_por_cargo('Inspector') == [1]
        assert e.obtener_empleados_por_cargo('Fantasma') == []
        cargos.assert_called_once_with('Inspector')


def test_publicos_de_empleado_validan_ids_y_protegen_transiciones():
    e = EmpleadoModel()
    with patch.object(e, '_EmpleadoModel__validar_empleado_activo_db', return_value=True), \
            patch.object(e, '_EmpleadoModel__actualizar_empleado_db', return_value=True), \
            patch.object(e, '_EmpleadoModel__eliminar_logico_db', return_value=True):
        datos = {'id_empleado': '9', 'nombre_empleado': 'Ana Pérez', 'cargo': 'Inspector',
                 'fecha_ingreso': '2025-01-01', 'gerencia_asignada': 'Obras Viales'}
        assert e.actualizar_empleado(datos) is True
        assert e.get_id_empleado() == 9
        assert e.eliminar_empleado_logico('9') is True
    with patch.object(e, '_EmpleadoModel__validar_empleado_activo_db', return_value=False):
        with pytest.raises(ValueError):
            e.actualizar_empleado(datos)
        with pytest.raises(ValueError):
            e.eliminar_empleado_logico('9')
    with patch.object(e, '_EmpleadoModel__obtener_empleado_por_id_db', return_value={'id': 9}) as by_id:
        assert e.obtener_empleado_por_id('9') == {'id': 9}
        assert e.obtener_empleado_por_id('bad') is None
        assert e.obtener_empleado_por_id(0) is None
        by_id.assert_called_once_with(9)
    with patch.object(e, '_EmpleadoModel__validar_empleado_activo_db', return_value=True) as active:
        assert e.validar_empleado_activo('9')
        assert e.validar_empleado_activo('bad') is False
        active.assert_called_once_with(9)


def test_guardar_empleado_db_crea_persona_y_empleado_en_una_transaccion():
    class InsertCursor(_Cursor):
        def __init__(self):
            super().__init__()
            self.results = iter([None, (2,), {'siguiente_id': 3}, {'siguiente_id': 7}])
            self.lastrowid = 11

        def fetchone(self):
            return next(self.results, None)

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT INTO empleados'):
                self.lastrowid = 20

    e = EmpleadoModel()
    e.set_nombre_empleado('Ana Pérez')
    e.set_cargo('Inspector')
    e.set_fecha_ingreso('2025-01-03')
    e.set_gerencia_asignada('Obras Viales')
    e.set_cedula_persona('12345678')
    cursor = InsertCursor()
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn):
        assert e._EmpleadoModel__guardar_empleado_db() == 20
    inserts = [(sql, params) for sql, params in cursor.calls if sql.lstrip().startswith('INSERT')]
    assert len(inserts) == 2
    assert inserts[0][1][1] == 12345678
    assert inserts[1][1] == (3, 'Ana Pérez', 'Inspector', '2025-01-03', 'Obras Viales', 11, 1)
    assert conn.commits == 1 and conn.closed and cursor.closed
