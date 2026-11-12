import pytest

from models.model_ReporteEstadistico import ReporteEstadisticoModel
from models.model_reportesExcel import ReporteExcelModel
from models.model_reportesPDF import ReportePDFModel
from services.filtros_service import FiltrosQueryBuilder


@pytest.mark.parametrize(
    'model',
    [ReporteEstadisticoModel, ReporteExcelModel, ReportePDFModel],
)
def test_report_filters_ignore_unmapped_sql_identifiers(model):
    where = []
    params = []
    attack = "nombre) OR 1=1 --"

    model()._aplicar_filtros(
        where,
        params,
        {attack: 'valor'},
        {'nombre': 'e.nombre'},
    )

    assert where == []
    assert params == []


@pytest.mark.parametrize(
    'model',
    [ReporteEstadisticoModel, ReporteExcelModel, ReportePDFModel],
)
def test_report_filters_bind_values_for_mapped_columns(model):
    where = []
    params = []
    value = "' OR 1=1 --"

    model()._aplicar_filtros(where, params, {'nombre': value}, {'nombre': 'e.nombre'})

    assert where == ['e.nombre LIKE %s']
    assert params == [f'%{value}%']


def test_query_builder_binds_values_and_rejects_untrusted_identifiers():
    builder = FiltrosQueryBuilder('empleados', 'e')
    builder.add_where('e.nombre', 'LIKE', "' OR 1=1 --")

    query, params = builder.get_query('e.id_empleados, e.nombre')

    assert query == 'SELECT e.id_empleados, e.nombre FROM empleados AS e WHERE e.nombre LIKE %s'
    assert params == ["%' OR 1=1 --%"]
    with pytest.raises(ValueError):
        builder.add_where('e.nombre OR 1=1', 'LIKE', 'x')
    with pytest.raises(ValueError):
        FiltrosQueryBuilder('empleados; DROP TABLE usuarios')
    with pytest.raises(ValueError):
        builder.add_join('JOIN roles r ON r.id = e.id OR 1=1')
    with pytest.raises(ValueError):
        builder.build_select('e.nombre; DROP TABLE usuarios')


def test_query_builder_rejects_unsupported_operator_and_invalid_between():
    builder = FiltrosQueryBuilder('empleados')

    with pytest.raises(ValueError):
        builder.add_where('nombre', '= 1 OR 1=1', 'x')
    with pytest.raises(ValueError):
        builder.add_where('id_empleados', 'BETWEEN', '1, 2')


@pytest.mark.parametrize(
    ('operator', 'value', 'clause', 'params'),
    [
        ('LIKE', 'ana', 'e.nombre LIKE %s', ['%ana%']),
        ('DATE_GTE', '2026-01-01', 'DATE(e.fecha) >= %s', ['2026-01-01']),
        ('DATE_LTE', '2026-12-31', 'DATE(e.fecha) <= %s', ['2026-12-31']),
        ('EQUALS', 0, 'e.estado = %s', [0]),
        ('BETWEEN', [2, 8], 'e.id BETWEEN %s AND %s', [2, 8]),
    ],
)
def test_query_builder_supported_filter_operators(operator, value, clause, params):
    builder = FiltrosQueryBuilder('empleados', 'e')
    column = 'e.id' if operator == 'BETWEEN' else ('e.estado' if operator == 'EQUALS' else ('e.fecha' if operator.startswith('DATE') else 'e.nombre'))
    builder.add_where(column, operator, value)

    query, actual_params = builder.get_query('e.id')

    assert query.endswith(f'WHERE {clause}')
    assert actual_params == params


@pytest.mark.parametrize('empty_value', ['', None])
def test_query_builder_ignores_empty_filter_without_emitting_clause(empty_value):
    builder = FiltrosQueryBuilder('usuarios')
    builder.add_where('correo', 'LIKE', empty_value)

    assert builder.get_query('*') == ('SELECT * FROM usuarios', [])


def test_query_builder_builds_join_group_order_and_alias_clauses():
    builder = FiltrosQueryBuilder('usuarios', 'u')
    builder.add_join('LEFT JOIN roles AS r ON r.id_rol = u.id_rol')
    builder.add_where('u.estado', 'EQUALS', 1)
    builder.group_by = 'u.estado'
    builder.order_by = 'u.estado DESC, r.nombre ASC'

    query, params = builder.get_query('u.estado AS estado, r.nombre')

    assert query == (
        'SELECT u.estado AS estado, r.nombre FROM usuarios AS u '
        'LEFT JOIN roles AS r ON r.id_rol = u.id_rol '
        'WHERE u.estado = %s GROUP BY u.estado '
        'ORDER BY u.estado DESC, r.nombre ASC'
    )
    assert params == [1]


@pytest.mark.parametrize(
    ('table', 'alias'),
    [
        ('usuarios; DELETE FROM usuarios', ''),
        ('usuarios', 'u;DROP'),
    ],
)
def test_query_builder_rejects_bad_table_or_alias(table, alias):
    with pytest.raises(ValueError):
        FiltrosQueryBuilder(table, alias)


@pytest.mark.parametrize(
    ('group_by', 'order_by'),
    [
        ('u.estado; DROP TABLE usuarios', None),
        (None, 'u.estado; DROP TABLE usuarios'),
    ],
)
def test_query_builder_rejects_invalid_group_or_order(group_by, order_by):
    builder = FiltrosQueryBuilder('usuarios', 'u')
    builder.group_by = group_by
    builder.order_by = order_by

    with pytest.raises(ValueError):
        builder.build_select('u.id')


def test_query_builder_accepts_valid_join_shapes_and_rejects_non_equality_join():
    builder = FiltrosQueryBuilder('usuarios')
    builder.add_join('INNER JOIN roles r ON r.id_rol = usuarios.id_rol')
    builder.add_join('RIGHT OUTER JOIN departamentos d ON d.id = usuarios.id_departamento')
    assert builder.build_select('usuarios.id') == (
        'SELECT usuarios.id FROM usuarios INNER JOIN roles r ON r.id_rol = usuarios.id_rol '
        'RIGHT OUTER JOIN departamentos d ON d.id = usuarios.id_departamento'
    )

    with pytest.raises(ValueError):
        builder.add_join('JOIN roles r ON r.id_rol > usuarios.id_rol')


@pytest.mark.parametrize(
    ('model', 'filters', 'mapping', 'expected_where', 'expected_params'),
    [
        (ReporteEstadisticoModel, {}, {'nombre': 'e.nombre'}, [], []),
        (ReporteEstadisticoModel, {'tipo_reporte': 'obras', 'agrupacion': 'mes'}, {}, [], []),
        (ReporteEstadisticoModel, {'correo_dominio': 'x.test'}, {'correo_dominio': 'u.correo'}, ['u.correo LIKE %s'], ['%x.test%']),
        (ReporteEstadisticoModel, {'fecha_creacion_desde': '2026-02-01', 'fecha_creacion_hasta': '2026-02-28'},
         {'fecha_creacion_desde': 'o.fecha', 'fecha_creacion_hasta': 'o.fecha'},
         ['DATE(o.fecha) >= %s', 'DATE(o.fecha) <= %s'], ['2026-02-01', '2026-02-28']),
        (ReporteEstadisticoModel, {'porcentaje_avance_min': 0, 'porcentaje_avance_max': 85},
         {}, ['o.porcentaje_avance_obra >= %s', 'o.porcentaje_avance_obra <= %s'], [0, 85]),
        (ReporteEstadisticoModel, {'sector': 'norte', 'ambito': 'rural'},
         {}, ['com.sector LIKE %s', 'com.ambito LIKE %s'], ['%norte%', '%rural%']),
        (ReporteEstadisticoModel, {'estado': '1'}, {'estado': 'e.estado'}, ['e.estado = %s'], [1]),
        (ReporteEstadisticoModel, {'estado': 'Activo'}, {'estado': 'e.estado'}, ['e.estado LIKE %s'], ['%Activo%']),
        (ReporteExcelModel, {'nombre_solicitante': 'Ana'}, {},
         ['(COALESCE(part.nombre, inst.razon_social, com.nombre_comunidad) LIKE %s)'], ['%Ana%']),
        (ReporteExcelModel, {'titulo_obra': 'Puente'}, {},
         ['o.titulo_obra LIKE %s'], ['%Puente%']),
        (ReporteExcelModel, {'porcentaje_avance_min': 30}, {'porcentaje_avance_min': 'o.porcentaje_avance_min'},
         ['o.porcentaje_avance >= %s'], [30]),
        (ReporteExcelModel, {'estado': '0'}, {'estado': 'e.estado'}, ['e.estado = %s'], [0]),
        (ReporteExcelModel, {'estado': 'Activo'}, {'estado': 'e.estado'}, [], []),
        (ReportePDFModel, {'ambito': 'urbano'}, {}, ['com.ambito LIKE %s'], ['%urbano%']),
        (ReportePDFModel, {'correo_dominio': 'example'}, {'correo_dominio': 'p.correo'}, ['p.correo LIKE %s'], ['%example%']),
    ],
)
def test_report_filter_helper_maps_only_supported_filters(
    model, filters, mapping, expected_where, expected_params
):
    where = []
    params = []

    model()._aplicar_filtros(where, params, filters, mapping)

    assert where == expected_where
    assert params == expected_params


@pytest.mark.parametrize(
    ('model', 'filters', 'mapping'),
    [
        (ReporteEstadisticoModel, {'nombre': '', 'otra': 'x'}, {'nombre': 'e.nombre'}),
        (ReporteExcelModel, {'nombre': '', 'sin_mapa': 'ignored'}, {'nombre': 'e.nombre'}),
        (ReportePDFModel, {'sin_mapa': 'ignored'}, {}),
    ],
)
def test_report_filter_helper_ignores_empty_and_unmapped_filter_values(model, filters, mapping):
    where = []
    params = []

    model()._aplicar_filtros(where, params, filters, mapping)

    assert where == []
    assert params == []
