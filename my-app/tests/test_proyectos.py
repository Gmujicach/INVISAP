import json

from models.model_proyecto import ProyectoModel


def test_computos_metricos_se_serializan_y_se_recuperan():
    entradas = [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}]

    serializado = ProyectoModel._serializar_computos_metricos(entradas)

    assert json.loads(serializado) == entradas
    assert ProyectoModel._parsear_computos_metricos(serializado) == entradas


def test_texto_legacy_de_computos_metricos_se_convierte():
    assert ProyectoModel._parsear_computos_metricos('10 km') == [
        {'metrica': '', 'opcion': '10 km', 'costo': ''}
    ]


def test_formatea_computos_metricos_para_mostrar():
    assert ProyectoModel._formatear_computos_metricos(
        [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}]
    ) == '500 Longitud 10 km'
