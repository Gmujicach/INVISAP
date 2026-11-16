"""Focused behavior tests for report, user, security, and backup models."""
import os
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest
from werkzeug.security import check_password_hash

from models import model_seguridad
from models.model_ReporteEstadistico import ReporteEstadisticoModel
from models.model_reportesExcel import ReporteExcelModel
from models.model_reportesPDF import ReportePDFModel
from models.model_respaldo import RespaldoModel
from models.model_seguridad import ModuloModel, RolModel, RolPermisoModel
from models.model_usuarios import DEFAULT_AVATAR, UsuarioModel


def db_pair(*, rows=None, row=None, rowcount=1, lastrowid=23, database='security_test'):
    cursor = MagicMock()
    cursor.fetchall.return_value = [] if rows is None else rows
    cursor.fetchone.return_value = row
    cursor.rowcount = rowcount
    cursor.lastrowid = lastrowid
    connection = MagicMock()
    connection.cursor.return_value = cursor
    connection.database = database
    return connection, cursor


def attach_connection(monkeypatch, model, connection, method='obtener_conexion_seguridad'):
    monkeypatch.setattr(model, method, lambda: connection)


# Statistical report filters and query resource management.

@pytest.mark.parametrize('model_type', [ReporteEstadisticoModel, ReporteExcelModel, ReportePDFModel])
def test_report_constructor_and_filtered_query_helper(model_type, monkeypatch):
    model = model_type()
    connection, cursor = db_pair(rows=[{'value': 7}])
    method = 'obtener_conexion_estricta'
    monkeypatch.setattr(model, method, lambda: connection)

    assert model._ejecutar_query('SELECT %s', [7]) == [{'value': 7}]
    cursor.execute.assert_called_once_with('SELECT %s', [7])
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('model_type', [ReporteExcelModel, ReportePDFModel])
def test_report_query_helper_selects_security_database_and_closes_on_error(model_type, monkeypatch):
    model = model_type()
    connection, cursor = db_pair()
    cursor.execute.side_effect = RuntimeError('query failure')
    monkeypatch.setattr(model, 'obtener_conexion_seguridad', lambda: connection)

    with pytest.raises(RuntimeError, match='query failure'):
        model._ejecutar_query('SELECT 1', db_name='seguridad')
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_excel_general_statistics_uses_three_aggregates_and_closes(monkeypatch):
    model = ReporteExcelModel()
    connection, cursor = db_pair()
    cursor.fetchone.side_effect = [
        {'hombres': 2, 'mujeres': 3, 'total': 5},
        {'promedio_salarial': Decimal('125.50')},
        {'total_pub': 8},
    ]
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: connection)

    assert model.obtener_estadisticas_generales() == {
        'empleados': {'hombres': 2, 'mujeres': 3, 'total': 5},
        'promedio_salarial': Decimal('125.50'),
        'publicaciones': 8,
    }
    assert cursor.execute.call_count == 3
    assert 'tbl_empleados' in cursor.execute.call_args_list[0].args[0]
    assert 'AVG(salario_empleado)' in cursor.execute.call_args_list[1].args[0]
    assert 'tbl_publicaciones' in cursor.execute.call_args_list[2].args[0]
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('model_type', [ReporteEstadisticoModel, ReporteExcelModel, ReportePDFModel])
def test_report_filter_operator_branches(model_type):
    model = model_type()
    where, params = [], []
    model._aplicar_filtros(
        where, params,
        {
            'correo_dominio': 'example.test',
            'fecha_inicio_desde': '2026-01-02',
            'fecha_fin_hasta': '2026-02-03',
            'porcentaje_avance_min': 0,
            'porcentaje_avance_max': 100,
            'estado': '1',
            'unknown': 'ignored',
            'empty': '',
        },
        {
            'correo_dominio': 'p.correo',
            'fecha_inicio_desde': 'o.inicio',
            'fecha_fin_hasta': 'o.fin',
            'porcentaje_avance_min': 'o.avance_min',
            'porcentaje_avance_max': 'o.avance_max',
            'estado': 'o.estado',
            'empty': 'o.empty',
        },
    )
    assert where == [
        'p.correo LIKE %s',
        'DATE(o.inicio) >= %s',
        'DATE(o.fin) <= %s',
        ('o.porcentaje_avance_obra >= %s' if model_type is ReporteEstadisticoModel else 'o.avance >= %s'),
        ('o.porcentaje_avance_obra <= %s' if model_type is ReporteEstadisticoModel else 'o.avance <= %s'),
        'o.estado = %s',
    ]
    assert params == ['%example.test%', '2026-01-02', '2026-02-03', 0, 100, 1]


@pytest.mark.parametrize(
    'model_type,filters,expected_where,expected_params',
    [
        (ReporteEstadisticoModel, {'tipo_reporte': 'x', 'agrupacion': 'mes', 'bad': 'v'}, [], []),
        (ReporteEstadisticoModel, {'estado': 'archivado'}, ['x.estado LIKE %s'], ['%archivado%']),
        (ReporteEstadisticoModel, {'sector': 'norte', 'ambito': 'rural'}, ['com.sector LIKE %s', 'com.ambito LIKE %s'], ['%norte%', '%rural%']),
        (ReporteExcelModel, {'nombre_solicitante': 'Ana', 'sector': 'norte', 'ambito': 'rural', 'titulo_obra': 'Puente'}, [
            '(COALESCE(part.nombre, inst.razon_social, com.nombre_comunidad) LIKE %s)',
            'com.sector LIKE %s', 'com.ambito LIKE %s', 'o.titulo_obra LIKE %s',
        ], ['%Ana%', '%norte%', '%rural%', '%Puente%']),
        (ReportePDFModel, {'estado': 'otro'}, [], []),
    ],
)
def test_report_filter_allowlists_and_special_fields(model_type, filters, expected_where, expected_params):
    where, params = [], []
    model_type()._aplicar_filtros(where, params, filters, {'estado': 'x.estado'})
    assert where == expected_where
    assert params == expected_params


REPORT_QUERY_CASES = [
    (ReporteExcelModel, 'obtener_solicitudes_reporte', 'solicitudes s', {'tipo_solicitud': 'Petición'}, ['s.tipo_solicitud LIKE %s']),
    (ReporteExcelModel, 'obtener_solicitantes_reporte', 'particular pa', {'nombre': 'Ada'}, ['pa.nombre LIKE %s']),
    (ReporteExcelModel, 'obtener_empleados_reporte', 'empleados e', {'fecha_ingreso_desde': '2026-01-01'}, ['DATE(e.fecha_ingreso) >= %s']),
    (ReporteExcelModel, 'obtener_usuarios_reporte', 'FROM usuarios', {'correo': 'a@b.test'}, ['correo LIKE %s']),
    (ReporteExcelModel, 'obtener_contrataciones_reporte', 'contratacion c', {'fecha_registro_hasta': '2026-02-01'}, ['DATE(c.fecha_registro) <= %s']),
    (ReporteExcelModel, 'obtener_obras_reporte', 'obra o', {'titulo_obra': 'Camino'}, ['o.titulo_obra LIKE %s']),
    (ReporteExcelModel, 'obtener_publicaciones_reporte', 'publicacion', {'fecha_publicacion_desde': '2026-03-04'}, ['DATE(fecha_publicacion) >= %s']),
    (ReporteExcelModel, 'obtener_avances_reporte', 'avance a', {'porcentaje_avance_min': 0}, ['a.porcentaje_avance >= %s']),
    (ReporteExcelModel, 'obtener_inspecciones_reporte', 'inspeccion i', {'tipo_inspeccion': 'Final'}, ['i.tipo_inspeccion LIKE %s']),
    (ReporteExcelModel, 'obtener_evidencias_reporte', 'evidencia ev', {'etapa': 'Cierre'}, ['ev.etapa LIKE %s']),
    (ReporteExcelModel, 'obtener_gravedades_reporte', 'gravedad_obra g', {'criticidad': 'Alta'}, ['g.criticidad LIKE %s']),
    (ReportePDFModel, 'obtener_solicitudes', 'solicitudes s', {'sector': 'Este'}, ['com.sector LIKE %s']),
    (ReportePDFModel, 'obtener_solicitantes', 'particular pa', {'correo_dominio': 'acme.test'}, ['p.correo LIKE %s']),
    (ReportePDFModel, 'obtener_empleados', 'empleados e', {'cargo': 'Inspector'}, ['e.cargo LIKE %s']),
    (ReportePDFModel, 'obtener_usuarios', 'FROM usuarios', {'rol': 'Usuario'}, ['rol LIKE %s']),
    (ReportePDFModel, 'obtener_contrataciones', 'contratacion c', {'numero_contrato': 'C-8'}, ['c.numero_contrato LIKE %s']),
    (ReportePDFModel, 'obtener_obras', 'obra o', {'fecha_fin_hasta': '2026-12-31'}, ['DATE(o.fecha_fin) <= %s']),
    (ReportePDFModel, 'obtener_publicaciones_reporte', 'publicacion', {'tipo_publicacion': 'Aviso'}, ['tipo_publicacion LIKE %s']),
]


@pytest.mark.parametrize('model_type,method,table,filters,where_parts', REPORT_QUERY_CASES)
def test_each_report_data_method_builds_a_bound_query(model_type, method, table, filters, where_parts):
    expected = [{'row': method}]
    model = model_type()
    calls = []
    model._ejecutar_query = lambda query, params, **kwargs: calls.append((query, params, kwargs)) or expected

    assert getattr(model, method)(filters) is expected
    assert len(calls) == 1
    query, params, kwargs = calls[0]
    assert table in query
    for part in where_parts:
        assert part in query
    assert params == [next(iter(filters.values())) if 'fecha_' in next(iter(filters)) or next(iter(filters)) == 'porcentaje_avance_min' else f"%{next(iter(filters.values()))}%"]
    assert 'ORDER BY' in query
    if method in ('obtener_usuarios', 'obtener_usuarios_reporte'):
        assert kwargs == {'db_name': 'seguridad'}
    else:
        assert kwargs == {}


@pytest.mark.parametrize(
    'agrupacion,expression',
    [('mes', "DATE_FORMAT(s.fecha, '%Y-%m')"), ('semana', "DATE_FORMAT(s.fecha, '%x-W%v')"), ('dia', 'DATE(s.fecha)')],
)
def test_estadisticas_solicitudes_grouping_and_geography_queries(agrupacion, expression, monkeypatch):
    model = ReporteEstadisticoModel()
    connection, cursor = db_pair()
    cursor.fetchall.side_effect = [[{'label': 'x', 'valor': 2}] for _ in range(7)]
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: connection)

    result = model.obtener_estadisticas_solicitudes({'municipio': 'Centro'}, agrupacion)

    assert set(result) == {'por_fecha' if agrupacion == 'dia' else ('por_mes' if agrupacion == 'mes' else 'por_semana'),
                           'por_tipo', 'por_estatus', 'por_municipio', 'por_parroquia', 'por_sector'}
    assert len(cursor.execute.call_args_list) == 6
    assert expression in cursor.execute.call_args_list[0].args[0]
    assert all(c.args[1] == ['%Centro%'] for c in cursor.execute.call_args_list)
    assert 'com.sector IS NOT NULL' in cursor.execute.call_args_list[-1].args[0]
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    'method,groups,expression,count',
    [
        ('obtener_estadisticas_obras', ['por_fecha', 'por_estado', 'por_contratista', 'por_ubicacion', 'por_semaforo_color', 'por_avance'], 'COALESCE(o.fecha_inicio, o.fecha_fin)', 6),
        ('obtener_estadisticas_empleados', ['por_cargo', 'por_gerencia', 'por_estado', 'por_fecha_ingreso'], 'e.fecha_ingreso', 4),
        ('obtener_estadisticas_contrataciones', ['por_tipo', 'por_modalidad', 'por_objeto', 'por_estado', 'por_empresa', 'por_fecha'], 'c.fecha_registro', 6),
        ('obtener_estadisticas_publicaciones', ['por_tipo', 'por_autor', 'por_fecha'], 'fecha_publicacion', 3),
    ],
)
@pytest.mark.parametrize('agrupacion,format_fragment', [
    ('mes', '%Y-%m'), ('semana', '%x-W%v'), ('dia', 'DATE('),
])
def test_estadisticas_methods_grouping_filters_and_results(method, groups, expression, count, agrupacion, format_fragment, monkeypatch):
    model = ReporteEstadisticoModel()
    connection, cursor = db_pair()
    cursor.fetchall.side_effect = [[{'label': idx, 'valor': idx}] for idx in range(count)]
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: connection)

    result = getattr(model, method)({'titulo_obra': 'Puente'} if method.endswith('obras') else {}, agrupacion)

    assert set(result) == set(groups)
    assert len(cursor.execute.call_args_list) == count
    first_sql = cursor.execute.call_args_list[0].args[0]
    sql_statements = [c.args[0] for c in cursor.execute.call_args_list]
    assert any(expression in sql for sql in sql_statements)
    date_sql = next(sql for sql in sql_statements if expression in sql)
    assert format_fragment in date_sql
    expected_params = ['%Puente%'] if method.endswith('obras') else []
    assert all(c.args[1] == expected_params for c in cursor.execute.call_args_list)
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_estadisticas_query_exception_still_closes_resources(monkeypatch):
    model = ReporteEstadisticoModel()
    connection, cursor = db_pair()
    cursor.execute.side_effect = RuntimeError('database unavailable')
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: connection)
    with pytest.raises(RuntimeError, match='database unavailable'):
        model.obtener_estadisticas_publicaciones()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# User model constructor, accessors, SQL methods, and private persistence.

def test_usuario_constructor_getters_and_setters_round_trip():
    model = UsuarioModel(5, 'Mara', 'mara@example.test', 'hash', 'V-5', 'Editor', 'avatar.png')
    assert (model.get_id(), model.get_nombre(), model.get_correo(), model.get_contrasena(),
            model.get_cedula(), model.get_rol(), model.get_avatar()) == (
        5, 'Mara', 'mara@example.test', 'hash', 'V-5', 'Editor', 'avatar.png')
    for setter, getter, value in [
        ('set_nombre', 'get_nombre', 'Luz'),
        ('set_correo', 'get_correo', 'luz@example.test'),
        ('set_contrasena', 'get_contrasena', 'new-hash'),
        ('set_cedula', 'get_cedula', 'V-6'),
        ('set_rol', 'get_rol', 'Admin'),
        ('set_avatar', 'get_avatar', None),
    ]:
        getattr(model, setter)(value)
        assert getattr(model, getter)() == value
    assert UsuarioModel().get_rol() == 'Usuario'


@pytest.mark.parametrize(
    'method,args,sql_fragment,params,fetch_kind,expected',
    [
        ('buscar_por_nombre', ('Ana',), 'WHERE nombre = %s', ('Ana',), 'one', {'id_usuarios': 1}),
        ('buscar_por_email', ('a@b.test',), 'WHERE correo = %s', ('a@b.test',), 'one', {'id_usuarios': 1}),
        ('validar_duplicados', ('a@b.test', 'V1'), 'correo = %s OR cedula_usuario = %s', ('a@b.test', 'V1'), 'one', True),
        ('listar_todos', (), 'FROM usuarios', None, 'all', [{'avatar': None}, {'avatar': 'given.png'}]),
        ('buscar_por_id', (8,), 'WHERE id_usuarios = %s', (8,), 'one', {'avatar': None}),
        ('buscar_por_id_con_contrasena', (8,), 'contrasena FROM usuarios', (8,), 'one', {'avatar': None, 'contrasena': 'hash'}),
    ],
)
def test_usuario_read_methods_bind_sql_and_transform_results(method, args, sql_fragment, params, fetch_kind, expected, monkeypatch):
    model = UsuarioModel()
    connection, cursor = db_pair(rows=expected if fetch_kind == 'all' else None, row=expected if fetch_kind == 'one' else None)
    attach_connection(monkeypatch, model, connection)

    result = getattr(model, method)(*args)

    if method == 'validar_duplicados':
        assert result is True
    elif method == 'listar_todos':
        assert result == [{'avatar': DEFAULT_AVATAR}, {'avatar': 'given.png'}]
    elif method in ('buscar_por_id', 'buscar_por_id_con_contrasena'):
        assert result['avatar'] == DEFAULT_AVATAR
        if method.endswith('con_contrasena'):
            assert result['contrasena'] == 'hash'
    else:
        assert result == expected
    execute_args = cursor.execute.call_args.args
    actual_sql, actual_params = execute_args[0], execute_args[1] if len(execute_args) > 1 else None
    assert sql_fragment in actual_sql
    if params is not None:
        assert actual_params == params
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    'method,args,expected',
    [('buscar_por_nombre', ('Ana',), None), ('buscar_por_email', ('x',), None),
     ('validar_duplicados', ('x', 'y'), False), ('listar_todos', (), []),
     ('buscar_por_id', (1,), None), ('buscar_por_id_con_contrasena', (1,), None)],
)
def test_usuario_read_methods_handle_missing_connection(method, args, expected, monkeypatch):
    model = UsuarioModel()
    monkeypatch.setattr(model, 'obtener_conexion_seguridad', lambda: None)
    assert getattr(model, method)(*args) == expected


def test_usuario_incluir_hashes_password_and_registers(monkeypatch):
    model = UsuarioModel()
    connection, cursor = db_pair()
    attach_connection(monkeypatch, model, connection)
    assert model.incluir({'nombre': 'Iris', 'correo': 'i@example.test', 'cedula_usuario': 'V8', 'pass_user': 'secret'})
    execute_args = cursor.execute.call_args.args
    sql, params = execute_args[0], execute_args[1] if len(execute_args) > 1 else None
    assert 'INSERT INTO usuarios' in sql
    assert params[:2] == ('Iris', 'i@example.test')
    assert check_password_hash(params[2], 'secret')
    assert params[3:] == ('V8', 'Usuario')
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('password,sql_fragment', [('secret', 'contrasena=%s'), (None, 'WHERE id_usuarios=%s')])
def test_usuario_actualizar_selects_password_or_no_password_sql(password, sql_fragment, monkeypatch):
    model = UsuarioModel()
    connection, cursor = db_pair()
    attach_connection(monkeypatch, model, connection)
    assert model.actualizar(9, 'Noa', 'n@example.test', 'V9', 'Editor', password)
    execute_args = cursor.execute.call_args.args
    sql, params = execute_args[0], execute_args[1] if len(execute_args) > 1 else None
    assert sql_fragment in sql
    assert params[-1] == 9
    if password:
        assert check_password_hash(params[-2], password)
    else:
        assert params == ('Noa', 'n@example.test', 'V9', 'Editor', 9)
    connection.commit.assert_called_once()


def test_usuario_private_insert_update_delete_failure_and_rowcount(monkeypatch):
    model = UsuarioModel(4, 'A', 'a@b', 'hash', 'V4', 'Admin')
    connection, cursor = db_pair(rowcount=0)
    attach_connection(monkeypatch, model, connection)
    assert model._UsuarioModel__registrar_db() is False
    assert model._UsuarioModel__actualizar_db() is False
    assert model._UsuarioModel__eliminar_fisico_db() is True
    assert cursor.execute.call_args.args[1] == (4,)
    assert connection.commit.call_count == 3
    assert cursor.close.call_count == connection.close.call_count == 3
    monkeypatch.setattr(model, 'obtener_conexion_seguridad', lambda: None)
    assert model._UsuarioModel__registrar_db() is False
    assert model._UsuarioModel__actualizar_db() is False
    assert model._UsuarioModel__eliminar_fisico_db() is False


@pytest.mark.parametrize('id_value,expected_method', [(None, '__registrar_db'), (5, '__actualizar_db')])
def test_usuario_guardar_routes_by_identity(id_value, expected_method, monkeypatch):
    model = UsuarioModel(id_usuarios=id_value)
    called = []
    monkeypatch.setattr(model, '_UsuarioModel__registrar_db', lambda: called.append('insert') or True)
    monkeypatch.setattr(model, '_UsuarioModel__actualizar_db', lambda: called.append('update') or True)
    assert model.guardar() is True
    assert called == ['insert' if expected_method == '__registrar_db' else 'update']


@pytest.mark.parametrize('explicit_id,stored_id,expected', [(None, None, False), (None, 4, True), (8, None, True)])
def test_usuario_eliminar_requires_and_uses_id(explicit_id, stored_id, expected, monkeypatch):
    model = UsuarioModel(id_usuarios=stored_id)
    calls = []
    monkeypatch.setattr(model, '_UsuarioModel__eliminar_fisico_db', lambda: calls.append(model.get_id()) or True)
    assert model.eliminar(explicit_id) is expected
    assert calls == ([explicit_id or stored_id] if expected else [])


@pytest.mark.parametrize(
    'row,expected',
    [({'id_usuarios': 7}, True), (None, False)],
)
def test_usuario_existe_y_activo_uses_id_and_closes_resources(row, expected, monkeypatch):
    connection, cursor = db_pair(row=row)
    monkeypatch.setattr(
        UsuarioModel,
        'obtener_conexion_seguridad',
        staticmethod(lambda: connection),
    )

    assert UsuarioModel.existe_y_activo(7) is expected

    cursor.execute.assert_called_once_with(
        'SELECT id_usuarios FROM usuarios WHERE id_usuarios = %s',
        (7,),
    )
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# Security module/role/permission model CRUD, validation, SQL, and transactions.

def test_asegurar_tabla_permisos_usuario_executes_migrations_and_closes(monkeypatch):
    connection, cursor = db_pair()
    monkeypatch.setattr(model_seguridad._SeguridadDatabase, 'obtener_conexion_seguridad', staticmethod(lambda: connection))
    model_seguridad.asegurar_tabla_permisos_usuario()
    assert cursor.execute.call_count == 3
    assert 'CREATE TABLE IF NOT EXISTS usuarios_permisos' in cursor.execute.call_args_list[0].args[0]
    assert 'INSERT IGNORE INTO roles_permisos' in cursor.execute.call_args_list[2].args[0]
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    'kwargs',
    [
        {'nombre': 'obras', 'url': '/obras'},
        {'nombre': 'modulo_2', 'url': '/x', 'tipo': 'Transaccional', 'descripcion': 'Descripción #1'},
        {'nombre': 'x' * 40, 'url': '/', 'tipo': 'Enlace'},
    ],
)
def test_modulo_validation_accepts_valid_boundaries(kwargs):
    defaults = {'nombre': 'obras', 'url': '/obras'}
    defaults.update(kwargs)
    assert ModuloModel(**defaults)._validar() is None


@pytest.mark.parametrize(
    'kwargs',
    [
        {'nombre': 'O', 'url': '/'},
        {'nombre': 'Upper', 'url': '/'},
        {'nombre': 'ok', 'url': 'no-slash'},
        {'nombre': 'ok', 'url': '/', 'tipo': 'Unknown'},
        {'nombre': 'ok', 'url': '/', 'descripcion': 'bad;sql'},
    ],
)
def test_modulo_validation_rejects_bad_fields(kwargs):
    with pytest.raises(ValueError):
        ModuloModel(**kwargs)._validar()


def test_rol_validation_accepts_trimmed_name_and_rejects_invalid_name():
    assert RolModel(nombre='  José Pérez  ')._validar() is None
    for name in (None, 'AB', 'Admin123', 'x' * 21):
        with pytest.raises(ValueError):
            RolModel(nombre=name)._validar()


@pytest.mark.parametrize(
    'model,method,args,expected_fragment,expected_params,fetch,expected',
    [
        (ModuloModel(nombre='obras', url='/obras'), 'registrar', (), 'INSERT INTO modulos', ('obras', None, '/obras', 'CRUD', None, 0, 1), None, 23),
        (ModuloModel(id_modulo=4, nombre='obras', url='/obras'), 'actualizar', (), 'UPDATE modulos', ('obras', None, '/obras', 'CRUD', None, 0, 1, 4), None, True),
        (ModuloModel(id_modulo=4), 'eliminar', (), 'UPDATE modulos SET estado = 0', (4,), None, True),
        (ModuloModel(), 'consultar_activos', (), 'WHERE estado = 1', None, 'all', [{'id_modulo': 1}]),
        (ModuloModel(), 'obtener_por_id', (4,), 'WHERE id_modulo = %s', (4,), 'one', {'id_modulo': 4}),
        (ModuloModel(nombre='obras'), 'validar_nombre_existente', (), 'WHERE nombre = %s AND estado = 1', ('obras',), 'one', True),
        (ModuloModel(nombre='obras'), 'validar_nombre_existente', (8,), 'id_modulo <> %s', ('obras', 8), 'one', True),
    ],
)
def test_modulo_persistence_methods(model, method, args, expected_fragment, expected_params, fetch, expected, monkeypatch):
    connection, cursor = db_pair(
        rows=[{'id_modulo': 1}],
        row={'id_modulo': 4} if method == 'obtener_por_id' else ({'found': 1} if fetch == 'one' else None),
    )
    attach_connection(monkeypatch, model, connection)
    if method == 'actualizar' or method == 'eliminar':
        cursor.rowcount = 1
    result = getattr(model, method)(*args)
    if method == 'consultar_activos':
        assert result == [{'id_modulo': 1}]
    elif method == 'obtener_por_id':
        assert result == {'id_modulo': 4}
    elif method == 'validar_nombre_existente':
        assert result is True
    else:
        assert result == expected
    execute_args = cursor.execute.call_args.args
    sql, params = execute_args[0], execute_args[1] if len(execute_args) > 1 else None
    assert expected_fragment in sql
    if expected_params is not None:
        assert params == expected_params
    if method in ('registrar', 'actualizar', 'eliminar'):
        connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    'method,args,fragment,params,fetch,expected',
    [
        ('registrar', (), 'INSERT INTO roles', ('Admin', None, 1), None, 23),
        ('consultar_activos', (), 'WHERE estado = 1', None, 'all', [{'id_rol': 2}]),
        ('obtener_por_id', (2,), 'WHERE id_rol = %s', (2,), 'one', {'id_rol': 2}),
        ('actualizar', (), 'UPDATE roles SET nombre', ('Admin', None, 1, 2), None, True),
        ('eliminar', (), 'UPDATE roles SET estado = 0', (2,), None, True),
        ('validar_nombre_existente', (), 'WHERE nombre = %s AND estado = 1', ('Admin',), 'one', True),
        ('validar_nombre_existente', (9,), 'id_rol <> %s', ('Admin', 9), 'one', True),
        ('existe_super_usuario_activo', (), 'nombre = %s AND estado = 1', ('Super Usuario',), 'one', True),
        ('existe_super_usuario_activo', (9,), 'id_rol <> %s', ('Super Usuario', 9), 'one', True),
        ('obtener_super_usuario_id', (), 'nombre = %s AND estado = 1', ('Super Usuario',), 'one_id', 4),
        ('obtener_usuarios_por_rol', (), 'WHERE rol = %s AND estado = 1', ('Admin',), 'all', [{'id_usuarios': 3}]),
    ],
)
def test_rol_database_methods(method, args, fragment, params, fetch, expected, monkeypatch):
    model = RolModel(nombre=' Admin ', id_rol=2)
    role_row = {'id_rol': 2} if method == 'obtener_por_id' else {'found': 1}
    role_rows = [{'id_usuarios': 3}] if method == 'obtener_usuarios_por_rol' else [{'id_rol': 2}]
    connection, cursor = db_pair(
        rows=role_rows if fetch == 'all' else None,
        row=({'id_rol': 4} if fetch == 'one_id' else role_row) if fetch in ('one', 'one_id') else None,
    )
    attach_connection(monkeypatch, model, connection)
    result = getattr(model, method)(*args)
    if fetch == 'all':
        assert result == expected
    elif fetch == 'one_id':
        assert result == expected
    elif method == 'obtener_por_id':
        assert result == {'id_rol': 2}
    elif fetch == 'one':
        assert result is True
    else:
        assert result == expected
    execute_args = cursor.execute.call_args.args
    sql, actual_params = execute_args[0], execute_args[1] if len(execute_args) > 1 else None
    assert fragment in sql
    if params is not None:
        assert actual_params == params
    if method in ('registrar', 'actualizar', 'eliminar'):
        connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_rol_super_usuario_id_returns_none_when_missing(monkeypatch):
    model = RolModel()
    connection, cursor = db_pair(row=None)
    attach_connection(monkeypatch, model, connection)
    assert model.obtener_super_usuario_id() is None


@pytest.mark.parametrize(
    'model_type,method,args',
    [
        (ModuloModel, 'validar_nombre_existente', ()),
        (ModuloModel, 'validar_nombre_existente', (9,)),
        (RolModel, 'validar_nombre_existente', ()),
        (RolModel, 'validar_nombre_existente', (9,)),
        (RolModel, 'existe_super_usuario_activo', ()),
        (RolModel, 'existe_super_usuario_activo', (9,)),
    ],
)
def test_security_duplicate_lookups_return_false_when_no_active_row(model_type, method, args, monkeypatch):
    model = model_type(nombre='obras' if model_type is ModuloModel else 'Admin')
    connection, cursor = db_pair(row=None)
    attach_connection(monkeypatch, model, connection)
    assert getattr(model, method)(*args) is False
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    'method,args,sql_fragment,params,fetch,expected',
    [
        ('obtener_por_rol', (5,), 'LEFT JOIN roles_permisos', (5,), 'all', [{'puede_ver': 0}]),
        ('obtener_nombres_modulos_por_rol', ('Editor',), 'SELECT DISTINCT m.nombre', ('Editor',), 'names', ['obras']),
        ('obtener_permiso', ('Editor', 11, 'obras'), 'LEFT JOIN usuarios_permisos', ('Editor', 11, 'obras'), 'permission', {        'puede_ver': 0, 'puede_crear': 0, 'puede_editar': 1, 'puede_eliminar': 1}),
        ('obtener_permisos_usuario', (11,), 'FROM usuarios_permisos up', (11,), 'all', [{'id_modulo': 2}]),
    ],
)
def test_rol_permiso_queries_and_effective_overrides(method, args, sql_fragment, params, fetch, expected, monkeypatch):
    model = RolPermisoModel()
    row = None
    rows = expected if fetch == 'all' else None
    if fetch == 'names':
        rows = [{'nombre': 'obras'}]
    if fetch == 'permission':
        row = {
            'puede_ver': 1, 'puede_crear': 0, 'puede_editar': 1, 'puede_eliminar': 0,
            'usuario_puede_ver': 0, 'usuario_puede_crear': None,
            'usuario_puede_editar': None, 'usuario_puede_eliminar': 1,
        }
    connection, cursor = db_pair(rows=rows, row=row)
    attach_connection(monkeypatch, model, connection)
    result = getattr(model, method)(*args)
    if fetch == 'permission':
        assert result == expected
    else:
        assert result == expected
    sql, actual_params = cursor.execute.call_args.args
    assert sql_fragment in sql
    assert actual_params == params
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_rol_permiso_missing_module_returns_none(monkeypatch):
    model = RolPermisoModel()
    connection, cursor = db_pair(row=None)
    attach_connection(monkeypatch, model, connection)
    assert model.obtener_permiso('unknown', 3, 'missing') is None
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('method,identifier', [
    ('guardar_permisos_usuario', 6),
    ('guardar_permisos', 7),
])
def test_guardar_empty_permission_list_soft_deletes_and_commits(method, identifier, monkeypatch):
    model = RolPermisoModel()
    connection, cursor = db_pair()
    attach_connection(monkeypatch, model, connection)
    assert getattr(model, method)(identifier, []) is True
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (identifier,)
    connection.commit.assert_called_once()


@pytest.mark.parametrize('method,identifier,update_table', [
    ('guardar_permisos_usuario', 6, 'usuarios_permisos'),
    ('guardar_permisos', 7, 'roles_permisos'),
])
def test_guardar_permisos_replaces_state_normalizes_booleans_and_commits(method, identifier, update_table, monkeypatch):
    model = RolPermisoModel()
    connection, cursor = db_pair()
    attach_connection(monkeypatch, model, connection)
    permiso = {'id_modulo': 4, 'puede_ver': 'yes', 'puede_crear': 0, 'puede_editar': 1, 'puede_eliminar': None}
    assert getattr(model, method)(identifier, [permiso]) is True
    assert cursor.execute.call_count == 2
    assert f'UPDATE {update_table} SET estado = 0' in cursor.execute.call_args_list[0].args[0]
    insert_sql, insert_params = cursor.execute.call_args_list[1].args
    assert 'ON DUPLICATE KEY UPDATE' in insert_sql
    assert insert_params == (identifier, 4, 1, 0, 1, 0)
    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('method,identifier', [('guardar_permisos_usuario', 6), ('guardar_permisos', 7)])
def test_guardar_permisos_rolls_back_and_closes_on_insert_failure(method, identifier, monkeypatch):
    model = RolPermisoModel()
    connection, cursor = db_pair()
    cursor.execute.side_effect = [None, RuntimeError('insert failed')]
    attach_connection(monkeypatch, model, connection)
    assert getattr(model, method)(identifier, [{'id_modulo': 4}]) is False
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


# Backup helpers and all file/metadata workflows use temporary files and mocked processes/DBs.

def test_respaldo_constructor_creates_configured_directory(tmp_path, monkeypatch):
    target = tmp_path / 'backup-output'
    monkeypatch.setattr(RespaldoModel, 'CARPETA_RESPALDOS', str(target))
    model = RespaldoModel()
    assert target.is_dir()
    assert model.CARPETA_RESPALDOS == str(target)


@pytest.mark.parametrize('name,expected', [
    ('copia de bd!.sql', 'copia_de_bd__sql'),
    ('  abc-1_X  ', 'abc-1_X'),
    ('x' * 110, 'x' * 100),
    ('', ''),
])
def test_respaldo_limpia_nombres(name, expected):
    assert RespaldoModel._limpiar_nombre(name) == expected


@pytest.mark.parametrize('size,expected', [
    (0, '0.0 B'), (1023, '1023.0 B'), (1024, '1.0 KB'), (1024 ** 2, '1.0 MB'),
    (1024 ** 3, '1.0 GB'), (1024 ** 4, '1.0 GB'),
])
def test_respaldo_format_size_boundaries(size, expected):
    assert RespaldoModel._formatear_tamano(size) == expected


def test_respaldo_normalizes_database_row_and_malformed_sizes():
    row = {'tamaño_respaldo': Decimal('1.50'), 'nombre_archivo': None, 'descripcion': None}
    assert RespaldoModel._normalizar_fila(row) is row
    assert row == {
        'tamaño_respaldo': Decimal('1.50'), 'nombre_archivo': '', 'descripcion': '',
        'tamano': 1572864, 'tamano_formateado': '1.5 MB',
    }
    assert RespaldoModel._normalizar_fila({'tamaño_respaldo': 'invalid'})['tamano'] == 0


def test_respaldo_config_uses_configuration_and_fallback_executables(monkeypatch):
    config = {'host': 'db.test', 'user': 'app', 'password': '', 'database': 'appdb', 'charset': 'utf8mb4'}
    monkeypatch.setattr(RespaldoModel, 'configuracion_db', staticmethod(lambda: config))
    monkeypatch.setattr(os.path, 'exists', lambda path: False)
    result = RespaldoModel._obtener_config_bd()
    assert result == dict(config, mysqldump='mysqldump', mysql='mysql')


def test_respaldo_config_prefers_first_available_client(monkeypatch):
    config = {'host': 'h', 'user': 'u', 'password': 'p', 'database': 'd', 'charset': 'utf8'}
    monkeypatch.setattr(RespaldoModel, 'configuracion_db', staticmethod(lambda: config))
    available = r'C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysqldump.exe'
    monkeypatch.setattr(os.path, 'exists', lambda path: path == available)
    result = RespaldoModel._obtener_config_bd()
    assert result['mysqldump'] == available
    assert result['mysql'] == 'mysql'


def test_respaldo_guardar_en_seguridad_rejects_missing_connection(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: None)
    with pytest.raises(RuntimeError, match='seguridad'):
        model._guardar_en_seguridad(1, 'a.sql', 1, '', 2)


def test_respaldo_asegurar_tabla_migrates_missing_columns_and_decimal(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    connection, cursor = db_pair()
    cursor.fetchone.side_effect = [None, None, (None, 'decimal(4,2)')]
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model._asegurar_tabla_seguridad() is True
    sqls = [c.args[0] for c in cursor.execute.call_args_list]
    assert 'CREATE TABLE IF NOT EXISTS' in sqls[0]
    assert any('ADD COLUMN `nombre_archivo`' in sql for sql in sqls)
    assert any('ADD COLUMN `descripcion`' in sql for sql in sqls)
    assert any('MODIFY `tamaño_respaldo` decimal(10,2)' in sql for sql in sqls)
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_respaldo_asegurar_tabla_handles_connection_and_sql_errors(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: None)
    assert model._asegurar_tabla_seguridad() is False
    connection, cursor = db_pair()
    cursor.execute.side_effect = RuntimeError('DDL failed')
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model._asegurar_tabla_seguridad() is False
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_respaldo_siguiente_id_reads_max_and_handles_empty(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    connection, cursor = db_pair()
    cursor.fetchone.return_value = (12,)
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model._siguiente_id() == 12
    assert 'MAX(`id_respaldo`)' in cursor.execute.call_args.args[0]
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
    cursor.fetchone.return_value = None
    assert model._siguiente_id() == 1
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: None)
    with pytest.raises(RuntimeError, match='seguridad'):
        model._siguiente_id()


def test_respaldo_guardar_en_seguridad_converts_size_defaults_user_and_commits(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    connection, cursor = db_pair(database='security-db')
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    result = model._guardar_en_seguridad(2, 'b.sql', 1048576, 'desc', None)
    assert result == 'security-db'
    params = cursor.execute.call_args.args[1]
    assert params[0] == 2 and params[2] == Decimal('1.00') and params[3:] == (1, 1, 'b.sql', 'desc')
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('password,has_password_argument', [('', False), ('db-secret', True)])
def test_respaldo_export_dump_builds_safe_command_and_checks_file(tmp_path, monkeypatch, password, has_password_argument):
    model = RespaldoModel.__new__(RespaldoModel)
    target = tmp_path / 'dump.sql'
    monkeypatch.setattr(model, '_obtener_config_bd', lambda: {
        'mysqldump': 'fake-dump', 'host': 'db', 'user': 'user', 'password': password,
        'charset': 'utf8mb4', 'database': 'db_name',
    })

    seen = {}

    def fake_run(command, stdout, stderr, text):
        seen['command'] = command
        stdout.write('dump content')
        return SimpleNamespace(returncode=0, stderr='')

    monkeypatch.setattr('models.model_respaldo.subprocess.run', fake_run)
    assert model._exportar_dump(str(target)) is True
    assert target.read_text(encoding='utf-8') == 'dump content'
    assert seen['command'][0] == 'fake-dump'
    assert '--single-transaction' in seen['command']
    assert '--password=db-secret' in seen['command'] if has_password_argument else '--password=db-secret' not in seen['command']


def test_respaldo_export_dump_errors_when_process_fails_without_output(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, '_obtener_config_bd', lambda: {
        'mysqldump': 'fake', 'host': 'h', 'user': 'u', 'password': '', 'charset': 'utf8', 'database': 'd',
    })
    monkeypatch.setattr('models.model_respaldo.subprocess.run', lambda *a, **k: SimpleNamespace(returncode=2, stderr='dump failed'))
    with pytest.raises(RuntimeError, match='dump failed'):
        model._exportar_dump(str(tmp_path / 'failed.sql'))


def test_respaldo_export_accepts_nonempty_dump_even_if_process_returns_error(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, '_obtener_config_bd', lambda: {
        'mysqldump': 'fake', 'host': 'h', 'user': 'u', 'password': '', 'charset': 'utf8', 'database': 'd',
    })

    def wrote_partial(command, stdout, **kwargs):
        stdout.write('partial dump')
        return SimpleNamespace(returncode=1, stderr='warning')

    monkeypatch.setattr('models.model_respaldo.subprocess.run', wrote_partial)
    assert model._exportar_dump(str(tmp_path / 'partial.sql')) is True


def test_respaldo_import_sql_passes_file_as_stdin_and_reports_process_failure(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    source = tmp_path / 'source.sql'
    source.write_text('SQL DATA', encoding='utf-8')
    monkeypatch.setattr(model, '_obtener_config_bd', lambda: {
        'mysql': 'fake-mysql', 'host': 'h', 'user': 'u', 'password': 'pw', 'charset': 'utf8', 'database': 'd',
    })
    seen = {}

    def successful(command, stdin, **kwargs):
        seen['command'] = command
        seen['stdin'] = stdin.read()
        return SimpleNamespace(returncode=0, stderr='')

    monkeypatch.setattr('models.model_respaldo.subprocess.run', successful)
    assert model._importar_sql(str(source)) is True
    assert seen['stdin'] == 'SQL DATA'
    assert '--password=pw' in seen['command']
    monkeypatch.setattr('models.model_respaldo.subprocess.run', lambda *a, **k: SimpleNamespace(returncode=1, stderr='import failed'))
    with pytest.raises(RuntimeError, match='import failed'):
        model._importar_sql(str(source))


def test_respaldo_crear_genera_dump_sanitiza_datos_y_registra_metadata(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    model.CARPETA_RESPALDOS = str(tmp_path)
    monkeypatch.setattr(model, '_exportar_dump', lambda path: open(path, 'w', encoding='utf-8').write('SQL') > 0)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    monkeypatch.setattr(model, '_siguiente_id', lambda: 10)
    stored = []
    monkeypatch.setattr(model, '_guardar_en_seguridad', lambda *args: stored.append(args))
    result = model.crear_respaldo('<unsafe> "description";', 9, 'hello world')
    assert result['id_respaldo'] == 10
    assert result['nombre_archivo'] == 'hello_world.sql'
    assert result['descripcion'] == 'unsafe> description'
    assert result['tamano'] == 3 and result['estado'] == 1
    assert stored == [(10, 'hello_world.sql', 3, 'unsafe> description', 9)]
    assert (tmp_path / 'hello_world.sql').read_text(encoding='utf-8') == 'SQL'


def test_respaldo_crear_translates_dump_and_database_failures(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    model.CARPETA_RESPALDOS = str(tmp_path)
    monkeypatch.setattr(model, '_exportar_dump', lambda _path: (_ for _ in ()).throw(FileNotFoundError()))
    with pytest.raises(RuntimeError, match='mysqldump no está disponible'):
        model.crear_respaldo(nombre_archivo='missing.sql')
    monkeypatch.setattr(model, '_exportar_dump', lambda path: open(path, 'w', encoding='utf-8').write('x') > 0)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    monkeypatch.setattr(model, '_siguiente_id', lambda: (_ for _ in ()).throw(ValueError('id error')))
    with pytest.raises(RuntimeError, match='siguiente ID'):
        model.crear_respaldo(nombre_archivo='db-error.sql')


def test_respaldo_listar_normalizes_rows_and_handles_connection_or_query_errors(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    connection, cursor = db_pair(rows=[{'id_respaldo': 1, 'tamaño_respaldo': 1}])
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    result = model.listar_respaldos()
    assert result[0]['tamano'] == 1048576
    assert '`estado`=1 ORDER BY `fecha_respaldo` DESC' in cursor.execute.call_args.args[0]
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: None)
    assert model.listar_respaldos() == []
    connection, cursor = db_pair()
    cursor.execute.side_effect = RuntimeError('select failure')
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model.listar_respaldos() == []
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_respaldo_obtener_por_id_normalizes_missing_and_errors(monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    connection, cursor = db_pair(row={'id_respaldo': 5, 'tamaño_respaldo': 2})
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model.obtener_por_id(5)['tamano'] == 2097152
    assert cursor.execute.call_args.args[1] == (5,)
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
    cursor.fetchone.return_value = None
    assert model.obtener_por_id(5) is None
    cursor.execute.side_effect = RuntimeError('select failed')
    assert model.obtener_por_id(5) is None
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: None)
    assert model.obtener_por_id(5) is None


def test_respaldo_eliminar_unlinks_local_file_and_soft_deletes_record(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    model.CARPETA_RESPALDOS = str(tmp_path)
    backup_file = tmp_path / 'backup.sql'
    backup_file.write_text('dump', encoding='utf-8')
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    monkeypatch.setattr(model, 'obtener_por_id', lambda _id: {'nombre_archivo': 'backup.sql'})
    connection, cursor = db_pair(rowcount=1)
    monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model.eliminar_respaldo(3) is True
    assert not backup_file.exists()
    assert cursor.execute.call_args.args[1] == (3,)
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize('rowcount,connection_missing,expected', [(0, False, False), (1, True, False)])
def test_respaldo_eliminar_returns_false_for_no_update_or_no_connection(tmp_path, monkeypatch, rowcount, connection_missing, expected):
    model = RespaldoModel.__new__(RespaldoModel)
    model.CARPETA_RESPALDOS = str(tmp_path)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    monkeypatch.setattr(model, 'obtener_por_id', lambda _id: {'nombre_archivo': ''})
    if connection_missing:
        monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: None)
    else:
        connection, cursor = db_pair(rowcount=rowcount)
        monkeypatch.setattr(model, 'obtener_conexion_seguridad_segura', lambda: connection)
    assert model.eliminar_respaldo(3) is expected


def test_respaldo_importar_restores_file_and_registers_metadata(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    source = tmp_path / 'incoming.sql'
    source.write_text('statement;', encoding='utf-8')
    imported, stored = [], []
    monkeypatch.setattr(model, '_importar_sql', lambda path: imported.append(path))
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    monkeypatch.setattr(model, '_siguiente_id', lambda: 12)
    monkeypatch.setattr(model, '_guardar_en_seguridad', lambda *args: stored.append(args) or 'security-db')
    assert model.importar_respaldo(str(source), '<desc>;', 8) == {
        'id_respaldo': 12, 'advertencia': None, 'db_seguridad': 'security-db',
    }
    assert imported == [str(source)]
    assert stored == [(12, 'incoming.sql', source.stat().st_size, 'desc>', 8)]


def test_respaldo_importar_reports_restore_id_and_metadata_failures(tmp_path, monkeypatch):
    model = RespaldoModel.__new__(RespaldoModel)
    source = tmp_path / 'bad.sql'
    source.write_text('SQL', encoding='utf-8')
    monkeypatch.setattr(model, '_importar_sql', lambda _path: (_ for _ in ()).throw(ValueError('restore failed')))
    with pytest.raises(RuntimeError, match='importar respaldo'):
        model.importar_respaldo(str(source))
    monkeypatch.setattr(model, '_importar_sql', lambda _path: None)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: True)
    monkeypatch.setattr(model, '_siguiente_id', lambda: (_ for _ in ()).throw(ValueError('id failed')))
    with pytest.raises(RuntimeError, match='siguiente ID'):
        model.importar_respaldo(str(source))
    monkeypatch.setattr(model, '_siguiente_id', lambda: 1)
    monkeypatch.setattr(model, '_guardar_en_seguridad', lambda *args: (_ for _ in ()).throw(ValueError('metadata failed')))
    result = model.importar_respaldo(str(source), '  ')
    assert result['id_respaldo'] == 1
    assert 'metadata failed' in result['advertencia']
    assert result['db_seguridad'] is None
