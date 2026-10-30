from tests.integration.route_contracts import verify_module_route


def test_integracion_listado_informe_avance(app):
    case = verify_module_route(app, 'informe_avance')
    assert case['description'] == 'registro del listado de informes de avance'
