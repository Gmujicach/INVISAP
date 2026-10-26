from unittest.mock import patch

from models.model_empresas import EmpresaModel


def test_empresa_existente_activa_no_se_registra_de_nuevo():
    modelo = EmpresaModel()
    datos = {
        'rif': 'J-123',
        'nombre_empresa': 'Empresa Ejemplo',
        'telefono': '0251-1234567',
        'domicilio_fiscal': 'Barquisimeto',
    }

    with patch.object(modelo, '_ejecutar_consulta', return_value={'estado': 1}), \
            patch.object(modelo, '_ejecutar_modificacion') as modificar:
        resultado = modelo.registrar_Empresas(datos)

    assert resultado == 'DUPLICADO'
    modificar.assert_not_called()


def test_empresa_nueva_usa_rif_parametrizado():
    modelo = EmpresaModel()
    datos = {
        'rif': 'J-123',
        'nombre_empresa': 'Empresa Ejemplo',
        'telefono': '0251-1234567',
        'domicilio_fiscal': 'Barquisimeto',
    }

    with patch.object(modelo, '_ejecutar_consulta', return_value=None), \
            patch.object(modelo, '_ejecutar_modificacion', return_value=True) as modificar:
        assert modelo.registrar_Empresas(datos) is True

    assert modificar.call_args.args[1] == ('J-123', 'Empresa Ejemplo', '0251-1234567', 'Barquisimeto')
