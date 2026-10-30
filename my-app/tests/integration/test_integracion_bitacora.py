from tests.integration.route_contracts import verify_module_route


def test_integracion_api_bitacora(app):
    case = verify_module_route(app, 'bitacora')
    assert case['description'] == 'conexión de la API de bitácora con su endpoint Flask'
