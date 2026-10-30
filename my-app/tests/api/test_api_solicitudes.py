from routers import router_home


def test_api_solicitudes_responde_json_y_exige_sesion(client, api_client, monkeypatch):
    sin_sesion = client.get('/api/obtener-solicitudes-json')
    assert sin_sesion.status_code == 401
    assert sin_sesion.get_json() == []

    datos = [{'id_solicitudes': 7, 'problematica': 'Falla de alumbrado'}]
    monkeypatch.setattr(router_home, 'obtener_solicitudes', lambda: datos)

    respuesta = api_client.get('/api/obtener-solicitudes-json')

    assert respuesta.status_code == 200
    assert respuesta.is_json
    assert respuesta.get_json() == datos
