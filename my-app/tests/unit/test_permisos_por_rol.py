import pytest

from models.model_seguridad import ModuloModel, RolModel


def test_modulo_rechaza_url_que_no_empieza_con_barra():
    modulo = ModuloModel(nombre='obras', url='obras', tipo='CRUD')

    with pytest.raises(ValueError):
        modulo._validar()


def test_rol_rechaza_nombre_con_caracteres_no_permitidos():
    rol = RolModel(nombre='Admin123')

    with pytest.raises(ValueError):
        rol._validar()
