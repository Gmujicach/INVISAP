from controllers import controller_empresa


def test_api_empresa_consulta_por_rif_y_controla_respuestas(client, api_client, monkeypatch):
    assert client.get('/api/empresas/J-123').status_code == 401

    monkeypatch.setattr(
        controller_empresa,
        'obtener_empresa_por_rif',
        lambda rif: {'rif': rif, 'nombre': 'Constructora'},
    )
    respuesta = api_client.get('/api/empresas/J-123')
    assert respuesta.status_code == 200
    assert respuesta.get_json() == {
        'exito': True,
        'empresa': {'rif': 'J-123', 'nombre': 'Constructora'},
    }

    monkeypatch.setattr(controller_empresa, 'obtener_empresa_por_rif', lambda rif: None)
    no_encontrada = api_client.get('/api/empresas/J-999')
    assert no_encontrada.status_code == 404
    assert no_encontrada.get_json()['exito'] is False
