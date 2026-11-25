from tests.integration.route_contracts import verify_module_route


def test_integracion_consulta_usuario_por_id(app):
    # INICIO DE MOCK: Llamar verify_module_route (función de contrato de ruta)
    case = verify_module_route(app, 'usuarios')
    # INICIO DE ASERCIÓN: Verificar descripción de la ruta
    assert case['description'] == 'generación de la ruta de consulta de usuario por ID'
    # FIN DE ASERCIÓN
