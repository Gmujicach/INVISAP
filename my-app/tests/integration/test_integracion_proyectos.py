from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_proyectos(app):
    # INICIO DE MOCK: Llamar verify_module_route
    case = verify_module_route(app, 'proyectos')
    # INICIO DE ASERCIÓN: Verificar descripción de la ruta
    assert case['description'] == 'registro de la vista de gestión de proyectos'
    # FIN DE ASERCIÓN
