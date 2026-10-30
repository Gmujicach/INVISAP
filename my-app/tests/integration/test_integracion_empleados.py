from tests.integration.route_contracts import verify_module_route


def test_integracion_listado_empleados(app):
    case = verify_module_route(app, 'empleados')
    assert case['description'] == 'registro del listado de empleados'
