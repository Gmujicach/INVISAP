from unittest.mock import MagicMock, patch

import pytest

from models.model_reportesExcel import ReporteExcelModel


def test_filtro_excel_ignora_columna_no_mapeada():
    where, params = [], []

    ReporteExcelModel()._aplicar_filtros(
        where, params, {'columna_arbitraria': 'valor'}, {'cedula': 'p.cedula_persona'}
    )

    assert where == []
    assert params == []


@pytest.mark.parametrize(
    ('method_name', 'table', 'filters', 'where_sql', 'params', 'security_db'),
    [
        ('obtener_solicitudes_reporte', 'FROM solicitudes s', {'tipo_solicitud': 'Obra'},
         's.tipo_solicitud LIKE %s', ['%Obra%'], False),
        ('obtener_solicitantes_reporte', 'FROM particular pa', {'nombre': 'Ana'},
         'pa.nombre LIKE %s', ['%Ana%'], False),
        ('obtener_empleados_reporte', 'FROM empleados e', {'fecha_ingreso_desde': '2025-01-01'},
         'DATE(e.fecha_ingreso) >= %s', ['2025-01-01'], False),
        ('obtener_usuarios_reporte', 'FROM usuarios', {'rol': 'admin'},
         'rol LIKE %s', ['%admin%'], True),
        ('obtener_contrataciones_reporte', 'FROM contratacion c', {'empresa_ganadora': 'Obras'},
         'c.empresa_ganadora LIKE %s', ['%Obras%'], False),
        ('obtener_obras_reporte', 'FROM obra o', {'titulo_obra': 'Puente'},
         'o.titulo_obra LIKE %s', ['%Puente%'], False),
        ('obtener_publicaciones_reporte', 'FROM publicacion', {'tipo_publicacion': 'Aviso'},
         'tipo_publicacion LIKE %s', ['%Aviso%'], False),
        ('obtener_avances_reporte', 'FROM avance a', {'porcentaje_avance_min': 25},
         'a.porcentaje_avance >= %s', [25], False),
        ('obtener_inspecciones_reporte', 'FROM inspeccion i', {'tipo_inspeccion': 'Técnica'},
         'i.tipo_inspeccion LIKE %s', ['%Técnica%'], False),
        ('obtener_evidencias_reporte', 'FROM evidencia ev', {'etapa': 'Ejecución'},
         'ev.etapa LIKE %s', ['%Ejecución%'], False),
        ('obtener_gravedades_reporte', 'FROM gravedad_obra g', {'criticidad': 'Alta'},
         'g.criticidad LIKE %s', ['%Alta%'], False),
    ],
)
def test_generadores_excel_aplican_filtros_retorno_y_contexto_bd(
    method_name, table, filters, where_sql, params, security_db
):
    modelo = ReporteExcelModel()
    rows = [{'id': 42}]
    with patch.object(modelo, '_ejecutar_query', return_value=rows) as ejecutar:
        assert getattr(modelo, method_name)(filters) is rows

    query = ejecutar.call_args.args[0]
    assert table in query
    assert where_sql in query
    assert ejecutar.call_args.args[1] == params
    assert ejecutar.call_args.kwargs.get('db_name') == ('seguridad' if security_db else None)


def test_filtros_excel_cubre_fechas_limites_estado_y_filtros_especiales():
    where, params = [], []
    ReporteExcelModel()._aplicar_filtros(
        where, params,
        {
            'fecha_desde': '2025-01-01',
            'fecha_hasta': '2025-12-31',
            'estado': '1',
            'porcentaje_avance_max': 80,
            'nombre_solicitante': 'Ana',
            'sector': 'Norte',
            'ambito': 'Rural',
            'titulo_obra': 'Puente',
            'desconocido': 'ignorar',
            'vacio': '',
        },
        {
            'fecha_desde': 'p.fecha',
            'fecha_hasta': 'p.fecha',
            'estado': 'p.estado',
            'porcentaje_avance_max': 'o.porcentaje_avance_max',
        },
    )
    assert where == [
        'DATE(p.fecha) >= %s',
        'DATE(p.fecha) <= %s',
        'p.estado = %s',
        'o.porcentaje_avance <= %s',
        '(COALESCE(part.nombre, inst.razon_social, com.nombre_comunidad) LIKE %s)',
        'com.sector LIKE %s',
        'com.ambito LIKE %s',
        'o.titulo_obra LIKE %s',
    ]
    assert params == [
        '2025-01-01', '2025-12-31', 1, 80, '%Ana%', '%Norte%', '%Rural%', '%Puente%'
    ]


def test_ejecutar_query_elige_conexion_y_limpia_cursor_y_conexion():
    modelo = ReporteExcelModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'nombre': 'Ana'}]

    with patch.object(modelo, 'obtener_conexion_seguridad', return_value=conexion) as seguridad:
        assert modelo._ejecutar_query('SELECT nombre FROM usuarios', ['x'], 'seguridad') == [
            {'nombre': 'Ana'}
        ]
    seguridad.assert_called_once_with()
    cursor.execute.assert_called_once_with('SELECT nombre FROM usuarios', ['x'])
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_ejecutar_query_cierra_recursos_si_execute_falla():
    modelo = ReporteExcelModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.execute.side_effect = RuntimeError('fallo simulado')
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        with pytest.raises(RuntimeError, match='fallo simulado'):
            modelo._ejecutar_query('SELECT 1')
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_estadisticas_generales_compone_tres_valores_y_cierra_recursos():
    modelo = ReporteExcelModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.fetchone.side_effect = [
        {'hombres': 2, 'mujeres': 3, 'total': 5},
        {'promedio_salarial': 1250},
        {'total_pub': 7},
    ]
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.obtener_estadisticas_generales() == {
            'empleados': {'hombres': 2, 'mujeres': 3, 'total': 5},
            'promedio_salarial': 1250,
            'publicaciones': 7,
        }
    assert cursor.execute.call_count == 3
    assert 'FROM tbl_empleados' in cursor.execute.call_args_list[0].args[0]
    assert 'AVG(salario_empleado)' in cursor.execute.call_args_list[1].args[0]
    assert 'FROM tbl_publicaciones' in cursor.execute.call_args_list[2].args[0]
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()
