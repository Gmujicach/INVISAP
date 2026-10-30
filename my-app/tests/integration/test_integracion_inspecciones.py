from tests.integration.route_contracts import verify_module_route


def test_integracion_listado_inspecciones(app):
    case = verify_module_route(app, 'inspecciones')
    assert case['description'] == 'registro del listado de inspecciones'
