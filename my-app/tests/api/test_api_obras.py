from controllers import controller_obra


def test_api_obras_lista_estados_json_y_exige_sesion(client, api_client, monkeypatch):
    assert client.get('/api/obra/estados').status_code == 401
    estados = [{'id_estado': 1, 'nombre': 'En ejecución'}]

    class FakeObraModel:
        def listar_estados(self):
            return estados

    monkeypatch.setattr(controller_obra, 'ObraModel', FakeObraModel)
    respuesta = api_client.get('/api/obra/estados')

    assert respuesta.status_code == 200
    assert respuesta.get_json() == estados
