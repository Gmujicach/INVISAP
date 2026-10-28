import pytest

from controllers.controller_gravedad import _calcular_nivel_gravedad
from models.model_gravedad import GravedadObraModel


@pytest.mark.parametrize(('criticidad', 'nivel'), [(0, 'Bajo'), (50, 'Bajo'), (51, 'Alto'), (100, 'Alto')])
def test_calcula_nivel_de_gravedad(criticidad, nivel):
    assert _calcular_nivel_gravedad(criticidad) == nivel


def test_criticidad_rechaza_valores_fuera_de_rango():
    with pytest.raises(ValueError):
        GravedadObraModel().set_criticidad(101)


def test_criticidad_acepta_y_normaliza_valor_numerico():
    gravedad = GravedadObraModel()

    gravedad.set_criticidad('75.0')

    assert gravedad.get_criticidad() == 75
