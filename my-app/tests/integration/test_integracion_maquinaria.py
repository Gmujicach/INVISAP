from tests.integration.route_contracts import verify_module_route


def test_integracion_vista_maquinaria(app):
    case = verify_module_route(app, 'maquinaria')
    assert case['description'] == 'registro de la vista de gestión de maquinaria'
