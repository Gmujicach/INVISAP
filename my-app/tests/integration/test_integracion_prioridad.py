from tests.integration.route_contracts import verify_module_route


def test_integracion_api_prioridad(app):
    case = verify_module_route(app, 'prioridad')
    assert case['description'] == 'conexión de la API de prioridad con su endpoint Flask'
