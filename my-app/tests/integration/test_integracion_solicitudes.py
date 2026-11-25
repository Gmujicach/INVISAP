from tests.integration.route_contracts import verify_module_route


def test_integracion_ruta_solicitudes(app):
    # INICIO DE MOCK: Llamar verify_module_route
    case = verify_module_route(app, 'solicitudes')
    # INICIO DE ASERCIÓN: Verificar descripción de la ruta
    assert case['description'] == 'registro de la ruta de listado de solicitudes'
    # FIN DE ASERCIÓN
