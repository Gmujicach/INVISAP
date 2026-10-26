import pytest

from models.model_inspeccion import InspeccionModel


def test_validadores_de_inspeccion_aceptan_datos_correctos():
    inspeccion = InspeccionModel.__new__(InspeccionModel)

    assert inspeccion._validar_inspector('12') is True
    assert inspeccion._validar_fecha('2025-03-18') is True
    assert inspeccion._validar_observaciones('Inspección en buen estado') is True


def test_validadores_de_inspeccion_rechazan_datos_invalidos():
    inspeccion = InspeccionModel.__new__(InspeccionModel)

    assert inspeccion._validar_inspector('cero') is False
    assert inspeccion._validar_fecha('18/03/2025') is False
    assert inspeccion._validar_observaciones('no') is False


def test_tipo_de_inspeccion_rechaza_valores_no_catalogados():
    inspeccion = InspeccionModel.__new__(InspeccionModel)

    with pytest.raises(ValueError):
        inspeccion.set_tipo_inspeccion('Preventiva')
