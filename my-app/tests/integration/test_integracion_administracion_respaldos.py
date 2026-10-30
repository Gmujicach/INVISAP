from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_administracion_respaldos(app):
    case = verify_module_route(app, 'administracion_respaldos')
    assert case['description'] == 'registro de la vista de administración de respaldos'
