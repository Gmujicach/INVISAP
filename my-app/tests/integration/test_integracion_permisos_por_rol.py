from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_permisos_por_rol(app):
    case = verify_module_route(app, 'permisos_por_rol')
    assert case['description'] == 'registro de la vista de gestión de permisos'
