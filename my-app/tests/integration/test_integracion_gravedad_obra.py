from tests.integration.route_contracts import verify_module_route


def test_integracion_api_gravedad_obra(app):
    case = verify_module_route(app, 'gravedad_obra')
    assert case['description'] == 'conexión de la API de gravedad con su endpoint Flask'
