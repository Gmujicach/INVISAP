from tests.integration.route_contracts import verify_module_route


def test_integracion_listado_evidencias(app):
    case = verify_module_route(app, 'evidencias')
    assert case['description'] == 'registro del listado de evidencias'
