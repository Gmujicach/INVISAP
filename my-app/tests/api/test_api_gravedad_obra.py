from routers import router_home


def test_api_gravedad_lista_registros_json_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/api/gravedad/listar').status_code == 401

    gravedades = [{'id_gravedad': 2, 'nombre': 'Alta'}]
    monkeypatch.setattr(router_home, 'listar_gravedades_controller', lambda: gravedades)

    respuesta = api_client.get('/api/gravedad/listar')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == gravedades
