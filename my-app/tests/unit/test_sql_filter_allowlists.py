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
