from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_obras(app):
    # INICIO DE MOCK: Llamar verify_module_route
    case = verify_module_route(app, 'obras')
    # INICIO DE ASERCIÓN: Verificar descripción de la ruta
    assert case['description'] == 'registro de la vista de gestión de obras'
    # FIN DE ASERCIÓN
