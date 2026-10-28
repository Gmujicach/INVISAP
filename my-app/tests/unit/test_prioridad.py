import pytest

from models.model_prioridad import PrioridadModel


def test_prioridad_redondea_rango_valido():
    prioridad = PrioridadModel()

    prioridad.set_rango('0.7564')

    assert prioridad.get_rango() == 0.756


@pytest.mark.parametrize('valor', [-0.1, 1.1, 'invalido'])
def test_prioridad_rechaza_rango_fuera_de_limites(valor):
    with pytest.raises(ValueError):
        PrioridadModel().set_rango(valor)


def test_prioridad_rechaza_origen_no_permitido():
    with pytest.raises(ValueError):
        PrioridadModel().set_origen('desconocido')
