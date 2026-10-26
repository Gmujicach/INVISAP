import pytest

from models.model_solicitudes import SolicitudModel


def test_tipo_y_estado_de_solicitud_validos():
    solicitud = SolicitudModel()

    solicitud.set_tipo_solicitud('Comunidad')
    solicitud.set_estatus_solicitud('En Proceso')

    assert solicitud.get_tipo_solicitud() == 'Comunidad'
    assert solicitud.get_estatus_solicitud() == 'En Proceso'


def test_rechaza_tipo_de_solicitud_desconocido():
    with pytest.raises(ValueError):
        SolicitudModel().set_tipo_solicitud('Desconocido')


def test_problematica_incluye_categoria_valida():
    solicitud = SolicitudModel()

    solicitud.set_problematica(
        'La vía requiere reparación urgente',
        'Infraestructura y Vialidad',
    )

    assert solicitud.get_problematica().startswith('[Infraestructura y Vialidad]')
