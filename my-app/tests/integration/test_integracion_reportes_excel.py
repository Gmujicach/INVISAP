from tests.integration.route_contracts import verify_module_route


def test_integracion_endpoint_reportes_excel(app):
    case = verify_module_route(app, 'reportes_excel')
    assert case['description'] == 'registro del endpoint de reportes Excel'
