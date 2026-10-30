from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_contratacion(app):
    case = verify_module_route(app, 'contratacion')
    assert case['description'] == 'registro de la vista de gestión de contrataciones'
