from tests.integration.route_contracts import verify_module_route


def test_integracion_listado_publicaciones(app):
    case = verify_module_route(app, 'publicaciones')
    assert case['description'] == 'registro del listado de publicaciones'
