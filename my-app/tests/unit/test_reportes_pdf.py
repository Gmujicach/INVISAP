from unittest.mock import MagicMock, patch

import pytest

from models.model_reportesPDF import ReportePDFModel


def test_filtro_pdf_usa_parametro_y_no_interpola_valor():
    where, params = [], []

    ReportePDFModel()._aplicar_filtros(
        where, params, {'cedula': "123' OR 1=1 --"}, {'cedula': 'p.cedula_persona'}
    )

    assert where == ['p.cedula_persona LIKE %s']
    assert params == ["%123' OR 1=1 --%"]


@pytest.mark.parametrize(
    ('method_name', 'table', 'filters', 'where_sql', 'params', 'security_db'),
    [
        ('obtener_solicitudes', 'FROM solicitudes s', {'tipo_solicitud': 'Obra'},
         's.tipo_solicitud LIKE %s', ['%Obra%'], False),
        ('obtener_solicitantes', 'FROM particular pa', {'nombre': 'Ana'},
         'pa.nombre LIKE %s', ['%Ana%'], False),
        ('obtener_empleados', 'FROM empleados e', {'fecha_ingreso_hasta': '2025-12-31'},
         'DATE(e.fecha_ingreso) <= %s', ['2025-12-31'], False),
        ('obtener_usuarios', 'FROM usuarios', {'rol': 'admin'},
         'rol LIKE %s', ['%admin%'], True),
        ('obtener_contrataciones', 'FROM contratacion c', {'empresa_ganadora': 'Obras'},
         'c.empresa_ganadora LIKE %s', ['%Obras%'], False),
        ('obtener_obras', 'FROM obra o', {'titulo_obra': 'Puente'},
         'o.titulo_obra LIKE %s', ['%Puente%'], False),
        ('obtener_publicaciones_reporte', 'FROM publicacion', {'tipo_publicacion': 'Aviso'},
         'tipo_publicacion LIKE %s', ['%Aviso%'], False),
    ],
)
def test_generadores_pdf_aplican_filtros_retorno_y_contexto_bd(
    method_name, table, filters, where_sql, params, security_db
):
    modelo = ReportePDFModel()
    rows = [{'id': 42}]
    with patch.object(modelo, '_ejecutar_query', return_value=rows) as ejecutar:
        assert getattr(modelo, method_name)(filters) is rows

    query = ejecutar.call_args.args[0]
    assert table in query
    assert where_sql in query
    assert ejecutar.call_args.args[1] == params
    assert ejecutar.call_args.kwargs.get('db_name') == ('seguridad' if security_db else None)


def test_filtros_pdf_cubre_casos_especiales_y_descarta_estado_invalido():
    where, params = [], []
    ReportePDFModel()._aplicar_filtros(
        where, params,
        {
            'nombre_solicitante': 'Ana',
            'correo_dominio': 'ejemplo.test',
            'fecha_hasta': '2025-12-31',
            'estado': '2',
            'porcentaje_avance_min': 0,
            'sector': 'Norte',
            'ambito': 'Rural',
            'titulo_obra': 'Puente',
            'sin_mapa': 'ignorar',
        },
        {
            'correo_dominio': 'p.correo',
            'fecha_hasta': 'p.fecha',
            'estado': 'p.estado',
            'porcentaje_avance_min': 'o.porcentaje_avance_min',
        },
    )
    assert where == [
        '(COALESCE(part.nombre, inst.razon_social, com.nombre_comunidad) LIKE %s)',
        'p.correo LIKE %s',
        'DATE(p.fecha) <= %s',
        'o.porcentaje_avance >= %s',
        'com.sector LIKE %s',
        'com.ambito LIKE %s',
        'o.titulo_obra LIKE %s',
    ]
    assert params == [
        '%Ana%', '%ejemplo.test%', '2025-12-31', 0, '%Norte%', '%Rural%', '%Puente%'
    ]


def test_ejecutar_query_elige_conexion_y_limpia_recursos():
    modelo = ReportePDFModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'id': 1}]
    with patch.object(modelo, 'obtener_conexion_seguridad', return_value=conexion) as seguridad:
        assert modelo._ejecutar_query('SELECT id FROM usuarios', None, 'seguridad') == [{'id': 1}]
    seguridad.assert_called_once_with()
    cursor.execute.assert_called_once_with('SELECT id FROM usuarios', ())
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_ejecutar_query_libera_recursos_si_consulta_falla():
    modelo = ReportePDFModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    cursor.execute.side_effect = RuntimeError('fallo simulado')
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        with pytest.raises(RuntimeError, match='fallo simulado'):
            modelo._ejecutar_query('SELECT 1')
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()
