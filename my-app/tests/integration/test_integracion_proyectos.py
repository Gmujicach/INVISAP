from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_proyectos(app):
    case = verify_module_route(app, 'proyectos')
    assert case['description'] == 'registro de la vista de gestión de proyectos'
