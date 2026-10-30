from tests.integration.route_contracts import verify_module_route


def test_integracion_ruta_empresa(app):
    case = verify_module_route(app, 'empresa')
    assert case['description'] == 'registro de la ruta de listado de empresas'
