from models.model_ReporteEstadistico import ReporteEstadisticoModel


def test_filtro_estadistico_acepta_columna_mapeada():
    where, params = [], []

    ReporteEstadisticoModel()._aplicar_filtros(
        where, params, {'nombre': 'Ana'}, {'nombre': 'e.nombre'}
    )

    assert where == ['e.nombre LIKE %s']
    assert params == ['%Ana%']
