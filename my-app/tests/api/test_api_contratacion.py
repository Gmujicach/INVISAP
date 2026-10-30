from routers import router_home


def test_api_contratacion_lista_empresas_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/api/obtener-empresas-json').status_code == 401
    empresas = [{'rif_empresa': 'J-123', 'nombre_empresa': 'Constructora'}]
    monkeypatch.setattr(
        router_home.ContratacionModel,
        'obtener_empresas',
        lambda self: empresas,
    )

    respuesta = api_client.get('/api/obtener-empresas-json')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == empresas
