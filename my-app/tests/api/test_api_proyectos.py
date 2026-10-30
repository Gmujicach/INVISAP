from routers import router_home


def test_api_proyectos_valida_codigo_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/api/proyecto/validar-codigo/OB-2024').status_code == 401

    codigos_consultados = []

    def validar_codigo(self, codigo):
        codigos_consultados.append(codigo)
        return {'existe': True}

    monkeypatch.setattr(
        router_home.ProyectoModel,
        'validar_codigo_proyecto',
        validar_codigo,
    )
    respuesta = api_client.get('/api/proyecto/validar-codigo/OB-2024')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == {'existe': True}
    assert codigos_consultados == ['OB-2024']
