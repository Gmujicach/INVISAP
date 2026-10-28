from models.model_reportesExcel import ReporteExcelModel


def test_filtro_excel_ignora_columna_no_mapeada():
    where, params = [], []

    ReporteExcelModel()._aplicar_filtros(
        where, params, {'columna_arbitraria': 'valor'}, {'cedula': 'p.cedula_persona'}
    )

    assert where == []
    assert params == []
