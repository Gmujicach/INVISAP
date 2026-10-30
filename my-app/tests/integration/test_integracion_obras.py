from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_obras(app):
    case = verify_module_route(app, 'obras')
    assert case['description'] == 'registro de la vista de gestión de obras'
