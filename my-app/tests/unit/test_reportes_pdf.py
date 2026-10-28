from models.model_reportesPDF import ReportePDFModel


def test_filtro_pdf_usa_parametro_y_no_interpola_valor():
    where, params = [], []

    ReportePDFModel()._aplicar_filtros(
        where, params, {'cedula': "123' OR 1=1 --"}, {'cedula': 'p.cedula_persona'}
    )

    assert where == ['p.cedula_persona LIKE %s']
    assert params == ["%123' OR 1=1 --%"]
