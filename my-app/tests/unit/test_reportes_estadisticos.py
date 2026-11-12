from unittest.mock import MagicMock, patch

import pytest

from models.model_ReporteEstadistico import ReporteEstadisticoModel


def test_filtro_estadistico_acepta_columna_mapeada():
    where, params = [], []

    ReporteEstadisticoModel()._aplicar_filtros(
        where, params, {'nombre': 'Ana'}, {'nombre': 'e.nombre'}
    )

    assert where == ['e.nombre LIKE %s']
    assert params == ['%Ana%']


def test_filtros_estadisticos_aplican_condiciones_especiales_y_ignoran_no_mapeadas():
    where, params = [], []
    ReporteEstadisticoModel()._aplicar_filtros(
        where, params,
        {
            'correo_dominio': 'ejemplo.test',
            'fecha_inicio_desde': '2025-01-01',
            'fecha_fin_hasta': '2025-12-31',
            'porcentaje_avance_min': 0,
            'porcentaje_avance_max': 85,
            'sector': 'Norte',
            'ambito': 'Rural',
            'estado': '1',
            'estado_texto': 'Activo',
            'tipo_reporte': 'obras',
            'agrupacion': 'mes',
            'irrelevante': 'ignorar',
            'vacio': '',
        },
        {
            'correo_dominio': 'p.correo',
            'fecha_inicio_desde': 'o.fecha_inicio',
            'fecha_fin_hasta': 'o.fecha_fin',
            'estado': 'o.estado',
            'estado_texto': 'o.estado_texto',
        },
    )
    assert where == [
        'p.correo LIKE %s',
        'DATE(o.fecha_inicio) >= %s',
        'DATE(o.fecha_fin) <= %s',
        'o.porcentaje_avance_obra >= %s',
        'o.porcentaje_avance_obra <= %s',
        'com.sector LIKE %s',
        'com.ambito LIKE %s',
        'o.estado = %s',
        'o.estado_texto LIKE %s',
    ]
    assert params == [
        '%ejemplo.test%', '2025-01-01', '2025-12-31', 0, 85, '%Norte%', '%Rural%', 1, '%Activo%'
    ]


def test_ejecutar_query_retorna_filas_y_cierra_recursos_tras_error():
    modelo = ReporteEstadisticoModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'id': 5}]
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo._ejecutar_query('SELECT id FROM datos', [5]) == [{'id': 5}]
    cursor.execute.assert_called_once_with('SELECT id FROM datos', [5])
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()

    cursor.reset_mock()
    conexion.close.reset_mock()
    cursor.execute.side_effect = RuntimeError('fallo simulado')
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        with pytest.raises(RuntimeError, match='fallo simulado'):
            modelo._ejecutar_query('SELECT 1')
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def _modelo_estadistico_con_cursor():
    modelo = ReporteEstadisticoModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.side_effect = lambda: [{'label': 'muestra', 'valor': 2}]
    return modelo, conexion, cursor


@pytest.mark.parametrize(
    ('agrupacion', 'campo', 'sql_fragment'),
    [
        ('dia', 'por_fecha', 'GROUP BY DATE(s.fecha)'),
        ('mes', 'por_mes', "GROUP BY DATE_FORMAT(s.fecha, '%Y-%m')"),
        ('semana', 'por_semana', "GROUP BY DATE_FORMAT(s.fecha, '%x-W%v')"),
    ],
)
def test_estadisticas_solicitudes_cambian_agrupacion_y_agregan_filtros(
    agrupacion, campo, sql_fragment
):
    modelo, conexion, cursor = _modelo_estadistico_con_cursor()
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.obtener_estadisticas_solicitudes(
            {'tipo_solicitud': 'Obra'}, agrupacion
        )
    assert resultado[campo] == [{'label': 'muestra', 'valor': 2}]
    assert resultado['por_tipo'] == [{'label': 'muestra', 'valor': 2}]
    assert resultado['por_estatus'] == [{'label': 'muestra', 'valor': 2}]
    assert len(cursor.execute.call_args_list) == 3
    assert sql_fragment in cursor.execute.call_args_list[0].args[0]
    assert cursor.execute.call_args_list[0].args[1] == ['%Obra%']
    assert all(call.args[1] == ['%Obra%'] for call in cursor.execute.call_args_list)
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_estadisticas_solicitudes_incluyen_dimensiones_geograficas_si_hay_filtros():
    modelo, conexion, cursor = _modelo_estadistico_con_cursor()
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.obtener_estadisticas_solicitudes({'municipio': 'Coro'})
    assert all(key in resultado for key in (
        'por_fecha', 'por_tipo', 'por_estatus', 'por_municipio', 'por_parroquia', 'por_sector'
    ))
    assert len(cursor.execute.call_args_list) == 6
    assert all(call.args[1] == ['%Coro%'] for call in cursor.execute.call_args_list)
    assert 'GROUP BY p.municipio' in cursor.execute.call_args_list[3].args[0]
    assert 'GROUP BY p.parroquia' in cursor.execute.call_args_list[4].args[0]
    assert 'GROUP BY com.sector' in cursor.execute.call_args_list[5].args[0]


@pytest.mark.parametrize(
    ('agrupacion', 'sql_fragment'),
    [
        ('dia', 'GROUP BY DATE(COALESCE(o.fecha_inicio, o.fecha_fin))'),
        ('mes', "GROUP BY DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%Y-%m')"),
        ('semana', "GROUP BY DATE_FORMAT(COALESCE(o.fecha_inicio, o.fecha_fin), '%x-W%v')"),
    ],
)
def test_estadisticas_obras_agregan_fechas_estado_avance_y_filtro(
    agrupacion, sql_fragment
):
    modelo, conexion, cursor = _modelo_estadistico_con_cursor()
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.obtener_estadisticas_obras(
            {'porcentaje_avance_min': 40}, agrupacion
        )
    assert set(resultado) == {
        'por_fecha', 'por_estado', 'por_contratista', 'por_ubicacion',
        'por_semaforo_color', 'por_avance'
    }
    assert len(cursor.execute.call_args_list) == 6
    assert sql_fragment in cursor.execute.call_args_list[0].args[0]
    assert 'o.porcentaje_avance_obra >= %s' in cursor.execute.call_args_list[0].args[0]
    assert all(call.args[1] == [40] for call in cursor.execute.call_args_list)


@pytest.mark.parametrize(
    ('agrupacion', 'sql_fragment'),
    [
        ('dia', 'GROUP BY DATE(e.fecha_ingreso)'),
        ('mes', "GROUP BY DATE_FORMAT(e.fecha_ingreso, '%Y-%m')"),
        ('semana', "GROUP BY DATE_FORMAT(e.fecha_ingreso, '%x-W%v')"),
    ],
)
def test_estadisticas_empleados_incluyen_dimensiones_y_fecha_ingreso(
    agrupacion, sql_fragment
):
    modelo, conexion, cursor = _modelo_estadistico_con_cursor()
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.obtener_estadisticas_empleados(
            {'nombre_empleado': 'Ana'}, agrupacion
        )
    assert set(resultado) == {'por_cargo', 'por_gerencia', 'por_estado', 'por_fecha_ingreso'}
    assert len(cursor.execute.call_args_list) == 4
    assert sql_fragment in cursor.execute.call_args_list[3].args[0]
    assert all(call.args[1] == ['%Ana%'] for call in cursor.execute.call_args_list)


@pytest.mark.parametrize(
    ('agrupacion', 'sql_fragment'),
    [
        ('dia', 'GROUP BY DATE(c.fecha_registro)'),
        ('mes', "GROUP BY DATE_FORMAT(c.fecha_registro, '%Y-%m')"),
        ('semana', "GROUP BY DATE_FORMAT(c.fecha_registro, '%x-W%v')"),
    ],
)
def test_estadisticas_contrataciones_resumenes_y_agrupacion(
    agrupacion, sql_fragment
):
    modelo, conexion, cursor = _modelo_estadistico_con_cursor()
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.obtener_estadisticas_contrataciones(
            {'empresa_ganadora': 'Constructora'}, agrupacion
        )
    assert set(resultado) == {
        'por_tipo', 'por_modalidad', 'por_objeto', 'por_estado', 'por_empresa', 'por_fecha'
    }
    assert len(cursor.execute.call_args_list) == 6
    assert sql_fragment in cursor.execute.call_args_list[-1].args[0]
    assert all(call.args[1] == ['%Constructora%'] for call in cursor.execute.call_args_list)


@pytest.mark.parametrize(
    ('agrupacion', 'sql_fragment'),
    [
        ('dia', 'GROUP BY DATE(fecha_publicacion)'),
        ('mes', "GROUP BY DATE_FORMAT(fecha_publicacion, '%Y-%m')"),
        ('semana', "GROUP BY DATE_FORMAT(fecha_publicacion, '%x-W%v')"),
    ],
)
def test_estadisticas_publicaciones_resumen_por_tipo_autor_y_fecha(
    agrupacion, sql_fragment
):
    modelo, conexion, cursor = _modelo_estadistico_con_cursor()
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.obtener_estadisticas_publicaciones(
            {'tipo_publicacion': 'Aviso'}, agrupacion
        )
    assert set(resultado) == {'por_tipo', 'por_autor', 'por_fecha'}
    assert len(cursor.execute.call_args_list) == 3
    assert sql_fragment in cursor.execute.call_args_list[-1].args[0]
    assert all(call.args[1] == ['%Aviso%'] for call in cursor.execute.call_args_list)
