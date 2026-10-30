from tests.integration.route_contracts import verify_module_route


def test_integracion_consulta_usuario_por_id(app):
    case = verify_module_route(app, 'usuarios')
    assert case['description'] == 'generación de la ruta de consulta de usuario por ID'
