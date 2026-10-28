import pytest

from models.model_empleados import EmpleadoModel


def test_valida_y_limpia_nombre_y_cargo():
    empleado = EmpleadoModel()

    empleado.set_nombre_empleado(' Ana Pérez ')
    empleado.set_cargo('Inspector')

    assert empleado.get_nombre_empleado() == 'Ana Pérez'
    assert empleado.get_cargo() == 'Inspector'


@pytest.mark.parametrize(('setter', 'valor'), [
    ('set_nombre_empleado', 'A'),
    ('set_cargo', 'Cargo inventado'),
    ('set_cedula_persona', '123'),
])
def test_rechaza_datos_de_empleado_invalidos(setter, valor):
    with pytest.raises(ValueError):
        getattr(EmpleadoModel(), setter)(valor)
