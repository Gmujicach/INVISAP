from models.model_maquinaria import MaquinariaModel


def test_valida_nombre_y_tipo_de_maquinaria():
    modelo = MaquinariaModel()

    assert modelo.validar_nombre('Excavadora')['valido'] is True
    assert modelo.validar_tipo('Pesada')['valido'] is True


def test_rechaza_nombre_corto_y_tipo_ajeno_al_catalogo():
    modelo = MaquinariaModel()

    assert modelo.validar_nombre('AB')['valido'] is False
    assert modelo.validar_tipo('Aeronave')['valido'] is False
