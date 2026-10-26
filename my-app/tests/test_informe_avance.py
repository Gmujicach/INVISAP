import pytest

from models.model_informe_avance import InformeAvanceModel


def informe_sin_conexion():
    return InformeAvanceModel.__new__(InformeAvanceModel)


def test_porcentaje_de_avance_se_limita_a_rango_valido():
    informe = informe_sin_conexion()

    informe.set_porcentaje_avance(120)

    assert informe.get_porcentaje_avance() == 100


def test_estado_de_informe_normaliza_opcion_valida():
    informe = informe_sin_conexion()

    informe.set_estado('En Ejecución')

    assert informe.get_estado() == 'En Ejecucion'


def test_rechaza_estado_de_informe_desconocido():
    with pytest.raises(ValueError):
        informe_sin_conexion().set_estado('Desconocido')
