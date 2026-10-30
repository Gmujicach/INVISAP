from controllers import controller_respaldo


def test_api_respaldos_requiere_sesion_y_lista_registros(client, api_client, monkeypatch):
    assert client.get('/respaldo/api/listar-json').status_code == 401
    monkeypatch.setattr(controller_respaldo.modelo_respaldo, 'listar_respaldos', lambda: [])

    respuesta = api_client.get('/respaldo/api/listar-json')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {'status': 'success', 'respaldos': []}
